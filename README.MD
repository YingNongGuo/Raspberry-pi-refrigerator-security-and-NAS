# 冰箱監視器與SAMBA

# 目的
1.監測冰箱有無被使用  
2.偵測到有動作時才錄影,減少錄製影片容量  
3.寄Email提醒使用者冰箱遭到入侵  
4.使用SAMBA分享錄影影片  

## 設備簡介
1.Raspberry Pi 4  
2.作業系統：Raspberry Pi OS with desktop  
3.7吋觸控顯示器  
4.Raspberry Pi Camera Module(CSI傳輸)  
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/%E8%A8%AD%E5%82%991.jpg)  

## 安裝作業系統
請到官網下載[Raspberry Pi OS with desktop and recommended software](https://www.raspberrypi.org/software/operating-systems/)

再使用[Etcher](https://www.balena.io/etcher/)燒錄SD卡(建議先將SD卡格式化後再燒錄)

## 旋轉螢幕與更新軟體和軟體版本
### 安裝文字編輯器
```
sudo apt install vim
```
### 若螢幕顛倒,可調整螢幕設定
```
sudo vim /boot/config.txt
```
依照需求在最底下加上程式碼
```
lcd_rotate = 0 //不旋轉
lcd_rotate = 1 //旋轉90度
lcd_rotate = 2 //旋轉180度
lcd_rotate = 3 //旋轉270度
```
若是HDMI螢幕請使用display_rotate指令,重開機之後才會套用設定
```
reboot
```
### 更新軟體和軟體版本
```
sudo apt-get update
sudo apt-get upgrade
```

## 系統流程圖
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/%E7%B3%BB%E7%B5%B1%E6%B5%81%E7%A8%8B%E5%9C%96.png)  

## 寄送email測試

### 將 Google email 帳戶-->安全性-->低安全性應用程式存取權 開啟
```
import smtplib

def sendemail():
    from_addr='寄email的帳號'
    to_addr_list='收email的帳號'
    message='Hello'#要傳送的訊息
    password='寄email的密碼'
    smtpserver='smtp.gmail.com:587'
    header  = 'From: %s' % from_addr
    header += 'To: %s' % ','.join(to_addr_list)
    message = header + message
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login('寄email的帳號',password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

sendemail()#呼叫函式
```

## 動作偵測

### 開啟pi camera
```
sudo raspi-config
```
Interface Options-->camera-->enable ,並重新開機啟用設定

### 安裝模組
```
sudo pip3 install imutils
sudo pip3 install opencv-python
sudo apt-get install libatlas-base-dev
sudo apt-get install gpac
```

### 動作偵測流程圖
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/%E5%8B%95%E4%BD%9C%E5%81%B5%E6%B8%AC%E6%B5%81%E7%A8%8B%E5%9C%96.png)  
```
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
from time import sleep
from email.mime.text import MIMEText
from email.header import Header
import argparse
import imutils
import time
import cv2
import numpy as np
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from picamera import PiCamera
from time import sleep
from subprocess import call 

def convert(file_h264, file_mp4):
    print("Rasp_Pi => Video Recorded! \r\n")
    # Convert the h264 format to the mp4 format.
    command = "MP4Box -add " + file_h264 + " " + file_mp4
    call([command], shell=True)
    print("\r\nRasp_Pi => Video Converted! \r\n")

def motiondetection(avg,avg_float):
    blur = cv2.blur(vs.read(), (4, 4))
    diff = cv2.absdiff(avg, blur)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    cnts,hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result='NO'
    img=0
    for c in cnts:
        if cv2.contourArea(c) < 2500:
            continue
        result='Yes'
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(vs.read(), (x, y), (x + w, y + h), (0, 255, 0), 2)
        
    cv2.drawContours(vs.read(), cnts, -1, (0, 255, 255), 2)
    cv2.imshow('frame', vs.read())
    if cv2.waitKey(10) & 0xFF == ord('q'):
        fps.update()
        return result,avg
    fps.update()
    cv2.accumulateWeighted(blur, avg_float, 0.01)
    avg = cv2.convertScaleAbs(avg_float)
    return result,avg

def sending():
    mes = time.strftime("Someone Here!!   %Y-%m-%d %H:%M:%S", time.localtime()) 

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "Refrigerator Monitor"  #郵件標題
    content["from"] = "寄件者"  #寄件者
    content["to"] = "收件者" #收件者
    content.attach(MIMEText(mes))  # 郵件純文字內容
    content.attach(MIMEImage(Path('img.jpg').read_bytes()))  # 郵件圖片內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("寄件者",'密碼')  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
        
def warmup(avg,avg_float):
    area = 320 * 240 
    avg = cv2.blur(vs.read(), (4, 4))
    avg_float = np.float32(avg)
    tstart=time.time()
    while((time.time()-tstart)<10):
        print("warming up")
        print(time.time()-tstart)
        result,avg=motiondetection(avg,avg_float)
    return result,avg,avg_float

class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,format="bgr", use_video_port=True)
        self.frame = None
        self.stopped = False
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True
        
    def record(self):
        self.camera.start_preview()
        self.camera.start_recording('/home/pi/pi_record/video.h264')
        sleep(5)
        self.camera.stop_recording()
        self.camera.stop_preview()
        
        
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

vs = PiVideoStream().start()
time.sleep(2.0)
fps = FPS().start()

frame = vs.read()
area = 320 * 240
avg = cv2.blur(frame, (4, 4))
avg_float = np.float32(avg)

result,avg,avg_float=warmup(avg,avg_float)
lastresult='NO'
test=0

while (1):
    lastresult=result
    result,avg=motiondetection(avg,avg_float)
    if result=='Yes' and lastresult=='Yes':
        test=test+1
    else:
        test=0
    if result=='Yes':
        print("detect motion")
        print(test)
    else:
        print("No motion")
  
    if test>15:
        frame=vs.read()
        cv2.imwrite('img.jpg',frame)
        sending()
        print("sendemail")
        vs.record()
        ttt = time.strftime("%Y%m%d%H%M%S", time.localtime())
        mp4 = '/home/pi/share/record'+ttt+'.mp4'
        convert('/home/pi/pi_record/video.h264', mp4)
        test=0
        result,avg,avg_float=warmup(avg,avg_float)
        
    else:
        result,avg=motiondetection(avg,avg_float)
fps.stop()
cv2.destroyAllWindows()
vs.stop()
```
## Nginx livestream
```
sudo apt install nginx
```
```
sudo apt install libnginx-mod-rtmp
```
```
sudo vim rtmp.conf
```
```
sudo systemctl start nginx
sudo systemctl status nginx
```
```
sudo apt-get install libomxil-bellagio-dev
wget -O ffmpeg.tar.bz2 https://ffmpeg.org/releases/ffmpeg-snapshot-git.tar.bz2
tar xvjf ffmpeg.tar.bz2
cd ffmpeg
sudo ./configure --arch=arm --target-os=linux --enable-gpl --enable-omx --enable-omx-rpi --enable-nonfree --extra-ldflags="-latomic"
```
## 修改nginx.conf
```
sudo vim /etc/nginx/nginx.conf
```
```
rtmp {
    server {
        listen 1935;
        chunk_size 4096;
        application vod {
            play /home/pi/share;
        }
    }
}
```
## 若nginx.conf消失或改爛,重新安裝一次即可
```
sudo apt-get remove --purge nginx nginx-full nginx-common
sudo apt-get install nginx
```
```
 -flvflags no_duration_filesize
```
## SAMBA
### 樹苺派NAS示意圖
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/SAMBA%E7%A4%BA%E6%84%8F%E5%9C%96.png)  
下載並設定conf檔
```
sudo apt-get install samba samba-common-bin
mkdir /home/pi/shared
sudo vim /etc/samba/smb.conf
```
編輯設定檔
```
[網路上的芳鄰的資料夾名稱]
path = /home/pi/share
writeable=Yes
create mask=0777
directory mask=0777
public=no
```
新增使用者
```
sudo smbpasswd -a pi
sudo systemctl restart smbd
```
查樹莓派ip
```
hostname -I
```
## DEMO
### 動作偵測
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/ezgif-7-f15707d33f8c.gif)
---
### 偵測到有人，寄送警告信件
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/ezgif-7-8407a8f061da.gif)
---
### 從手機端連線到NAS
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/ezgif-5-debd3e2dfac3_%E6%89%8B%E6%A9%9F%E9%80%A3%E7%B7%9A.gif)
---
### 從電腦端連線到NAS
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/ezgif-5-87c60080fa54_%E9%80%A3%E7%B7%9A%E7%B6%B2%E8%B7%AF%E7%A3%81%E7%A2%9F%E6%A9%9F.gif)
---
## 參考資料
http://www.pythonforbeginners.com/code-snippets-source-code/using-python-to-send-email  
https://blog.gtwang.org/programming/opencv-motion-detection-and-tracking-tutorial/  
https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/  
https://pimylifeup.com/raspberry-pi-samba/  
https://www.researchgate.net/figure/Image-convolution-with-an-input-image-of-size-7-7-and-a-filter-kernel-of-size-3-3_fig1_318849314  

## 作者 1091lsa第11組
郭穎穠、吳辰恩、葉浩堯、許恩瑞


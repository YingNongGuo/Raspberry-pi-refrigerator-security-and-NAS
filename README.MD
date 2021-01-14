# 冰箱監視器與SAMBA

## 目的
1. 監測冰箱有無被使用
2. 使用電路偵測冰箱有無被開啟
3. 偵測到冰箱開啟後如有動作時才錄影,減少錄製影片容量  
4. 寄Email提醒使用者冰箱遭到入侵  
5. 使用SAMBA/Nginx分享錄影影片  

## 設備簡介
1. Raspberry Pi 4  
2. 作業系統：Raspberry Pi OS with desktop  
3. 7吋觸控顯示器  
4. Raspberry Pi Camera Module(CSI傳輸)

![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/%E8%A8%AD%E5%82%991.jpg)  
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/%E8%A8%AD%E5%82%992.jpg)

## 預先準備
#### 安裝作業系統
請到官網下載[Raspberry Pi OS with desktop and recommended software](https://www.raspberrypi.org/software/operating-systems/)

再使用[Etcher](https://www.balena.io/etcher/)燒錄SD卡(建議先將SD卡格式化後再燒錄)

#### 安裝文字編輯器
可使用預設nano,依個人喜好決定是否安裝vim
```
sudo apt install vim
```
#### 若螢幕顛倒,可調整螢幕設定
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
#### 更新軟體和軟體版本
```
sudo apt-get update
sudo apt-get upgrade
```

## 系統流程圖
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/%E7%B3%BB%E7%B5%B1%E6%B5%81%E7%A8%8B%E5%9C%96.png)  

## 架設Nginx server 
安裝Nginx
```
sudo apt install nginx
```
開啟並檢查一下Nginx狀態 
```
sudo service nginx start
sudo service nginx status
```
新增domain name 
```
sudo vim /etc/hosts
```
```
127.0.0.1	localhost
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters
127.0.1.1		raspberrypi
127.0.0.1	LSAteam11.com #新增domain name 
```
#### 編輯設定檔 
```
sudo vim /etc/nginx/sites-available/LSAteam11
```
```
server {
	listen 8080;#聽8080port
	server_name LSAteam11.com;
	root /var/www/LSAteam11/;#index與等一下錄影影片要存放的位置(mp4可直接用瀏覽器播放,h264需另外安裝編碼器)
	index index.html;
	location / {
	  try_files $uri =404;#若找不到檔案會顯示404
	}
}
```
從sites-available softlink到 sites-enabled
```
sudo ln -s /etc/nginx/sites-available/LSAteam11 /etc/nginx/sites-enabled/
```
在/var/www/新增資料夾LSAteam11(等一下錄影影片要存放的位置,也可以放圖片,gif等)
```
sudo mkdir /var/www/LSAteam11
```
```
sudo cp /var/www/html/index.nginx-debian.html /var/www/LSAteam11/
```
重啟nginx(才會重新套用剛才的設定檔)
```
sudo service nginx restart
```
#### 開啟無痕模式在網址列輸入檢查是否成功 
video.mp4為/var/www/LSAteam11目錄下的檔案  
10.106.24.219為樹莓派(在終端機輸入hostname -I可查看) 
```
http://10.106.24.219:8080/video.mp4
```
#### 若不小心刪除nginx設定檔(或改爛了),重新安裝一次即可
```
sudo apt-get remove --purge nginx nginx-full nginx-common
sudo apt-get install nginx
```

## SAMBA
下載並設定conf檔
```
sudo apt-get install samba samba-common-bin
```
新增分享檔案目錄(等一下將錄影影片存在這裡)
```
mkdir /home/pi/share
```
編輯設定檔
```
sudo vim /etc/samba/smb.conf
```
```
[share]#網路上的芳鄰的資料夾名稱
path = /home/pi/share
writeable=Yes
create mask=0777
directory mask=0777
public=no
```
新增使用者
注意這裡的使用者必須是樹莓派上已經有的user(預設user是pi)
```
sudo smbpasswd -a pi
sudo systemctl restart smbd
```
若想新增樹莓派user輸入
```
sudo adduser
```
重啟SAMBA讀取設定
```
sudo systemctl restart smbd
```
查樹莓派ip
```
hostname -I
```
如果關機後須重新啟用SAMBA服務,請執行
```
sudo service smbd start
```
並確定樹莓派ip是否有改變,網路上的芳鄰讀取位置會不同  
在WIN10的檔案總管-->本機-->電腦(左上角,檔案旁邊)-->連線網路磁碟機-->在資料夾 輸入\\10.106.24.219\share-->輸入帳號密碼  

## 硬體與軟體設計
### 冰箱門電路設計
冰箱的內側兩條分開的電線(麵包版專用單芯線)
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/%E5%86%B0%E7%AE%B1%E9%96%80%E9%9B%BB%E8%B7%AF1.jpg) 

冰箱門上的電線(麵包版專用單芯線)
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/%E5%86%B0%E7%AE%B1%E9%96%80%E9%9B%BB%E8%B7%AF2.jpg)

兩條電線分別連上GPIO22(pin15)與GROUND(pin9)
在中間加上一個10K電阻可以保護電路(但因為臨時找不到我們這邊沒有裝上10K電阻)
![image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/Raspberry-GPIO.jpg)

### 冰箱門檢測程式
當冰箱門打開時會回傳1,當冰箱門關起時會回傳0  
將PIN22設為上拉電阻(pull up),注意並不是每一PIN腳都適合這麼做,請查閱 樹莓派 4 datasheet!  
上拉電阻(pull up)意思是連接一個內建的電阻至3.3V,若是下拉電阻(pull down)則表示連接一個內建的電阻至接地  
當冰箱門打開時電路為通路PIN22便可以讀到訊號 
``` 
import RPi.GPIO as GPIO
def door_test():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22,GPIO.IN,GPIO.PUD_UP)#將PIN22設為pull up
    if GPIO.input(22):
        print("door is open")
        return 1
    else:
        print("door is closed")
        return 0
```

### python的module與library準備
安裝python使用的模組
```
sudo pip3 install imutils
sudo pip3 install opencv-python
sudo apt-get install libatlas-base-dev
sudo apt-get install gpac
```
python import的library
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
import socket
import RPi.GPIO as GPIO
from shutil import copyfile
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from picamera import PiCamera
from time import sleep
from subprocess import call 
```

### 寄送email測試
#### 將 Google email 帳戶-->安全性-->低安全性應用程式存取權 開啟  
[!image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/google%E5%B8%B3%E6%88%B6%E8%A8%AD%E5%AE%9A.png)

```
def sending():
    #mes是要寄送的內容
    mes = time.strftime("Someone Here!!   %Y-%m-%d %H:%M:%S", time.localtime())
    #讀取樹莓派的IP_address
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    #錄影會存在/var/www/LSAteam11/,將架設的Nginx網站寄送給使用者
    mes=mes+'\n record:\n http://'+s.getsockname()[0]+':8080/'+ttt+'.mp4'
    s.close
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "Refrigerator Monitor"  #郵件標題
    content["from"] = "寄件者Gmail"  #寄件者(寄件者可和收件者相同,可以自己寄給自己喔!)
    content["to"] = "收件者Gmail" #收件者
    content.attach(MIMEText(mes))  # 郵件純文字內容
    content.attach(MIMEImage(Path('img.jpg').read_bytes()))  # 郵件圖片內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("寄件者gmail",'密碼')  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
```

### 異物偵測
#### 開啟pi camera
```
sudo raspi-config
```
Interface Options-->camera-->enable ,並重新開機啟用設定

#### 異物偵測流程圖
[!image](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/README/Pictures/%E7%95%B0%E7%89%A9%E5%81%B5%E6%B8%AC%E6%B5%81%E7%A8%8B%E5%9C%96.png)  

#### PiVideoStream
建立PiVideoStream類別(class)
```
class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,format="bgr", use_video_port=True)
        self.frame = None
        self.stopped = False
    def start(self):#開始影像串流(stream)
        Thread(target=self.update, args=()).start()
        return self
    def update(self):#更新視窗影像
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
    def read(self):#讀取一幀(frame)
        return self.frame
    def stop(self):#結束影像串流(stream)
        self.stopped = True
        
    def record(self):#錄下影像串流(stream)
        self.camera.start_preview()
        self.camera.start_recording('/home/pi/pi_record/video.h264')
        sleep(5)
        self.camera.stop_recording()
        self.camera.stop_preview()
```

#### 異物偵測函式
```
def motiondetection(avg,avg_float):
    blur = cv2.blur(vs.read(), (4, 4))#平滑化
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
```

#### h264轉成mp4檔函式
Pi camera預設為h264,將其轉為mp4方便觀看
```
def convert(file_h264, file_mp4):
    print("Rasp_Pi => Video Recorded! \r\n")
    # Convert the h264 format to the mp4 format.
    command = "MP4Box -add " + file_h264 + " " + file_mp4
    call([command], shell=True)
    print("\r\nRasp_Pi => Video Converted! \r\n")
```

#### 暖機程式
暖機10秒之後接下來異物偵測都會和這些圖的平均做比較
```
def warmup(avg,avg_float):
    area = 320 * 240 
    avg = cv2.blur(vs.read(), (4, 4))
    avg_float = np.float32(avg)
    tstart=time.time()
    while((time.time()-tstart)<10):#暖機10秒
        print("warming up")
        print(time.time()-tstart)
        result,avg=motiondetection(avg,avg_float)
    return result,avg,avg_float
```

#### 完整程式碼
各個函式檢測皆成功就可以執行完整程式碼囉!  
[final_project.py](https://github.com/YingNongGuo/Raspberry-pi-refrigerator-security-and-NAS/blob/main/final_project.py)

## DEMO
### 異物偵測
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
[python寄信範例](http://www.pythonforbeginners.com/code-snippets-source-code/using-python-to-send-email)  
[python異物偵測](https://blog.gtwang.org/programming/opencv-motion-detection-and-tracking-tutorial/)  
[pi camera硬體加速](https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/)  
[pi SAMA教學](https://pimylifeup.com/raspberry-pi-samba/)  
[影像處理教學](https://www.researchgate.net/figure/Image-convolution-with-an-input-image-of-size-7-7-and-a-filter-kernel-of-size-3-3_fig1_318849314)
[電路開關教學](https://www.raspberrypi.org/forums/viewtopic.php?t=58267)

## 作者 1091lsa第11組
郭穎穠、吳辰恩、葉浩堯、許恩瑞


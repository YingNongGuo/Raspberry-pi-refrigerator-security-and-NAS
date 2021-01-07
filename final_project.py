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
            smtp.login("寄件者",'寄件者密碼')  # 登入寄件者gmail
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

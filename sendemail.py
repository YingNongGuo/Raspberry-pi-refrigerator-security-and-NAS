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

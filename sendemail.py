import smtplib

def sendemail():
    from_addr='寄email的帳號'
    to_addr_list='收email的帳號'
    message='Hello'
    password='寄email的密碼'
    smtpserver='smtp.gmail.com:587'
    header  = 'From: %s' % from_addr
    header += 'To: %s' % ','.join(to_addr_list)
    message = header + message
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login('linuxlsateam11',password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

sendemail()
# @Time : 2024/11/26 0:14
# @Author : YaHoo94
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from config import get_config

def init_smtp():
    global smtp_obj
    config = get_config()
    email_address = config.get('email_address')
    email_smtp_secret = config.get('email_smtp_secret')
    smtp_server = config.get('smtp_server')
    smtp_port = config.get('smtp_port')

    smtp_obj = smtplib.SMTP_SSL(smtp_server, smtp_port)
    smtp_obj.login(email_address, email_smtp_secret)

def send_email(title:str,content: str):
    config = get_config()
    email_receiver = config.get('email_receiver')
    email_address = config.get('email_address')

    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header(f'eyes on you! <{email_address}>')  # 发送者
    message['To'] = Header(','.join(email_receiver), 'utf-8')  # 接收者
    message['Subject'] = Header(title, 'utf-8')
    # 三个参数分别是：发件人邮箱账号，收件人邮箱账号，发送的邮件体
    smtp_obj.sendmail(email_address, email_receiver, message.as_string())

def close_smtp():
    smtp_obj.quit()

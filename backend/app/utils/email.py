import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email, subject, body):
    """
    發送電子郵件
    
    參數:
        to_email (str): 接收者郵箱
        subject (str): 郵件主題
        body (str): 郵件內容 (HTML 格式)
    """
    from_email = os.environ.get('MAIL_USERNAME', 'ncuHousingPortal@gmail.com')
    password = os.environ.get('MAIL_PASSWORD', 'your-app-password')
    
    # 創建多部分郵件
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    
    # 添加 HTML 內容
    message.attach(MIMEText(body, 'html'))
    
    try:
        # 連接到 SMTP 服務器
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # 安全連接
        server.login(from_email, password)
        
        # 發送郵件
        server.send_message(message)
        server.quit()
        
        print(f"成功發送郵件到 {to_email}")
        return True
    except Exception as e:
        print(f"發送郵件失敗: {str(e)}")
        raise e
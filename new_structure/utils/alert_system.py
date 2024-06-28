import smtplib
from email.mime.text import MIMEText
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from utils.logger import setup_logger

logger = setup_logger()

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = "Bitcoin Trading Alert"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
           smtp_server.login(EMAIL_SENDER, EMAIL_PASSWORD)
           smtp_server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        
        logger.info(f"Alert sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

    print(f"Alert: {message}")
from flask_mail import Message
from app import mail
from flask import current_app

def send_email(to, subject, body):
    msg = Message(subject=subject, recipients=[to], body=body)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Mail Gönderilemedi: {e}")
        return False
    
    
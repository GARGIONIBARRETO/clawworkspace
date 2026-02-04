#!/usr/bin/env python3
"""
Email sender for Max - sends emails via Gmail SMTP.
"""
import smtplib
import json
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

CREDS_PATH = "/root/.secrets/email_credentials.json"

def load_credentials():
    with open(CREDS_PATH) as f:
        return json.load(f)

def send_email(to, subject, body, attachments=None, html=False, reply_to=None):
    """
    Send an email.
    
    Args:
        to: recipient email (string or list)
        subject: email subject
        body: email body (plain text or HTML)
        attachments: list of file paths to attach
        html: if True, body is HTML
        reply_to: message-id to reply to
    """
    creds = load_credentials()
    
    msg = MIMEMultipart()
    msg['From'] = creds['email']
    msg['To'] = to if isinstance(to, str) else ', '.join(to)
    msg['Subject'] = subject
    
    if reply_to:
        msg['In-Reply-To'] = reply_to
        msg['References'] = reply_to
    
    # Add body
    if html:
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Add attachments
    if attachments:
        for filepath in attachments:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)
    
    # Send
    with smtplib.SMTP_SSL(creds['smtp_server'], 465) as server:
        server.login(creds['email'], creds['app_password'])
        server.send_message(msg)
    
    return {"success": True, "to": to, "subject": subject}

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: email_sender.py <to> <subject> <body> [attachment1] [attachment2] ...")
        print("Example: email_sender.py user@email.com 'Test Subject' 'Hello World' /path/to/file.pdf")
        sys.exit(1)
    
    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    attachments = sys.argv[4:] if len(sys.argv) > 4 else None
    
    result = send_email(to, subject, body, attachments)
    print(json.dumps(result, indent=2))

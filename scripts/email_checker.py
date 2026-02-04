#!/usr/bin/env python3
"""
Email checker for Max - monitors Gmail inbox and returns unread emails.
"""
import imaplib
import email
from email.header import decode_header
import json
import os
import sys
from datetime import datetime

CREDS_PATH = "/root/.secrets/email_credentials.json"

def load_credentials():
    with open(CREDS_PATH) as f:
        return json.load(f)

def decode_str(s):
    """Decode email header string."""
    if s is None:
        return ""
    decoded = decode_header(s)
    result = []
    for part, encoding in decoded:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or 'utf-8', errors='replace'))
        else:
            result.append(part)
    return ' '.join(result)

def get_email_body(msg):
    """Extract email body."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        except:
            body = str(msg.get_payload())
    return body[:2000]  # Limit body length

def check_emails(mark_seen=False, limit=10):
    """Check for unread emails."""
    creds = load_credentials()
    
    mail = imaplib.IMAP4_SSL(creds['imap_server'])
    mail.login(creds['email'], creds['app_password'])
    mail.select('INBOX')
    
    # Search for unread emails
    status, messages = mail.search(None, 'UNSEEN')
    
    if status != 'OK':
        return {"error": "Failed to search emails"}
    
    email_ids = messages[0].split()
    emails = []
    
    for email_id in email_ids[-limit:]:  # Get last N unread
        status, msg_data = mail.fetch(email_id, '(RFC822)' if mark_seen else '(BODY.PEEK[])')
        
        if status != 'OK':
            continue
            
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Extract attachments info
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        "filename": decode_str(filename),
                        "content_type": part.get_content_type(),
                        "size": len(part.get_payload(decode=True) or b'')
                    })
        
        emails.append({
            "id": email_id.decode(),
            "from": decode_str(msg.get('From')),
            "to": decode_str(msg.get('To')),
            "subject": decode_str(msg.get('Subject')),
            "date": msg.get('Date'),
            "body": get_email_body(msg),
            "attachments": attachments
        })
    
    mail.logout()
    
    return {
        "unread_count": len(email_ids),
        "emails": emails,
        "checked_at": datetime.now().isoformat()
    }

def get_email_by_id(email_id, save_attachments_to=None):
    """Get a specific email by ID with full content and optionally save attachments."""
    creds = load_credentials()
    
    mail = imaplib.IMAP4_SSL(creds['imap_server'])
    mail.login(creds['email'], creds['app_password'])
    mail.select('INBOX')
    
    status, msg_data = mail.fetch(email_id.encode(), '(RFC822)')
    
    if status != 'OK':
        return {"error": f"Failed to fetch email {email_id}"}
    
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                filename = decode_str(filename)
                content = part.get_payload(decode=True)
                att_info = {
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "size": len(content or b'')
                }
                
                if save_attachments_to and content:
                    os.makedirs(save_attachments_to, exist_ok=True)
                    filepath = os.path.join(save_attachments_to, filename)
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    att_info["saved_to"] = filepath
                
                attachments.append(att_info)
    
    mail.logout()
    
    return {
        "id": email_id,
        "from": decode_str(msg.get('From')),
        "to": decode_str(msg.get('To')),
        "subject": decode_str(msg.get('Subject')),
        "date": msg.get('Date'),
        "body": get_email_body(msg),
        "attachments": attachments
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            result = check_emails(limit=int(sys.argv[2]) if len(sys.argv) > 2 else 10)
        elif sys.argv[1] == "get":
            email_id = sys.argv[2]
            save_to = sys.argv[3] if len(sys.argv) > 3 else None
            result = get_email_by_id(email_id, save_to)
        else:
            result = {"error": "Unknown command. Use: check [limit] | get <id> [save_path]"}
    else:
        result = check_emails()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

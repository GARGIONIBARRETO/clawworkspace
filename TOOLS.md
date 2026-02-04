# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

---

## 📧 Email

**Conta:** clinicadacolunadrfelipebarreto@gmail.com
**Credenciais:** `/root/.secrets/email_credentials.json`

### Scripts disponíveis:

**Checar emails:**
```bash
python3 /root/clawd/scripts/email_checker.py check [limit]
python3 /root/clawd/scripts/email_checker.py get <email_id> [save_attachments_path]
```

**Enviar email:**
```bash
python3 /root/clawd/scripts/email_sender.py <to> <subject> <body> [attachments...]
```

### Uso via Python:
```python
from scripts.email_checker import check_emails, get_email_by_id
from scripts.email_sender import send_email

# Checar não lidos
result = check_emails(limit=10)

# Buscar email específico e salvar anexos
email = get_email_by_id("123", save_attachments_to="/tmp/attachments")

# Enviar email
send_email("dest@email.com", "Assunto", "Corpo do email", attachments=["/path/file.pdf"])
```

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

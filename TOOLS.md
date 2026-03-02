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

## 🏥 Sistema de Gestão de Pacientes

**Base de dados:** Supabase PostgreSQL
**Credenciais:** `/root/.secrets/supabase_credentials.json`

### Scripts disponíveis:

**Sistema principal:**
```bash
python3 /root/clawd/scripts/clinica_manager.py
# Interface completa com menus interativos
```

**Gestão de dados:**
```bash
# Conectar e criar tabelas
python3 /root/clawd/scripts/db_manager.py

# Gerenciar pacientes, exames e bioimpedância
python3 /root/clawd/scripts/pacientes_manager.py

# Gerar relatórios e gráficos
python3 /root/clawd/scripts/relatorios_clinicos.py

# Importar dados de CSV
python3 /root/clawd/scripts/import_dados.py
```

### Estrutura do banco:

**Tabelas principais:**
- `pacientes` - dados pessoais e contato
- `consultas` - histórico de consultas
- `exames_laboratoriais` - exames com parâmetros em JSON
- `bioimpedancia` - medições de composição corporal

### Funcionalidades:

- ✅ **Busca rápida** por nome/CPF
- ✅ **Exames comparativos** - evolução temporal
- ✅ **Gráficos de bioimpedância** - peso, IMC, gordura, músculo
- ✅ **Dashboards HTML** - relatórios visuais
- ✅ **Importação CSV** - templates para entrada em massa
- ✅ **Backup automático** (quando conexão ativa)

### Templates CSV:
- `/root/clawd/templates/pacientes_template.csv`
- `/root/clawd/templates/bioimpedancia_template.csv`
- `/root/clawd/templates/exames_template.csv`

### Relatórios:
- `/root/clawd/relatorios/` - gráficos PNG e dashboards HTML

**🚨 Status atual:** Sistema pronto, aguardando conectividade com Supabase para ativação completa.

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

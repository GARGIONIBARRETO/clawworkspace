# MEMORY.md

## Sistema de Gestão de Pacientes

### 02/03/2026 - Migração Completa para PostgreSQL Local
- **Problema:** Sistema tentava conectar no Supabase que estava inacessível
- **Solução:** Migrado 100% para PostgreSQL local
- **Scripts atualizados:** db_manager.py, pacientes_manager.py
- **Backup:** Configurado backup diário local
- **Status:** Sistema 100% operacional com 654 pacientes e 1480 consultas

### 02/03/2026 - Interface Web Completa
- **Interface disponível:** http://129.121.33.120:5000
- **Funcionalidades implementadas:**
  - Busca de pacientes (nome/CPF/telefone)
  - Cadastro de novo paciente
  - Edição de dados do paciente
  - Upload e download de exames/documentos
  - Agenda de consultas (hoje/futuras)
  - **Prontuário Eletrônico Completo** com anamnese, exame físico, diagnóstico e conduta
  - Auto-save de rascunhos
- **Tabelas criadas:** episodios_clinicos para prontuários detalhados
- **HTTPS ativado:** Porta 5443 com certificado SSL - Memória de Longo Prazo

## Sistema de Anamnese da Clínica

### Componentes
1. **Bot Telegram** (`anamnese-bot.service`) - Coleta anamnese via chat
2. **WebApp** (`https://felipebarretoneuro.com.br/webapp-anamnese/`) - Formulário web
3. **Backend API** (`https://api.felipebarretoneuro.com.br/api`) - Salva PDF + envia email

### Credenciais
- Token bot anamnese: `/root/.secrets/telegram_anamnese_token`
- Email Gmail: `/root/.secrets/email_credentials.json`

### Localização dos PDFs
- Servidor: `/root/clawd/clinica/anamneses/`

---

## Configurações Importantes

### Heartbeats
- Desabilitados para economizar créditos
- Modelo configurado: `openai/gpt-4o-mini` (quando reativar)

### Email Clínica
- Email: `clinicadacolunadrfelipebarreto@gmail.com`
- Scripts: `/root/clawd/scripts/email_checker.py`, `email_sender.py`

---

## Hospedagem

### VPS Clawdbot (este servidor)
- IP: `129.121.33.120`
- Onde roda: Clawdbot, backend anamnese, bot telegram

### Site Principal (Armata Cloud)
- Domínio: `felipebarretoneuro.com.br`
- IP: `177.73.233.25`
- Painel: https://armata.cloud (credenciais em `/root/.secrets/armata_cloud.json`)

### Google Cloud (server.felipebarretoneuro.com.br)
- IP: `35.198.55.149`
- SSH: `/root/.secrets/server_felipebarreto_ssh.json`
- Nota: SSH estava inacessível em 2026-02-18

---

## Referências Médicas

- Manual TUSS Coluna: `referencias/Manual_Codificacao_Coluna_SBC_SBOT_SBN.txt`
- Códigos validados: `referencias/codigos_tuss.md`

---

## Regra de Ouro ⚠️
**NUNCA inventar informação médica.** Se não souber, dizer que não sabe e ir atrás da fonte.

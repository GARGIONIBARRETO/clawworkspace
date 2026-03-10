# HEARTBEAT.md

## Tarefas Periódicas

### 🏥 Sistema de Pacientes - PostgreSQL Local
- ✅ **Sistema OPERACIONAL** - PostgreSQL local funcionando
- ✅ **Supabase DESABILITADO** - Migrado 100% para local (02/03/2026)
- **Backup automático** - Executar 1x ao dia
- Comando backup: `python3 /root/clawd/scripts/backup_local.py`
- Status: `python3 /root/clawd/scripts/verificar_importacao.py`

### 📱 Transcrição WhatsApp
- **Monitor automático** - Verificar 2x ao dia
- Comando monitor: `python3 /root/clawd/scripts/monitor_whatsapp_transcriber.py`
- Logs: `/tmp/wa-transcriber.log`
- **Status**: ✅ OPERACIONAL (reiniciado via systemctl 09/03/2026 06:22)

### ⏱️ Frequência do Heartbeat
- **2x ao dia** - manhã (~9h) e noite (~21h)
- Evitar checks excessivos durante o dia

### 🔄 Status Atual
- Sistema 100% local - PostgreSQL 13.23
- 655 pacientes cadastrados
- 1481 consultas registradas
- Último backup: 10/03/2026 00:02

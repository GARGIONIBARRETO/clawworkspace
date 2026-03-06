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
- **Status**: ✅ OPERACIONAL (reiniciado 05/03/2026 13:44)

### 🔄 Status Atual
- Sistema 100% local - PostgreSQL 13.23
- 654 pacientes cadastrados
- 1480 consultas registradas
- Último backup: 06/03/2026 01:14

#!/usr/bin/env python3
"""
Scheduler de Confirmações - Clínica Dr. Felipe Barreto
Envia confirmações de consulta 24h antes via WhatsApp
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'
TEMPLATE_FILE = BASE_DIR / 'templates/confirmacao_consulta.txt'
WHATSAPP_SEND = Path('/root/clawd/whatsapp-bridge/send.js')
LOG_FILE = BASE_DIR / 'confirmacoes_enviadas.jsonl'


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_template():
    with open(TEMPLATE_FILE) as f:
        return f.read()


def enviar_whatsapp(telefone: str, mensagem: str) -> bool:
    """Envia mensagem via WhatsApp"""
    try:
        # Formata telefone
        tel = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not tel.startswith('55'):
            tel = '55' + tel
        
        result = subprocess.run(
            ['node', str(WHATSAPP_SEND), tel, mensagem],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WHATSAPP_SEND.parent)
        )
        
        if result.returncode == 0:
            print(f"✅ WhatsApp enviado para {tel}")
            return True
        else:
            print(f"❌ Erro ao enviar WhatsApp: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção ao enviar WhatsApp: {e}")
        return False


def formatar_mensagem(template: str, paciente: dict, consulta: dict) -> str:
    """Formata a mensagem de confirmação"""
    data_hora = consulta.get('data', '')
    
    # Parse da data
    try:
        dt = datetime.fromisoformat(data_hora.replace('Z', '+00:00'))
        data_formatada = dt.strftime('%d/%m/%Y')
        horario_formatado = dt.strftime('%H:%M')
    except:
        data_formatada = data_hora[:10]
        horario_formatado = data_hora[11:16] if len(data_hora) > 11 else ''
    
    return template.format(
        nome=paciente.get('nome', consulta.get('titulo', 'Paciente')).split()[0],
        data=data_formatada,
        horario=horario_formatado,
        local=consulta.get('local', 'Consultório')
    )


def registrar_envio(consulta_id: str, telefone: str, sucesso: bool):
    """Registra envio de confirmação"""
    registro = {
        'timestamp': datetime.now().isoformat(),
        'consultaId': consulta_id,
        'telefone': telefone,
        'sucesso': sucesso
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(registro) + '\n')


def ja_enviado(consulta_id: str) -> bool:
    """Verifica se confirmação já foi enviada"""
    if not LOG_FILE.exists():
        return False
    
    with open(LOG_FILE) as f:
        for line in f:
            registro = json.loads(line)
            if registro.get('consultaId') == consulta_id and registro.get('sucesso'):
                return True
    return False


def processar_confirmacoes():
    """Processa e envia confirmações pendentes"""
    config = load_config()
    template = load_template()
    horas_antes = config['confirmacao']['horasAntes']
    
    print(f"\n🔍 Buscando consultas para confirmar ({horas_antes}h antes)...")
    
    # Importa módulos locais
    from calendar_integration import consultas_amanha, extrair_telefone_evento
    from prontuario import Prontuario
    
    consultas = consultas_amanha()
    
    if not consultas:
        print("📭 Nenhuma consulta para amanhã")
        return
    
    print(f"📅 {len(consultas)} consulta(s) encontrada(s) para amanhã\n")
    
    for consulta in consultas:
        consulta_id = consulta['id']
        
        if ja_enviado(consulta_id):
            print(f"⏭️ Já enviado: {consulta['titulo']}")
            continue
        
        # Tenta encontrar telefone
        telefone = extrair_telefone_evento(consulta)
        
        if not telefone:
            # Busca no prontuário pelo nome
            nome = consulta['titulo']
            pacientes = Prontuario.buscar_paciente(nome)
            if pacientes:
                telefone = pacientes[0].get('telefone')
        
        if not telefone:
            print(f"⚠️ Telefone não encontrado: {consulta['titulo']}")
            continue
        
        # Monta paciente dict para template
        paciente = {'nome': consulta['titulo']}
        
        # Formata e envia mensagem
        mensagem = formatar_mensagem(template, paciente, consulta)
        sucesso = enviar_whatsapp(telefone, mensagem)
        
        registrar_envio(consulta_id, telefone, sucesso)


def enviar_confirmacao_manual(telefone: str, nome: str, data: str, horario: str, local: str = "Consultório"):
    """Envia confirmação manualmente"""
    template = load_template()
    
    mensagem = template.format(
        nome=nome.split()[0],
        data=data,
        horario=horario,
        local=local
    )
    
    return enviar_whatsapp(telefone, mensagem)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python scheduler.py <comando>")
        print("\nComandos:")
        print("  run                    - Processa confirmações pendentes")
        print("  manual <tel> <nome> <data> <hora> [local]  - Envia confirmação manual")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        processar_confirmacoes()
    
    elif cmd == "manual" and len(sys.argv) >= 6:
        tel, nome, data, hora = sys.argv[2:6]
        local = sys.argv[6] if len(sys.argv) > 6 else "Consultório"
        enviar_confirmacao_manual(tel, nome, data, hora, local)
    
    else:
        print(f"Comando inválido: {cmd}")

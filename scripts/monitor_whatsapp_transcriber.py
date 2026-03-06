#!/usr/bin/env python3
"""
Monitor do Serviço de Transcrição WhatsApp
Verifica se o bot está rodando e funcionando corretamente
"""

import subprocess
import requests
import os
import signal
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_process():
    """Verifica se o processo está rodando"""
    try:
        result = subprocess.run(['pgrep', '-f', 'anamnese-bot.js'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def check_server():
    """Verifica se o servidor está respondendo"""
    try:
        response = requests.get('http://localhost:5060', timeout=5)
        return response.status_code == 200 and 'WA Anamnese Bot OK' in response.text
    except:
        return False

def start_service():
    """Inicia o serviço"""
    log("Iniciando serviço de transcrição...")
    os.chdir('/opt/wa-transcriber')
    subprocess.Popen(['nohup', 'node', 'anamnese-bot.js'], 
                     stdout=open('/tmp/wa-transcriber.log', 'a'),
                     stderr=subprocess.STDOUT)
    time.sleep(3)  # Aguarda 3 segundos para iniciar

def restart_service():
    """Reinicia o serviço"""
    log("Reiniciando serviço...")
    
    # Mata processos existentes
    try:
        result = subprocess.run(['pgrep', '-f', 'anamnese-bot.js'], 
                              capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid.strip():
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(1)
    except:
        pass
    
    # Inicia novamente
    start_service()

def main():
    log("Verificando status do serviço de transcrição WhatsApp")
    
    process_ok = check_process()
    server_ok = check_server()
    
    log(f"Processo rodando: {process_ok}")
    log(f"Servidor respondendo: {server_ok}")
    
    if not process_ok or not server_ok:
        log("❌ Serviço com problemas - reiniciando")
        restart_service()
        
        # Verifica novamente
        time.sleep(5)
        if check_process() and check_server():
            log("✅ Serviço reiniciado com sucesso")
        else:
            log("❌ Falha ao reiniciar o serviço")
    else:
        log("✅ Serviço funcionando normalmente")

if __name__ == '__main__':
    main()
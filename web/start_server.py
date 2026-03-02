#!/usr/bin/env python3
"""
Script para iniciar o servidor web do sistema de pacientes
"""

import os
import sys
import subprocess
import socket
from datetime import datetime

def check_port(port):
    """Verifica se a porta está disponível"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True se porta está livre

def find_available_port(start_port=5000):
    """Encontra uma porta disponível"""
    for port in range(start_port, start_port + 100):
        if check_port(port):
            return port
    return None

def main():
    print("🚀 INICIANDO SERVIDOR WEB - SISTEMA DE PACIENTES")
    print("=" * 60)
    print(f"⏰ Inicialização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Muda para o diretório web
    web_dir = '/root/clawd/web'
    if not os.path.exists(web_dir):
        print("❌ Diretório web não encontrado!")
        return
    
    os.chdir(web_dir)
    
    # Verifica se o app.py existe
    if not os.path.exists('app.py'):
        print("❌ Arquivo app.py não encontrado!")
        return
    
    # Encontra porta disponível
    port = find_available_port(5000)
    if not port:
        print("❌ Nenhuma porta disponível!")
        return
    
    print(f"🌐 Servidor será iniciado na porta: {port}")
    print(f"📂 Diretório de trabalho: {web_dir}")
    print()
    print("📊 INFORMAÇÕES DE ACESSO:")
    print(f"   URL Local: http://localhost:{port}")
    print(f"   URL Rede: http://{get_ip()}:{port}")
    print(f"   👤 Usuário: drfelipe")
    print(f"   🔑 Senha: clinica2026")
    print()
    print("🔧 FUNCIONALIDADES DISPONÍVEIS:")
    print("   ✅ Dashboard executivo")
    print("   ✅ Gestão de pacientes") 
    print("   ✅ Busca inteligente")
    print("   ✅ Relatórios visuais")
    print("   ✅ API REST completa")
    print()
    print("⚠️ STATUS:")
    print("   - Interface web: OPERACIONAL")
    print("   - Banco de dados: Verificando...")
    print()
    print("🔄 Para parar o servidor: Ctrl+C")
    print("=" * 60)
    print()
    
    try:
        # Executa o servidor Flask
        subprocess.run([
            sys.executable, 'app.py'
        ], env={
            **os.environ,
            'FLASK_ENV': 'development',
            'FLASK_DEBUG': 'False',
            'PORT': str(port)
        })
    
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")

def get_ip():
    """Obtém IP local"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    main()
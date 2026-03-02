#!/usr/bin/env python3
"""
Monitor de Conectividade Supabase
Testa conectividade a cada 30 minutos e avisa quando estiver disponível
"""

import sys
import time
import subprocess
from datetime import datetime

# Adiciona scripts ao path
sys.path.append('/root/clawd/scripts')

def testar_conectividade():
    """Testa conectividade executando o script de teste"""
    try:
        result = subprocess.run([
            'python3', '/root/clawd/scripts/teste_conectividade.py'
        ], capture_output=True, text=True, timeout=30)
        
        # Se chegou até aqui sem exceção, analisa a saída
        output = result.stdout
        
        # Se contém "SISTEMA PRONTO PARA USO", está conectado
        if "SISTEMA PRONTO PARA USO" in output:
            return True, output
        else:
            return False, output
            
    except Exception as e:
        return False, str(e)

def enviar_notificacao_telegram(mensagem):
    """Envia notificação via Telegram (placeholder)"""
    print(f"📱 NOTIFICAÇÃO: {mensagem}")
    # Aqui você pode implementar envio via Telegram API

def main():
    print("🔍 MONITOR DE CONECTIVIDADE SUPABASE")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🔄 Testando conectividade a cada 30 minutos...")
    print("🛑 Para parar: Ctrl+C")
    print()
    
    conectado_anteriormente = False
    tentativas = 0
    
    while True:
        try:
            tentativas += 1
            print(f"🔍 Teste #{tentativas} - {datetime.now().strftime('%H:%M:%S')}")
            
            conectado, output = testar_conectividade()
            
            if conectado and not conectado_anteriormente:
                # Sistema acabou de ficar disponível!
                mensagem = "🎉 SISTEMA DE PACIENTES DISPONÍVEL! Supabase conectado com sucesso."
                print(f"\n✅ {mensagem}")
                print("🌐 Acesse: http://localhost:5000")
                print("👤 Login: drfelipe | Senha: clinica2026")
                
                # Envia notificação
                enviar_notificacao_telegram(mensagem)
                
                conectado_anteriormente = True
                
            elif conectado:
                print("✅ Sistema operacional")
                
            else:
                if conectado_anteriormente:
                    print("⚠️ Sistema ficou indisponível")
                    conectado_anteriormente = False
                else:
                    print("❌ Sistema ainda indisponível")
            
            # Aguarda 30 minutos (1800 segundos)
            print(f"⏳ Próximo teste em 30 minutos...")
            time.sleep(1800)
            
        except KeyboardInterrupt:
            print("\n👋 Monitor encerrado pelo usuário")
            break
            
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
            time.sleep(60)  # Espera 1 minuto em caso de erro

if __name__ == "__main__":
    main()
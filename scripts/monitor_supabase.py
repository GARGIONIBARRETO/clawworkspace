#!/usr/bin/env python3
"""
Monitor simples de conectividade Supabase
Para uso via heartbeat ou execução manual
"""

import sys
import subprocess
import os

def main():
    """Testa conectividade e retorna status"""
    
    try:
        # Executa teste de conectividade
        result = subprocess.run([
            'python3', '/root/clawd/scripts/teste_conectividade.py'
        ], capture_output=True, text=True, timeout=30, cwd='/root/clawd')
        
        output = result.stdout
        
        # Se sistema está pronto
        if "SISTEMA PRONTO PARA USO" in output:
            print("🎉 SUPABASE CONECTADO! Sistema de pacientes operacional!")
            print()
            print("🚀 PARA USAR:")
            print("1. Interface Web: python3 /root/clawd/iniciar_sistema_completo.py")
            print("2. Menu Terminal: python3 /root/clawd/scripts/clinica_manager.py") 
            print()
            print("🌐 Acesso Web: http://localhost:5000")
            print("👤 Login: drfelipe | Senha: clinica2026")
            return True
            
        else:
            # Ainda sem conectividade
            return False
            
    except Exception as e:
        print(f"Erro ao testar conectividade: {e}")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)  # Sistema disponível
    else:
        sys.exit(1)  # Sistema ainda indisponível
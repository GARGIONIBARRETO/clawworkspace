#!/usr/bin/env python3
"""
SISTEMA COMPLETO DE GESTÃO DE PACIENTES - Dr. Felipe
Script de inicialização unificado
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_header():
    """Cabeçalho do sistema"""
    print("\n" + "=" * 70)
    print("🏥 SISTEMA COMPLETO DE GESTÃO DE PACIENTES - DR. FELIPE")
    print("=" * 70)
    print(f"⏰ Inicialização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()

def testar_conectividade():
    """Testa conectividade com Supabase"""
    print("🔍 TESTANDO CONECTIVIDADE COM SUPABASE...")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            'python3', '/root/clawd/scripts/teste_conectividade.py'
        ], capture_output=True, text=True, timeout=30)
        
        output = result.stdout
        print(output)
        
        # Verifica se conectou
        if "SISTEMA PRONTO PARA USO" in output:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def mostrar_opcoes_disponiveis():
    """Mostra opções disponíveis"""
    print("\n📋 OPÇÕES DISPONÍVEIS:")
    print("-" * 50)
    print("1. 🌐 Iniciar Interface Web (RECOMENDADO)")
    print("2. 💻 Sistema de Menu Interativo")
    print("3. 🔍 Monitor de Conectividade")
    print("4. 📊 Gerar Templates CSV")
    print("5. 📖 Ver Documentação")
    print("0. ❌ Sair")
    print()

def iniciar_interface_web():
    """Inicia interface web"""
    print("\n🌐 INICIANDO INTERFACE WEB...")
    print("-" * 40)
    print("📱 INFORMAÇÕES DE ACESSO:")
    print("   URL: http://localhost:5000")
    print("   Usuário: drfelipe")
    print("   Senha: clinica2026")
    print()
    print("⚠️ O navegador será aberto automaticamente!")
    print("🔄 Para parar: Ctrl+C")
    print()
    
    try:
        # Muda para diretório web
        os.chdir('/root/clawd/web')
        
        # Tenta abrir navegador (se disponível)
        try:
            subprocess.run(['xdg-open', 'http://localhost:5000'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        except:
            pass  # Navegador não disponível
        
        # Executa servidor
        subprocess.run(['python3', 'start_server.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Interface web encerrada")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar interface web: {e}")

def iniciar_sistema_menu():
    """Inicia sistema de menu interativo"""
    print("\n💻 INICIANDO SISTEMA DE MENU...")
    print("-" * 40)
    
    try:
        os.chdir('/root/clawd')
        subprocess.run(['python3', 'scripts/clinica_manager.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Sistema de menu encerrado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("💡 Verifique a conectividade com Supabase")

def iniciar_monitor():
    """Inicia monitor de conectividade"""
    print("\n🔍 INICIANDO MONITOR DE CONECTIVIDADE...")
    print("-" * 40)
    print("🔄 Testando a cada 30 minutos")
    print("📱 Você será avisado quando o sistema estiver disponível")
    print("🛑 Para parar: Ctrl+C")
    print()
    
    try:
        os.chdir('/root/clawd/web')
        subprocess.run(['python3', 'monitor_connectivity.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Monitor encerrado")
    except Exception as e:
        print(f"\n❌ Erro no monitor: {e}")

def gerar_templates():
    """Gera templates CSV"""
    print("\n📊 GERANDO TEMPLATES CSV...")
    print("-" * 40)
    
    try:
        os.chdir('/root/clawd')
        subprocess.run(['python3', 'scripts/gerar_templates.py'])
        
        print("\n✅ Templates gerados com sucesso!")
        print("📁 Localização: /root/clawd/templates/")
        print("📝 Edite os arquivos CSV e importe quando o sistema conectar")
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar templates: {e}")

def mostrar_documentacao():
    """Mostra documentação principal"""
    print("\n📖 DOCUMENTAÇÃO DO SISTEMA")
    print("-" * 40)
    print("📋 Arquivos principais:")
    print("   • SISTEMA_PACIENTES_README.md - Manual completo")
    print("   • EXEMPLO_PRATICO.md - Caso de uso detalhado")
    print("   • web/README.md - Interface web")
    print()
    print("📂 Estrutura:")
    print("   • /root/clawd/scripts/ - Sistema principal")
    print("   • /root/clawd/web/ - Interface web")
    print("   • /root/clawd/templates/ - Templates CSV")
    print("   • /root/clawd/relatorios/ - Relatórios gerados")
    print()
    print("🌐 Acesso Web: http://localhost:5000")
    print("👤 Login: drfelipe | Senha: clinica2026")

def main():
    """Função principal"""
    print_header()
    
    # Testa conectividade inicial
    conectado = testar_conectividade()
    
    if conectado:
        print("\n🎉 SISTEMA TOTALMENTE OPERACIONAL!")
        print("✅ Banco de dados conectado")
        print("✅ Interface web disponível")
        print("🚀 Pronto para uso completo!")
    else:
        print("\n⚠️ SISTEMA EM MODO PREPARAÇÃO")
        print("❌ Banco de dados temporariamente indisponível")
        print("✅ Interface web disponível (modo demonstração)")
        print("🔄 Conectividade será testada periodicamente")
    
    while True:
        mostrar_opcoes_disponiveis()
        
        try:
            opcao = input("Digite sua opção: ").strip()
            
            if opcao == "1":
                iniciar_interface_web()
            elif opcao == "2":
                if conectado:
                    iniciar_sistema_menu()
                else:
                    print("⚠️ Sistema de menu requer conectividade com banco")
                    print("💡 Use a Interface Web (opção 1) enquanto isso")
            elif opcao == "3":
                iniciar_monitor()
            elif opcao == "4":
                gerar_templates()
            elif opcao == "5":
                mostrar_documentacao()
            elif opcao == "0":
                print("\n👋 Até logo!")
                break
            else:
                print("❌ Opção inválida!")
                
            input("\n🔄 Pressione ENTER para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            input("🔄 Pressione ENTER para continuar...")

if __name__ == "__main__":
    main()
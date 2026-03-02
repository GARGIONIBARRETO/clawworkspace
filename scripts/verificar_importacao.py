#!/usr/bin/env python3
"""
Script para verificar status da importação e estrutura de dados
"""

import os
import sys
from pathlib import Path

sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

def verificar_arquivos_importacao():
    """Verifica arquivos prontos para importação"""
    base_path = Path('/root/clawd/importacao')
    
    print("📁 STATUS DOS ARQUIVOS PARA IMPORTAÇÃO")
    print("=" * 50)
    
    # Verificar cada pasta
    pastas = {
        'pacientes': 'Dados dos pacientes (CSV)',
        'consultas': 'Histórico de consultas (CSV)', 
        'episodios_clinicos': 'Episódios clínicos (CSV)',
        'anexos/exames_imagem': 'Exames de imagem (organizados por CPF)',
        'anexos/fotos_exames': 'Fotos de exames (organizados por CPF)'
    }
    
    for pasta, descricao in pastas.items():
        pasta_path = base_path / pasta
        
        if pasta_path.exists():
            if pasta.startswith('anexos/'):
                # Contar subpastas (CPFs)
                subpastas = [p for p in pasta_path.iterdir() if p.is_dir()]
                if subpastas:
                    total_arquivos = sum(len([f for f in sp.iterdir() if f.is_file()]) for sp in subpastas)
                    print(f"✅ {pasta}: {len(subpastas)} pacientes, {total_arquivos} arquivos")
                else:
                    print(f"⚠️  {pasta}: Pasta existe mas está vazia")
            else:
                # Contar arquivos CSV
                arquivos_csv = list(pasta_path.glob('*.csv'))
                if arquivos_csv:
                    print(f"✅ {pasta}: {len(arquivos_csv)} arquivo(s) CSV encontrado(s)")
                    for arquivo in arquivos_csv:
                        print(f"   📄 {arquivo.name}")
                else:
                    print(f"⚠️  {pasta}: Pasta existe mas sem arquivos CSV")
        else:
            print(f"❌ {pasta}: Pasta não encontrada")
    
    print()

def verificar_banco_dados():
    """Verifica dados já importados no banco"""
    try:
        db = PostgreSQLLocal()
        
        print("🗄️  STATUS DO BANCO DE DADOS")
        print("=" * 50)
        
        # Obter estatísticas do banco
        stats = db.get_stats()
        print(f"👥 Pacientes: {stats['pacientes']} registros")
        print(f"🩺 Consultas: {stats['consultas']} registros")
        print(f"🔬 Exames: {stats['exames_laboratoriais']} registros")
        print(f"⚖️ Bioimpedância: {stats['bioimpedancia']} registros")
        
        # Verificar anexos organizados
        anexos_path = Path('/root/clawd/anexos_pacientes')
        if anexos_path.exists():
            pastas_pacientes = [p for p in anexos_path.iterdir() if p.is_dir()]
            total_anexos = 0
            for pasta in pastas_pacientes:
                for subpasta in pasta.iterdir():
                    if subpasta.is_dir():
                        total_anexos += len([f for f in subpasta.iterdir() if f.is_file()])
            print(f"📎 Anexos organizados: {len(pastas_pacientes)} pacientes, {total_anexos} arquivos")
        else:
            print("📎 Anexos organizados: 0 (pasta não existe)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {str(e)}")
        print("💡 Verifique se as credenciais do Supabase estão corretas")
    
    print()

def mostrar_ultimos_logs():
    """Mostra logs mais recentes de importação"""
    logs_path = Path('/root/clawd/logs')
    
    if not logs_path.exists():
        print("📝 Nenhum log de importação encontrado")
        return
    
    arquivos_log = list(logs_path.glob('importacao_*.log'))
    
    if not arquivos_log:
        print("📝 Nenhum log de importação encontrado")
        return
    
    # Pegar o log mais recente
    log_mais_recente = max(arquivos_log, key=lambda f: f.stat().st_mtime)
    
    print("📝 ÚLTIMO LOG DE IMPORTAÇÃO")
    print("=" * 50)
    print(f"Arquivo: {log_mais_recente.name}")
    print()
    
    # Mostrar últimas 10 linhas
    with open(log_mais_recente, 'r') as f:
        linhas = f.readlines()
        
    print("Últimas linhas:")
    for linha in linhas[-10:]:
        print(linha.strip())
    
    print()

def main():
    print("🏥 VERIFICADOR DE IMPORTAÇÃO - Clínica Dr. Felipe")
    print("=" * 60)
    print()
    
    verificar_arquivos_importacao()
    verificar_banco_dados()
    mostrar_ultimos_logs()
    
    print("💡 PRÓXIMOS PASSOS:")
    print("- Para importar tudo: python3 /root/clawd/scripts/importador_completo.py")
    print("- Para importar apenas um tipo: python3 /root/clawd/scripts/importador_completo.py [pacientes|consultas|episodios|anexos]")
    print("- Para ver este status novamente: python3 /root/clawd/scripts/verificar_importacao.py")

if __name__ == "__main__":
    main()
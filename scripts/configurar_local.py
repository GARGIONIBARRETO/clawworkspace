#!/usr/bin/env python3

"""
Configurador para PostgreSQL Local
Configura o sistema para usar banco local enquanto Supabase está fora
"""

import json
import subprocess
import psycopg2
import os
from pathlib import Path

def criar_usuario_postgres():
    """Cria usuário postgres para o sistema"""
    try:
        # Conecta como postgres (superuser)
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Cria usuário clinica se não existir
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'clinica') THEN
                    CREATE USER clinica WITH PASSWORD 'clinica2026';
                    GRANT ALL PRIVILEGES ON DATABASE postgres TO clinica;
                END IF;
            END
            $$;
        """)
        
        # Cria database clinica se não existir
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = 'clinica_db'
        """)
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE clinica_db OWNER clinica")
        
        cursor.close()
        conn.close()
        print("✅ Usuário e database criados com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False

def criar_credenciais_locais():
    """Cria arquivo de credenciais para PostgreSQL local"""
    credenciais = {
        "host": "localhost",
        "port": 5432,
        "database": "clinica_db",
        "username": "clinica",
        "password": "clinica2026",
        "connection_string": "postgresql://clinica:clinica2026@localhost:5432/clinica_db"
    }
    
    # Salva credenciais
    os.makedirs('/root/.secrets', exist_ok=True)
    with open('/root/.secrets/supabase_credentials_local.json', 'w') as f:
        json.dump(credenciais, f, indent=2)
    
    print("✅ Credenciais locais criadas")
    return credenciais

def atualizar_scripts():
    """Atualiza scripts para usar credenciais locais"""
    scripts_dir = Path('/root/clawd/scripts')
    
    for script in scripts_dir.glob('*.py'):
        if script.name in ['db_manager.py', 'pacientes_manager.py', 'relatorios_clinicos.py']:
            try:
                content = script.read_text()
                # Substitui caminho das credenciais
                content = content.replace(
                    'supabase_credentials.json',
                    'supabase_credentials_local.json'
                )
                script.write_text(content)
                print(f"✅ {script.name} atualizado")
            except Exception as e:
                print(f"❌ Erro ao atualizar {script.name}: {e}")

def main():
    print("🏥 CONFIGURANDO SISTEMA LOCAL")
    print("=" * 50)
    
    # 1. Criar usuário e database
    if not criar_usuario_postgres():
        return False
    
    # 2. Criar credenciais
    credenciais = criar_credenciais_locais()
    
    # 3. Atualizar scripts
    atualizar_scripts()
    
    print("\n" + "=" * 50)
    print("✅ SISTEMA LOCAL CONFIGURADO!")
    print(f"Host: {credenciais['host']}")
    print(f"Database: {credenciais['database']}")
    print(f"Usuário: {credenciais['username']}")
    print("\nAgora execute:")
    print("python3 /root/clawd/scripts/db_manager.py")
    print("python3 /root/clawd/scripts/clinica_manager.py")
    
    return True

if __name__ == "__main__":
    main()
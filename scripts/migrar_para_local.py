#!/usr/bin/env python3
"""
Script para migrar completamente para PostgreSQL local
Desabilita Supabase e atualiza todos os scripts
"""

import os
import shutil
from datetime import datetime

def fazer_backup(arquivo):
    """Faz backup do arquivo antes de modificar"""
    backup_name = f"{arquivo}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(arquivo, backup_name)
    print(f"📁 Backup criado: {backup_name}")

def atualizar_db_manager():
    """Atualiza db_manager.py para usar apenas PostgreSQL local"""
    arquivo = "db_manager.py"
    fazer_backup(arquivo)
    
    novo_conteudo = '''#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Pacientes - Dr. Felipe
Base de dados PostgreSQL LOCAL
"""

import psycopg2
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class PacientesDB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Conecta ao PostgreSQL LOCAL"""
        try:
            with open('/root/.secrets/local_postgresql.json', 'r') as f:
                creds = json.load(f)
            
            self.connection = psycopg2.connect(
                host=creds['host'],
                port=creds['port'],
                database=creds['database'],
                user=creds['username'],
                password=creds['password']
            )
            self.cursor = self.connection.cursor()
            print("✅ Conectado ao PostgreSQL local com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro na conexão local: {e}")
            raise
    
    def test_connection(self):
        """Testa a conexão e mostra info do banco"""
        try:
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            print(f"📊 PostgreSQL Version: {version[0]}")
            
            self.cursor.execute("SELECT current_database();")
            db_name = self.cursor.fetchone()
            print(f"🗄️ Database: {db_name[0]}")
            
            # Contar registros
            tables = ['pacientes', 'consultas', 'exames_laboratoriais', 'bioimpedancia']
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = self.cursor.fetchone()[0]
                print(f"📋 {table}: {count} registros")
            
            return True
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.connection:
            self.connection.close()
            print("🔌 Conexão fechada")

if __name__ == "__main__":
    print("🏥 TESTE DE CONEXÃO LOCAL - Dr. Felipe")
    print("=" * 50)
    
    db = PacientesDB()
    db.test_connection()
    db.close()
'''
    
    with open(arquivo, 'w') as f:
        f.write(novo_conteudo)
    
    print(f"✅ {arquivo} atualizado para usar apenas PostgreSQL local")

def atualizar_pacientes_manager():
    """Atualiza pacientes_manager.py para usar apenas conexão local"""
    arquivo = "pacientes_manager.py"
    
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            conteudo = f.read()
        
        if 'supabase_credentials.json' in conteudo:
            fazer_backup(arquivo)
            
            # Substituir referências ao Supabase
            conteudo = conteudo.replace(
                '/root/.secrets/supabase_credentials.json',
                '/root/.secrets/local_postgresql.json'
            )
            conteudo = conteudo.replace(
                'Conectado ao Supabase',
                'Conectado ao PostgreSQL local'
            )
            
            with open(arquivo, 'w') as f:
                f.write(conteudo)
            
            print(f"✅ {arquivo} atualizado")

def criar_teste_local():
    """Cria script de teste específico para conexão local"""
    conteudo = '''#!/usr/bin/env python3
"""
Teste de conexão PostgreSQL local
"""

import psycopg2
import json

print("🔍 TESTE DE CONEXÃO POSTGRESQL LOCAL")
print("=" * 50)

try:
    with open('/root/.secrets/local_postgresql.json', 'r') as f:
        creds = json.load(f)
    
    print(f"🔗 Conectando a {creds['host']}:{creds['port']}/{creds['database']}...")
    
    conn = psycopg2.connect(
        host=creds['host'],
        port=creds['port'],
        database=creds['database'],
        user=creds['username'],
        password=creds['password']
    )
    
    cur = conn.cursor()
    
    # Teste básico
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ Conectado! PostgreSQL {version[0].split(',')[0]}")
    
    # Contar registros
    print("\\n📊 DADOS NO BANCO:")
    tables = ['pacientes', 'consultas', 'exames_laboratoriais', 'bioimpedancia']
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"  • {table}: {count} registros")
    
    conn.close()
    print("\\n✅ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"\\n❌ ERRO: {e}")
'''
    
    with open('teste_local.py', 'w') as f:
        f.write(conteudo)
    
    os.chmod('teste_local.py', 0o755)
    print("✅ teste_local.py criado")

def main():
    print("🔄 MIGRANDO PARA POSTGRESQL LOCAL")
    print("=" * 50)
    
    # Mudar para diretório dos scripts
    os.chdir('/root/clawd/scripts')
    
    # Atualizar scripts principais
    atualizar_db_manager()
    atualizar_pacientes_manager()
    criar_teste_local()
    
    # Remover arquivo de teste do Supabase
    if os.path.exists('teste_conectividade.py'):
        os.rename('teste_conectividade.py', 'teste_conectividade.py.old')
        print("📦 teste_conectividade.py arquivado")
    
    print("\n✅ MIGRAÇÃO CONCLUÍDA!")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("1. Teste a conexão: python3 teste_local.py")
    print("2. Verifique o sistema: python3 verificar_importacao.py")
    print("3. Use o sistema: python3 clinica_manager.py")

if __name__ == "__main__":
    main()
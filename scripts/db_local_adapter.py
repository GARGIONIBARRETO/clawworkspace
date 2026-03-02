#!/usr/bin/env python3
"""
Adaptador para usar PostgreSQL local em vez de Supabase
Mantém a mesma interface, mas conecta localmente
"""

import psycopg2
import json
import os
from datetime import datetime

class PostgreSQLLocal:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Conecta ao PostgreSQL local"""
        try:
            # Tentar local primeiro
            creds_file = '/root/.secrets/local_postgresql.json'
            if os.path.exists(creds_file):
                with open(creds_file, 'r') as f:
                    creds = json.load(f)
                print("🔗 Usando PostgreSQL local...")
            else:
                # Fallback para Supabase se existir
                creds_file = '/root/.secrets/supabase_credentials.json'
                with open(creds_file, 'r') as f:
                    creds = json.load(f)
                print("🔗 Tentando Supabase...")
            
            self.connection = psycopg2.connect(
                host=creds['host'],
                port=creds['port'],
                database=creds['database'],
                user=creds['username'],
                password=creds['password']
            )
            self.cursor = self.connection.cursor()
            print("✅ Conectado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
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
            
            return True
        except Exception as e:
            print(f"❌ Erro ao testar: {e}")
            return False
    
    def create_tables(self):
        """Cria todas as tabelas necessárias"""
        try:
            # Tabela de pacientes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    cpf VARCHAR(11) UNIQUE NOT NULL,
                    rg VARCHAR(20),
                    telefone VARCHAR(20),
                    email VARCHAR(255),
                    endereco TEXT,
                    data_nascimento DATE,
                    convenio VARCHAR(100) DEFAULT 'Particular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Tabela de consultas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultas (
                    id SERIAL PRIMARY KEY,
                    paciente_id INTEGER REFERENCES pacientes(id),
                    data_consulta DATE NOT NULL,
                    medico VARCHAR(255) DEFAULT 'Dr. Felipe',
                    motivo TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Tabela de exames laboratoriais
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS exames_laboratoriais (
                    id SERIAL PRIMARY KEY,
                    paciente_id INTEGER REFERENCES pacientes(id),
                    data_exame DATE NOT NULL,
                    tipo_exame VARCHAR(100) NOT NULL,
                    laboratorio VARCHAR(255),
                    parametros JSONB,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Tabela de bioimpedância
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bioimpedancia (
                    id SERIAL PRIMARY KEY,
                    paciente_id INTEGER REFERENCES pacientes(id),
                    data_medicao DATE NOT NULL,
                    peso DECIMAL(5,2),
                    altura DECIMAL(3,2),
                    imc DECIMAL(4,2),
                    gordura_corporal DECIMAL(4,2),
                    massa_muscular DECIMAL(5,2),
                    agua_corporal DECIMAL(4,2),
                    taxa_metabolica DECIMAL(6,2),
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Criar índices para performance
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes(cpf);",
                "CREATE INDEX IF NOT EXISTS idx_consultas_paciente ON consultas(paciente_id);",
                "CREATE INDEX IF NOT EXISTS idx_consultas_data ON consultas(data_consulta);",
                "CREATE INDEX IF NOT EXISTS idx_exames_paciente ON exames_laboratoriais(paciente_id);",
                "CREATE INDEX IF NOT EXISTS idx_bioimpedancia_paciente ON bioimpedancia(paciente_id);"
            ]
            
            for index_sql in indices:
                self.cursor.execute(index_sql)
            
            self.connection.commit()
            print("✅ Tabelas criadas com sucesso!")
            
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Erro ao criar tabelas: {e}")
            raise
    
    def get_stats(self):
        """Retorna estatísticas do banco"""
        stats = {}
        
        # Contar registros
        tables = ['pacientes', 'consultas', 'exames_laboratoriais', 'bioimpedancia']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
            stats[table] = self.cursor.fetchone()[0]
        
        return stats
    
    def backup_database(self, backup_path="/root/clawd/backups"):
        """Cria backup do banco de dados"""
        os.makedirs(backup_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_path}/clinica_backup_{timestamp}.sql"
        
        # Usar pg_dump para backup
        os.system(f"PGPASSWORD='clinica2026!' pg_dump -h localhost -U clinica_admin clinica_dr_felipe > {backup_file}")
        
        print(f"💾 Backup salvo: {backup_file}")
        return backup_file
    
    def close(self):
        """Fecha conexão"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Conexão fechada")

# Função para compatibilidade
def conectar_banco():
    """Conecta ao banco (local ou Supabase)"""
    return PostgreSQLLocal()

if __name__ == "__main__":
    # Teste da conexão
    db = PostgreSQLLocal()
    db.test_connection()
    db.create_tables()
    
    stats = db.get_stats()
    print(f"📊 Estatísticas: {stats}")
    
    db.close()
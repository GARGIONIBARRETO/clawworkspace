#!/usr/bin/env python3
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

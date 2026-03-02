#!/usr/bin/env python3
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
    print("\n📊 DADOS NO BANCO:")
    tables = ['pacientes', 'consultas', 'exames_laboratoriais', 'bioimpedancia']
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"  • {table}: {count} registros")
    
    conn.close()
    print("\n✅ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")

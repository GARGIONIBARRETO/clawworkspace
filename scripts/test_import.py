#!/usr/bin/env python3
"""
Teste simples de importação - Templates já existem
"""

import sys
sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

def test_import():
    db = PostgreSQLLocal()
    
    # Teste rápido - inserir um paciente
    try:
        db.cursor.execute("""
        INSERT INTO pacientes (nome, cpf, telefone, convenio, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        """, ("Dr. Felipe Teste", "12345678900", "(11) 99999-9999", "Particular"))
        
        db.connection.commit()
        print("✅ Paciente de teste inserido!")
        
        # Verificar
        db.cursor.execute("SELECT COUNT(*) FROM pacientes")
        count = db.cursor.fetchone()[0]
        print(f"📊 Total pacientes: {count}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    db.close()

if __name__ == "__main__":
    test_import()
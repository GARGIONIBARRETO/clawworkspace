#!/usr/bin/env python3
"""
Ajusta tabela para permitir CPF opcional
"""

import sys
sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

def ajustar_banco():
    """Remove constraint NOT NULL do CPF"""
    db = PostgreSQLLocal()
    
    try:
        # Tornar CPF opcional
        db.cursor.execute("ALTER TABLE pacientes ALTER COLUMN cpf DROP NOT NULL;")
        
        # Remover constraint UNIQUE do CPF (se existir)
        db.cursor.execute("ALTER TABLE pacientes DROP CONSTRAINT IF EXISTS pacientes_cpf_key;")
        
        # Adicionar constraint UNIQUE apenas para CPFs não nulos
        db.cursor.execute("CREATE UNIQUE INDEX pacientes_cpf_unique ON pacientes (cpf) WHERE cpf IS NOT NULL;")
        
        db.connection.commit()
        print("✅ Banco ajustado: CPF agora é opcional")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.connection.rollback()
    
    db.close()

if __name__ == "__main__":
    ajustar_banco()
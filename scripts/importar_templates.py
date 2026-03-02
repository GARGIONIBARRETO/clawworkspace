#!/usr/bin/env python3
"""
Importador simples para testar com os templates existentes
"""

import sys
import pandas as pd
from datetime import datetime
sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

def importar_templates():
    db = PostgreSQLLocal()
    
    print("🚀 Importando templates de exemplo...")
    
    try:
        # 1. Importar pacientes
        print("\n👥 Importando pacientes...")
        df_pacientes = pd.read_csv('/root/clawd/importacao/pacientes/template_pacientes.csv')
        
        for _, row in df_pacientes.iterrows():
            cpf = str(row['cpf']).replace('.', '').replace('-', '')
            
            db.cursor.execute("""
            INSERT INTO pacientes (nome, cpf, rg, telefone, email, endereco, data_nascimento, convenio, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (cpf) DO NOTHING
            """, (
                row['nome'], cpf, str(row.get('rg', '')), 
                str(row.get('telefone', '')), str(row.get('email', '')),
                str(row.get('endereco', '')), row.get('data_nascimento'),
                str(row.get('convenio', 'Particular'))
            ))
            
            print(f"✅ {row['nome']} (CPF: {cpf})")
        
        db.connection.commit()
        
        # 2. Importar consultas
        print("\n🩺 Importando consultas...")
        df_consultas = pd.read_csv('/root/clawd/importacao/consultas/template_consultas.csv')
        
        for _, row in df_consultas.iterrows():
            cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
            
            # Buscar ID do paciente
            db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
            paciente = db.cursor.fetchone()
            
            if paciente:
                db.cursor.execute("""
                INSERT INTO consultas (paciente_id, data_consulta, medico, motivo, observacoes, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    paciente[0], row['data_consulta'], 
                    str(row.get('medico', 'Dr. Felipe')),
                    str(row.get('motivo', '')), str(row.get('observacoes', ''))
                ))
                
                print(f"✅ Consulta para CPF {cpf} em {row['data_consulta']}")
        
        db.connection.commit()
        
        # 3. Importar episódios clínicos
        print("\n🏥 Importando episódios clínicos...")
        df_episodios = pd.read_csv('/root/clawd/importacao/episodios_clinicos/template_episodios.csv')
        
        for _, row in df_episodios.iterrows():
            cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
            
            # Buscar ID do paciente
            db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
            paciente = db.cursor.fetchone()
            
            if paciente:
                observacoes = f"DESCRIÇÃO: {row.get('descricao', '')}\n\nDIAGNÓSTICO: {row.get('diagnostico', '')}\n\nTRATAMENTO: {row.get('tratamento', '')}"
                
                db.cursor.execute("""
                INSERT INTO consultas (paciente_id, data_consulta, medico, motivo, observacoes, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    paciente[0], row.get('data_episodio'), 'Dr. Felipe',
                    f"EPISÓDIO: {row.get('tipo_episodio', 'Clínico')}", observacoes
                ))
                
                print(f"✅ Episódio {row.get('tipo_episodio')} para CPF {cpf}")
        
        db.connection.commit()
        
        # Mostrar estatísticas finais
        print("\n📊 ESTATÍSTICAS FINAIS:")
        stats = db.get_stats()
        print(f"👥 Pacientes: {stats['pacientes']}")
        print(f"🩺 Consultas: {stats['consultas']}")
        print(f"🔬 Exames: {stats['exames_laboratoriais']}")
        print(f"⚖️ Bioimpedância: {stats['bioimpedancia']}")
        
        print("\n✅ IMPORTAÇÃO COMPLETA! Sistema pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        db.connection.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    importar_templates()
#!/usr/bin/env python3
"""
Processador CSV v2 - Aceita pacientes sem CPF
"""

import pandas as pd
import sys
from datetime import datetime
import re
import uuid

sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

def processar_csv_completo():
    """Processa todos os registros, incluindo sem CPF"""
    
    db = PostgreSQLLocal()
    
    # Primeiro, limpar dados de teste
    print("🧹 Limpando dados de teste anteriores...")
    db.cursor.execute("DELETE FROM consultas;")
    db.cursor.execute("DELETE FROM pacientes WHERE nome LIKE '%Template%' OR nome LIKE '%Teste%';")
    db.connection.commit()
    
    # Ler CSV
    print("📄 Lendo arquivo CSV completo...")
    df = pd.read_csv('/root/.clawdbot/media/inbound/49739f5f-1772-4763-94c4-a390a03855b2.csv', 
                     sep=';', encoding='utf-8')
    
    print(f"📊 Total de {len(df)} registros para processar")
    
    importados = 0
    erros = 0
    
    for index, row in df.iterrows():
        try:
            # Nome completo
            first_name = str(row.get('first name', '')).strip()
            last_name = str(row.get('last name', '')).strip()
            nome_completo = f"{first_name} {last_name}".strip()
            
            if not nome_completo or nome_completo == ' ' or len(nome_completo) < 2:
                continue
                
            # CPF - pode ser vazio agora
            cpf_raw = row.get('document', '')
            cpf = None
            if pd.notna(cpf_raw) and cpf_raw:
                cpf = re.sub(r'[^\d]', '', str(cpf_raw))
                if len(cpf) == 11:
                    cpf = cpf
                else:
                    cpf = None
            
            # Outros dados
            telefone = str(row.get('phone', '')).replace("'", "").replace("+55", "").strip()
            if telefone and len(telefone) >= 10:
                telefone = re.sub(r'[^\d]', '', telefone)
                if len(telefone) == 11:
                    telefone = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
                elif len(telefone) == 10:
                    telefone = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
            
            email = str(row.get('email', '')).strip() if pd.notna(row.get('email')) else ''
            
            # Data nascimento
            data_nasc = row.get('date of birth')
            data_nascimento = None
            if pd.notna(data_nasc) and str(data_nasc) != '':
                if '-' in str(data_nasc) and len(str(data_nasc)) == 10:
                    data_nascimento = str(data_nasc)
            
            # Endereço
            endereco_parts = []
            for field in ['address street', 'address number', 'address city', 'address state']:
                value = row.get(field)
                if pd.notna(value) and str(value).strip():
                    endereco_parts.append(str(value).strip())
            endereco = ', '.join(endereco_parts) if endereco_parts else ''
            
            # Convênio
            insurance = row.get('insurance', '')
            convenio = 'Particular'
            if pd.notna(insurance) and insurance:
                insurance_clean = str(insurance).replace('*', '').strip()
                if insurance_clean.lower() not in ['no insurance', 'private', '']:
                    convenio = insurance_clean
            
            # Inserir no banco
            insert_sql = """
            INSERT INTO pacientes (nome, cpf, telefone, email, endereco, data_nascimento, convenio, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            db.cursor.execute(insert_sql, (
                nome_completo[:255],  # Limitar tamanho
                cpf,
                telefone[:20] if telefone else None,
                email[:255] if email else None,
                endereco[:500] if endereco else None,
                data_nascimento,
                convenio[:100]
            ))
            
            db.connection.commit()
            importados += 1
            
            if importados % 50 == 0:
                print(f"✅ Processados: {importados}")
            
        except Exception as e:
            erros += 1
            if erros <= 10:  # Mostrar apenas os primeiros 10 erros
                print(f"❌ Erro linha {index+1}: {str(e)}")
            db.connection.rollback()
    
    print(f"\n🎉 IMPORTAÇÃO FINALIZADA!")
    print(f"✅ Importados: {importados}")
    print(f"❌ Erros: {erros}")
    
    # Estatísticas finais
    db.cursor.execute("SELECT COUNT(*) FROM pacientes")
    total = db.cursor.fetchone()[0]
    print(f"💾 Total no banco: {total} pacientes")
    
    # Estatísticas por tipo
    db.cursor.execute("SELECT COUNT(*) FROM pacientes WHERE cpf IS NOT NULL")
    com_cpf = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM pacientes WHERE cpf IS NULL")
    sem_cpf = db.cursor.fetchone()[0]
    
    print(f"📊 Com CPF: {com_cpf} | Sem CPF: {sem_cpf}")
    
    db.close()
    
    return importados, erros

if __name__ == "__main__":
    processar_csv_completo()
#!/usr/bin/env python3
"""
Processador específico para o CSV do Dr. Felipe
Converte dados do sistema antigo para o formato do PostgreSQL local
"""

import pandas as pd
import sys
from datetime import datetime
import re

sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

def limpar_telefone(telefone):
    """Limpa e formata número de telefone"""
    if pd.isna(telefone) or telefone == '':
        return ''
    
    # Remove aspas e caracteres especiais
    telefone = str(telefone).replace("'", "").replace("+55", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    
    # Remove caracteres não numéricos
    telefone = re.sub(r'[^\d]', '', telefone)
    
    # Formatar telefone brasileiro
    if len(telefone) == 11:  # Celular: 11987654321
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:  # Fixo: 1133334444
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    
    return telefone

def limpar_cpf(document):
    """Extrai e limpa CPF"""
    if pd.isna(document) or document == '':
        return ''
    
    # Remove tudo que não é dígito
    cpf = re.sub(r'[^\d]', '', str(document))
    
    # Verifica se tem 11 dígitos
    if len(cpf) == 11:
        return cpf
    
    return ''

def formatar_data(data_str):
    """Formata data para PostgreSQL"""
    if pd.isna(data_str) or data_str == '':
        return None
    
    try:
        # Formato: YYYY-MM-DD
        if '-' in str(data_str) and len(str(data_str)) == 10:
            return str(data_str)
        return None
    except:
        return None

def processar_csv_felipe():
    """Processa o CSV específico do Felipe"""
    
    # Conectar ao banco
    db = PostgreSQLLocal()
    
    # Ler CSV com separador correto
    print("📄 Lendo arquivo CSV...")
    df = pd.read_csv('/root/.clawdbot/media/inbound/49739f5f-1772-4763-94c4-a390a03855b2.csv', 
                     sep=';', encoding='utf-8')
    
    print(f"📊 Encontrados {len(df)} registros para processar")
    
    importados = 0
    erros = 0
    
    for index, row in df.iterrows():
        try:
            # Extrair dados principais
            nome_completo = f"{row.get('first name', '')} {row.get('last name', '')}".strip()
            if not nome_completo or nome_completo == ' ':
                print(f"⚠️  Linha {index+1}: Nome vazio - pulando")
                continue
                
            cpf = limpar_cpf(row.get('document', ''))
            telefone = limpar_telefone(row.get('phone', ''))
            email = str(row.get('email', '')).strip() if pd.notna(row.get('email')) else ''
            data_nascimento = formatar_data(row.get('date of birth'))
            
            # Endereço
            endereco_parts = []
            if pd.notna(row.get('address street')) and row.get('address street'):
                endereco_parts.append(str(row.get('address street')))
            if pd.notna(row.get('address number')) and row.get('address number'):
                endereco_parts.append(str(row.get('address number')))
            if pd.notna(row.get('address city')) and row.get('address city'):
                endereco_parts.append(str(row.get('address city')))
            if pd.notna(row.get('address state')) and row.get('address state'):
                endereco_parts.append(str(row.get('address state')))
                
            endereco = ', '.join(endereco_parts) if endereco_parts else ''
            
            # Convênio
            convenio = 'Particular'
            if pd.notna(row.get('insurance')) and row.get('insurance'):
                convenio = str(row.get('insurance')).replace('*', '').strip()
                if 'no insurance' in convenio.lower() or convenio.lower() == 'private':
                    convenio = 'Particular'
            
            # Inserir no banco
            insert_sql = """
            INSERT INTO pacientes (nome, cpf, telefone, email, endereco, data_nascimento, convenio, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (cpf) DO UPDATE SET
                nome = EXCLUDED.nome,
                telefone = EXCLUDED.telefone,
                email = EXCLUDED.email,
                endereco = EXCLUDED.endereco,
                data_nascimento = EXCLUDED.data_nascimento,
                convenio = EXCLUDED.convenio,
                updated_at = NOW()
            WHERE pacientes.cpf = EXCLUDED.cpf AND LENGTH(EXCLUDED.cpf) = 11
            """
            
            db.cursor.execute(insert_sql, (
                nome_completo,
                cpf if cpf else None,
                telefone,
                email,
                endereco,
                data_nascimento,
                convenio
            ))
            
            db.connection.commit()
            importados += 1
            
            if importados % 50 == 0:  # Log a cada 50 registros
                print(f"✅ Processados: {importados}")
            
        except Exception as e:
            erros += 1
            print(f"❌ Erro linha {index+1} ({nome_completo}): {str(e)}")
            db.connection.rollback()
    
    # Estatísticas finais
    print(f"\n📊 IMPORTAÇÃO CONCLUÍDA!")
    print(f"✅ Importados: {importados} pacientes")
    print(f"❌ Erros: {erros}")
    
    # Verificar total no banco
    db.cursor.execute("SELECT COUNT(*) FROM pacientes")
    total = db.cursor.fetchone()[0]
    print(f"💾 Total no banco: {total} pacientes")
    
    db.close()
    
    return importados, erros

if __name__ == "__main__":
    processar_csv_felipe()
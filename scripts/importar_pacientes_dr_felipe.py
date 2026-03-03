#!/usr/bin/env python3
"""
Importador simplificado de pacientes para Dr. Felipe
Aceita pacientes sem CPF e importa histórico médico
"""

import pandas as pd
import psycopg2
import json
from datetime import datetime
import sys

def conectar_db():
    """Conecta ao PostgreSQL local"""
    return psycopg2.connect(
        dbname="clinica_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )

def importar_pacientes(arquivo_csv):
    """Importa pacientes do CSV"""
    try:
        # Ler CSV
        df = pd.read_csv(arquivo_csv)
        print(f"📋 Encontrados {len(df)} pacientes no arquivo")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        sucesso = 0
        erros = 0
        
        for idx, row in df.iterrows():
            try:
                # Preparar dados (CPF é opcional)
                dados = {
                    'nome': row.get('nome', '').strip(),
                    'data_nascimento': row.get('data_nascimento'),
                    'sexo': row.get('sexo', '').upper(),
                    'telefone': row.get('telefone', '').strip(),
                    'email': row.get('email', '').strip() if pd.notna(row.get('email')) else None,
                    'cpf': row.get('cpf', '').strip() if pd.notna(row.get('cpf')) else None,
                    'endereco': row.get('endereco', '').strip() if pd.notna(row.get('endereco')) else None,
                    'cidade': row.get('cidade', '').strip() if pd.notna(row.get('cidade')) else None,
                    'estado': row.get('estado', '').strip() if pd.notna(row.get('estado')) else None,
                    'cep': row.get('cep', '').strip() if pd.notna(row.get('cep')) else None,
                    'historico_medico': row.get('historico_medico', '').strip() if pd.notna(row.get('historico_medico')) else None,
                    'medicacoes_atuais': row.get('medicacoes_atuais', '').strip() if pd.notna(row.get('medicacoes_atuais')) else None,
                    'alergias': row.get('alergias', '').strip() if pd.notna(row.get('alergias')) else None,
                    'observacoes': row.get('observacoes', '').strip() if pd.notna(row.get('observacoes')) else None
                }
                
                # Inserir paciente
                cur.execute("""
                    INSERT INTO pacientes (
                        nome, data_nascimento, sexo, telefone, email, cpf,
                        endereco, cidade, estado, cep,
                        historico_medico, medicacoes_atuais, alergias, observacoes
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """, (
                    dados['nome'], dados['data_nascimento'], dados['sexo'],
                    dados['telefone'], dados['email'], dados['cpf'],
                    dados['endereco'], dados['cidade'], dados['estado'], dados['cep'],
                    dados['historico_medico'], dados['medicacoes_atuais'],
                    dados['alergias'], dados['observacoes']
                ))
                
                paciente_id = cur.fetchone()[0]
                
                print(f"✅ {dados['nome']} - ID: {paciente_id}")
                sucesso += 1
                
            except Exception as e:
                print(f"❌ Erro ao importar linha {idx + 1}: {str(e)}")
                erros += 1
                conn.rollback()
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n📊 Resumo da importação:")
        print(f"✅ Sucesso: {sucesso} pacientes")
        print(f"❌ Erros: {erros} pacientes")
        
        return sucesso > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def importar_prontuarios(arquivo_csv):
    """Importa prontuários/consultas do CSV"""
    try:
        df = pd.read_csv(arquivo_csv)
        print(f"📋 Importando prontuários de {len(df)} pacientes")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        for idx, row in df.iterrows():
            # Buscar paciente pelo nome
            nome = row.get('nome', '').strip()
            cur.execute("SELECT id FROM pacientes WHERE nome = %s", (nome,))
            result = cur.fetchone()
            
            if result:
                paciente_id = result[0]
                
                # Criar consulta com o histórico
                if pd.notna(row.get('historico_medico')):
                    cur.execute("""
                        INSERT INTO consultas (
                            paciente_id, data_consulta, anamnese, 
                            diagnostico, conduta
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (
                        paciente_id,
                        datetime.now().date(),
                        row.get('historico_medico', ''),
                        'Histórico importado do sistema anterior',
                        row.get('medicacoes_atuais', '')
                    ))
                    print(f"📝 Prontuário importado para {nome}")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao importar prontuários: {str(e)}")

if __name__ == "__main__":
    print("🏥 Importador de Pacientes - Dr. Felipe Barreto")
    print("=" * 50)
    
    arquivo = "/root/clawd/importar_pacientes_felipe.csv"
    if len(sys.argv) > 1:
        arquivo = sys.argv[1]
    
    print(f"📂 Arquivo: {arquivo}")
    
    if importar_pacientes(arquivo):
        print("\n📝 Importando históricos como prontuários...")
        importar_prontuarios(arquivo)
        print("\n✅ Importação concluída!")
    else:
        print("\n❌ Falha na importação")
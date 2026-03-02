#!/usr/bin/env python3
import pandas as pd
from scripts.db_local_adapter import PostgreSQLLocal as DatabaseAdapter
import sys

def importar_pacientes_sem_cpf(arquivo_csv):
    """Importa pacientes permitindo CPF vazio"""
    db = DatabaseAdapter()
    
    try:
        # Ler CSV
        df = pd.read_csv(arquivo_csv)
        print(f"📋 Importando {len(df)} pacientes...")
        
        sucesso = 0
        for idx, row in df.iterrows():
            try:
                # Preparar dados - CPF pode ser None
                paciente_data = {
                    'nome': row.get('nome', '').strip(),
                    'data_nascimento': row.get('data_nascimento'),
                    'sexo': row.get('sexo', '').upper(),
                    'telefone': row.get('telefone', '').strip(),
                    'email': row.get('email', '').strip() if pd.notna(row.get('email')) else None,
                    'cpf': row.get('cpf', '').strip() if pd.notna(row.get('cpf')) and row.get('cpf', '').strip() else None,
                    'endereco': row.get('endereco', '').strip() if pd.notna(row.get('endereco')) else '',
                    'cidade': row.get('cidade', '').strip() if pd.notna(row.get('cidade')) else '',
                    'estado': row.get('estado', '').strip() if pd.notna(row.get('estado')) else '',
                    'cep': row.get('cep', '').strip() if pd.notna(row.get('cep')) else '',
                    'historico_medico': row.get('historico_medico', '').strip() if pd.notna(row.get('historico_medico')) else '',
                    'medicacoes_atuais': row.get('medicacoes_atuais', '').strip() if pd.notna(row.get('medicacoes_atuais')) else '',
                    'alergias': row.get('alergias', '').strip() if pd.notna(row.get('alergias')) else '',
                    'observacoes': row.get('observacoes', '').strip() if pd.notna(row.get('observacoes')) else ''
                }
                
                # Adicionar paciente
                paciente_id = db.adicionar_paciente(paciente_data)
                print(f"✅ {paciente_data['nome']} - ID: {paciente_id}")
                
                # Se tem histórico, criar consulta inicial
                if paciente_data.get('historico_medico'):
                    consulta_data = {
                        'paciente_id': paciente_id,
                        'data_consulta': '2026-03-02',
                        'anamnese': paciente_data['historico_medico'],
                        'exame_fisico': 'Histórico importado do sistema anterior',
                        'hipotese_diagnostica': '',
                        'conduta': paciente_data.get('medicacoes_atuais', ''),
                        'retorno': '',
                        'observacoes': f"Alergias: {paciente_data.get('alergias', 'Não informadas')}"
                    }
                    db.adicionar_consulta(consulta_data)
                    print(f"   📝 Prontuário histórico adicionado")
                
                sucesso += 1
                
            except Exception as e:
                print(f"❌ Erro linha {idx + 1}: {str(e)}")
                continue
        
        print(f"\n✅ Importação concluída: {sucesso}/{len(df)} pacientes")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        db.fechar_conexao()

if __name__ == "__main__":
    arquivo = sys.argv[1] if len(sys.argv) > 1 else "/root/clawd/pacientes_novos_felipe.csv"
    importar_pacientes_sem_cpf(arquivo)
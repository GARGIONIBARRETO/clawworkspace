#!/usr/bin/env python3
"""
Importador de Consultas e Históricos - Dr. Felipe
Aceita CSV simples e conecta com pacientes existentes
"""

import pandas as pd
import psycopg2
from datetime import datetime
import sys

def conectar_db():
    """Conecta ao PostgreSQL local"""
    return psycopg2.connect(
        dbname="clinica_db",
        user="clinica_user",
        password="clinica_password",
        host="localhost",
        port="5432"
    )

def buscar_paciente_id(conn, nome_paciente):
    """Busca ID do paciente pelo nome (aceita match parcial)"""
    cur = conn.cursor()
    
    # Primeiro tenta match exato
    cur.execute("SELECT id, nome FROM pacientes WHERE LOWER(nome) = LOWER(%s)", (nome_paciente,))
    result = cur.fetchone()
    
    if result:
        return result[0], result[1]
    
    # Se não encontrou, tenta match parcial
    cur.execute("""
        SELECT id, nome FROM pacientes 
        WHERE LOWER(nome) LIKE LOWER(%s) 
        ORDER BY nome 
        LIMIT 1
    """, (f'%{nome_paciente}%',))
    result = cur.fetchone()
    
    return (result[0], result[1]) if result else (None, None)

def importar_consultas(arquivo_csv):
    """Importa consultas do CSV"""
    print("🏥 Importando Consultas...")
    print("=" * 50)
    
    try:
        # Ler CSV
        df = pd.read_csv(arquivo_csv)
        print(f"📋 {len(df)} consultas encontradas no arquivo\n")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        sucesso = 0
        nao_encontrados = []
        
        for idx, row in df.iterrows():
            nome_busca = row.get('nome_paciente', '').strip()
            
            # Buscar paciente
            paciente_id, nome_real = buscar_paciente_id(conn, nome_busca)
            
            if not paciente_id:
                nao_encontrados.append(nome_busca)
                print(f"❌ Paciente não encontrado: {nome_busca}")
                continue
            
            # Preparar dados da consulta
            try:
                consulta_data = {
                    'paciente_id': paciente_id,
                    'data_consulta': row.get('data_consulta', datetime.now().strftime('%Y-%m-%d')),
                    'anamnese': f"Queixa principal: {row.get('queixa_principal', '')}\n\nHistória: {row.get('historia_doenca', '')}",
                    'exame_fisico': row.get('exame_fisico', ''),
                    'hipotese_diagnostica': row.get('hipotese_diagnostica', ''),
                    'conduta': row.get('conduta', ''),
                    'retorno': row.get('retorno', ''),
                    'observacoes': row.get('observacoes', '')
                }
                
                # Inserir consulta
                cur.execute("""
                    INSERT INTO consultas (
                        paciente_id, data_consulta, anamnese, exame_fisico,
                        hipotese_diagnostica, conduta, retorno, observacoes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    consulta_data['paciente_id'],
                    consulta_data['data_consulta'],
                    consulta_data['anamnese'],
                    consulta_data['exame_fisico'],
                    consulta_data['hipotese_diagnostica'],
                    consulta_data['conduta'],
                    consulta_data['retorno'],
                    consulta_data['observacoes']
                ))
                
                consulta_id = cur.fetchone()[0]
                print(f"✅ {nome_real} - Consulta {consulta_data['data_consulta']} (ID: {consulta_id})")
                sucesso += 1
                
            except Exception as e:
                print(f"❌ Erro ao importar consulta de {nome_real}: {str(e)}")
                conn.rollback()
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n📊 Resumo:")
        print(f"✅ Importadas: {sucesso} consultas")
        if nao_encontrados:
            print(f"⚠️  Pacientes não encontrados: {len(nao_encontrados)}")
            for nome in nao_encontrados[:5]:  # Mostrar só os primeiros 5
                print(f"   - {nome}")
            if len(nao_encontrados) > 5:
                print(f"   ... e mais {len(nao_encontrados) - 5}")
        
        return sucesso > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def importar_historicos(arquivo_csv):
    """Importa históricos médicos e atualiza pacientes"""
    print("\n📝 Importando Históricos Médicos...")
    print("=" * 50)
    
    try:
        df = pd.read_csv(arquivo_csv)
        print(f"📋 {len(df)} históricos encontrados\n")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        sucesso = 0
        
        for idx, row in df.iterrows():
            nome_busca = row.get('nome_paciente', '').strip()
            
            # Buscar paciente
            paciente_id, nome_real = buscar_paciente_id(conn, nome_busca)
            
            if not paciente_id:
                print(f"❌ Paciente não encontrado: {nome_busca}")
                continue
            
            try:
                # Montar histórico completo
                historico_parts = []
                
                if pd.notna(row.get('diagnosticos_previos')):
                    historico_parts.append(f"DIAGNÓSTICOS PRÉVIOS: {row['diagnosticos_previos']}")
                
                if pd.notna(row.get('cirurgias_anteriores')) and row['cirurgias_anteriores'] != 'Nenhuma':
                    historico_parts.append(f"CIRURGIAS: {row['cirurgias_anteriores']}")
                
                if pd.notna(row.get('exames_importantes')):
                    historico_parts.append(f"EXAMES RELEVANTES: {row['exames_importantes']}")
                
                historico = '\n\n'.join(historico_parts)
                
                # Atualizar paciente
                cur.execute("""
                    UPDATE pacientes SET
                        historico_medico = COALESCE(historico_medico, '') || %s,
                        medicacoes_atuais = COALESCE(%s, medicacoes_atuais),
                        alergias = COALESCE(%s, alergias),
                        observacoes = COALESCE(observacoes, '') || %s,
                        data_atualizacao = NOW()
                    WHERE id = %s
                """, (
                    '\n\n' + historico if historico else '',
                    row.get('medicacoes_cronicas', ''),
                    row.get('alergias', ''),
                    '\n' + row.get('observacoes_gerais', '') if pd.notna(row.get('observacoes_gerais')) else '',
                    paciente_id
                ))
                
                print(f"✅ {nome_real} - Histórico atualizado")
                sucesso += 1
                
            except Exception as e:
                print(f"❌ Erro ao importar histórico de {nome_real}: {str(e)}")
                conn.rollback()
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n✅ {sucesso} históricos importados com sucesso!")
        
        return sucesso > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def menu_principal():
    """Menu interativo para importação"""
    print("🏥 IMPORTADOR DE DADOS - DR. FELIPE")
    print("=" * 50)
    print("1. Importar CONSULTAS")
    print("2. Importar HISTÓRICOS")
    print("3. Importar AMBOS")
    print("0. Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "1":
        arquivo = input("Nome do arquivo CSV de consultas [template_consultas_felipe.csv]: ").strip()
        arquivo = arquivo or "template_consultas_felipe.csv"
        importar_consultas(arquivo)
    
    elif opcao == "2":
        arquivo = input("Nome do arquivo CSV de históricos [template_historico_felipe.csv]: ").strip()
        arquivo = arquivo or "template_historico_felipe.csv"
        importar_historicos(arquivo)
    
    elif opcao == "3":
        print("\n📋 Importando consultas...")
        arquivo1 = input("Arquivo de consultas [template_consultas_felipe.csv]: ").strip()
        arquivo1 = arquivo1 or "template_consultas_felipe.csv"
        
        print("\n📝 Importando históricos...")
        arquivo2 = input("Arquivo de históricos [template_historico_felipe.csv]: ").strip()
        arquivo2 = arquivo2 or "template_historico_felipe.csv"
        
        if importar_consultas(arquivo1):
            importar_historicos(arquivo2)
    
    elif opcao == "0":
        print("👋 Até logo!")
        return
    
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo direto com arquivo
        if "consulta" in sys.argv[1].lower():
            importar_consultas(sys.argv[1])
        elif "historico" in sys.argv[1].lower():
            importar_historicos(sys.argv[1])
        else:
            print("❌ Use: python importar_consultas_felipe.py [arquivo_consultas.csv | arquivo_historico.csv]")
    else:
        # Modo interativo
        menu_principal()
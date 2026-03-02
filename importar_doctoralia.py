#!/usr/bin/env python3
"""
Importador de dados do Doctoralia para o sistema Dr. Felipe
Processa CSV exportado do Doctoralia e importa pacientes + consultas
"""

import pandas as pd
import psycopg2
from datetime import datetime
import sys
import re

def conectar_db():
    """Conecta ao PostgreSQL local"""
    return psycopg2.connect(
        dbname="clinica_dr_felipe",
        user="clinica_admin",
        password="clinica2026!",
        host="localhost",
        port="5432"
    )

def limpar_nome(nome):
    """Remove caracteres especiais e normaliza nomes"""
    if pd.isna(nome):
        return ''
    # Remove aspas extras e espaços
    nome = str(nome).strip('"').strip()
    return nome

def processar_doctoralia(arquivo_csv):
    """Processa arquivo CSV do Doctoralia"""
    print("🏥 IMPORTADOR DOCTORALIA - DR. FELIPE BARRETO")
    print("=" * 60)
    
    try:
        # Ler CSV com delimitador correto
        df = pd.read_csv(arquivo_csv, delimiter=';', encoding='utf-8-sig')
        print(f"📋 Total de registros: {len(df)}")
        
        # Filtrar apenas consultas (não canceladas)
        df_validas = df[~df['appointment status'].str.contains('Canceled', na=False)]
        print(f"✅ Consultas válidas: {len(df_validas)}")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        # Dicionário para rastrear pacientes já importados
        pacientes_importados = {}
        novos_pacientes = 0
        consultas_importadas = 0
        
        # Processar cada linha
        for idx, row in df_validas.iterrows():
            try:
                # Limpar dados do paciente
                nome = limpar_nome(row.get('first name', ''))
                sobrenome = limpar_nome(row.get('last name', ''))
                nome_completo = f"{nome} {sobrenome}".strip()
                
                if not nome_completo or nome_completo.lower() in ['representante', 'teste teste']:
                    continue
                
                # Verificar se é representante/reunião
                if any(palavra in nome_completo.lower() for palavra in ['representante', 'reuniao', 'cirurgia']):
                    continue
                
                # Buscar ou criar paciente
                if nome_completo not in pacientes_importados:
                    # Verificar se já existe
                    cur.execute("""
                        SELECT id FROM pacientes 
                        WHERE LOWER(nome) = LOWER(%s) 
                        OR (LOWER(nome) LIKE LOWER(%s) AND LOWER(nome) LIKE LOWER(%s))
                    """, (nome_completo, f'%{nome}%', f'%{sobrenome}%'))
                    
                    result = cur.fetchone()
                    
                    if result:
                        paciente_id = result[0]
                        pacientes_importados[nome_completo] = paciente_id
                    else:
                        # Criar novo paciente
                        cur.execute("""
                            INSERT INTO pacientes (
                                nome, telefone, email, data_cadastro
                            ) VALUES (%s, %s, %s, %s)
                            RETURNING id
                        """, (
                            nome_completo,
                            '(11) 0000-0000',  # Placeholder - Doctoralia não exporta telefone
                            '',  # Email vazio
                            datetime.now()
                        ))
                        
                        paciente_id = cur.fetchone()[0]
                        pacientes_importados[nome_completo] = paciente_id
                        novos_pacientes += 1
                        print(f"   👤 Novo paciente: {nome_completo} (ID: {paciente_id})")
                else:
                    paciente_id = pacientes_importados[nome_completo]
                
                # Processar consulta
                data_consulta = pd.to_datetime(row['start time']).date()
                
                # Extrair informações dos comments
                comentarios = row.get('comments', '') if pd.notna(row.get('comments')) else ''
                
                # Criar consulta
                cur.execute("""
                    INSERT INTO consultas (
                        paciente_id, data_consulta, 
                        motivo, observacoes
                    ) VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (
                    paciente_id,
                    data_consulta,
                    f"Consulta {row.get('service', '')} - Local: {row.get('agenda', '')}",
                    comentarios
                ))
                
                result = cur.fetchone()
                if result:
                    consultas_importadas += 1
                    if consultas_importadas % 50 == 0:
                        print(f"   📝 {consultas_importadas} consultas processadas...")
                
            except Exception as e:
                print(f"⚠️  Erro linha {idx}: {str(e)[:80]}")
                conn.rollback()
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DA IMPORTAÇÃO:")
        print(f"✅ Novos pacientes: {novos_pacientes}")
        print(f"✅ Consultas importadas: {consultas_importadas}")
        print(f"📁 Total de pacientes processados: {len(pacientes_importados)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def estatisticas_doctoralia(arquivo_csv):
    """Mostra estatísticas do arquivo Doctoralia"""
    try:
        df = pd.read_csv(arquivo_csv, delimiter=';', encoding='utf-8-sig')
        
        print("\n📊 ESTATÍSTICAS DO ARQUIVO:")
        print(f"Total de registros: {len(df)}")
        
        # Status das consultas
        print("\n📅 Status das consultas:")
        status_counts = df['appointment status'].value_counts()
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
        
        # Locais de atendimento
        print("\n🏥 Locais de atendimento:")
        locais = df['agenda'].value_counts()
        for local, count in locais.items():
            if count > 10:  # Mostrar apenas locais com mais de 10 consultas
                print(f"  - {local}: {count} consultas")
        
        # Período
        df['data'] = pd.to_datetime(df['start time'])
        print(f"\n📅 Período: {df['data'].min().date()} até {df['data'].max().date()}")
        
        # Anos
        print("\n📆 Consultas por ano:")
        anos = df['data'].dt.year.value_counts().sort_index()
        for ano, count in anos.items():
            print(f"  - {ano}: {count} consultas")
            
    except Exception as e:
        print(f"❌ Erro ao gerar estatísticas: {str(e)}")

if __name__ == "__main__":
    arquivo = "/root/.clawdbot/media/inbound/f11f920a-bf16-4488-a164-6739557aabac.csv"
    
    print("🏥 IMPORTADOR DOCTORALIA - DR. FELIPE BARRETO")
    print("=" * 60)
    print("1. Ver estatísticas do arquivo")
    print("2. Importar dados (pacientes + consultas)")
    print("3. Ambos (estatísticas + importação)")
    
    opcao = input("\nEscolha [1-3]: ").strip()
    
    if opcao == "1":
        estatisticas_doctoralia(arquivo)
    elif opcao == "2":
        processar_doctoralia(arquivo)
    elif opcao == "3":
        estatisticas_doctoralia(arquivo)
        print("\n" + "=" * 60 + "\n")
        if input("Continuar com importação? [S/n]: ").strip().lower() != 'n':
            processar_doctoralia(arquivo)
    else:
        print("❌ Opção inválida!")
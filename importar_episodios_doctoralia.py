#!/usr/bin/env python3
"""
Importador de Episódios Clínicos e Anexos do Doctoralia
Processa prontuários detalhados com observações, diagnósticos e prescrições
"""

import pandas as pd
import psycopg2
from datetime import datetime
import sys
import json

def conectar_db():
    """Conecta ao PostgreSQL local"""
    return psycopg2.connect(
        dbname="clinica_dr_felipe",
        user="clinica_admin",
        password="clinica2026!",
        host="localhost",
        port="5432"
    )

def buscar_paciente(conn, patient_id, nome, sobrenome):
    """Busca paciente por ID do Doctoralia ou nome"""
    cur = conn.cursor()
    
    # Primeiro tenta pelo nome completo
    nome_completo = f"{nome} {sobrenome}".strip()
    cur.execute("""
        SELECT id FROM pacientes 
        WHERE LOWER(nome) = LOWER(%s) 
        OR (LOWER(nome) LIKE LOWER(%s) AND LOWER(nome) LIKE LOWER(%s))
    """, (nome_completo, f'%{nome}%', f'%{sobrenome}%'))
    
    result = cur.fetchone()
    return result[0] if result else None

def processar_episodios(arquivo_csv):
    """Processa episódios clínicos (prontuários detalhados)"""
    print("🏥 IMPORTANDO EPISÓDIOS CLÍNICOS...")
    print("=" * 60)
    
    try:
        # Ler CSV
        df = pd.read_csv(arquivo_csv, delimiter=';', encoding='utf-8-sig')
        print(f"📋 Total de registros: {len(df)}")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        # Agrupar por episódio
        episodios = {}
        
        for idx, row in df.iterrows():
            episode_id = row['episodeId']
            if episode_id not in episodios:
                episodios[episode_id] = {
                    'patient_id': row['patientId'],
                    'nome': row['first name'],
                    'sobrenome': row['last name'],
                    'data': None,
                    'observacoes': [],
                    'diagnosticos': [],
                    'prescricoes': [],
                    'exame_fisico': [],
                    'procedimentos': []
                }
            
            # Classificar informação por tipo
            titulo = row['title'].lower() if pd.notna(row['title']) else ''
            valor = row['value'] if pd.notna(row['value']) else ''
            data = pd.to_datetime(row['date']).date() if pd.notna(row['date']) else None
            
            if data and not episodios[episode_id]['data']:
                episodios[episode_id]['data'] = data
            
            if 'observa' in titulo:
                episodios[episode_id]['observacoes'].append(valor)
            elif 'diagnóstico' in titulo:
                episodios[episode_id]['diagnosticos'].append(valor)
            elif 'prescri' in titulo:
                episodios[episode_id]['prescricoes'].append(valor)
            elif 'exame físico' in titulo:
                episodios[episode_id]['exame_fisico'].append(valor)
            elif 'procedimento' in titulo:
                episodios[episode_id]['procedimentos'].append(valor)
        
        print(f"\n📊 {len(episodios)} episódios únicos encontrados")
        
        # Importar episódios
        consultas_criadas = 0
        pacientes_nao_encontrados = []
        
        for episode_id, dados in episodios.items():
            # Buscar paciente
            paciente_id = buscar_paciente(conn, dados['patient_id'], dados['nome'], dados['sobrenome'])
            
            if not paciente_id:
                pacientes_nao_encontrados.append(f"{dados['nome']} {dados['sobrenome']}")
                continue
            
            try:
                # Montar texto completo do episódio
                texto_completo = []
                
                if dados['observacoes']:
                    texto_completo.append("=== OBSERVAÇÕES ===")
                    texto_completo.extend(dados['observacoes'])
                    texto_completo.append("")
                
                if dados['exame_fisico']:
                    texto_completo.append("=== EXAME FÍSICO ===")
                    texto_completo.extend(dados['exame_fisico'])
                    texto_completo.append("")
                
                if dados['diagnosticos']:
                    texto_completo.append("=== DIAGNÓSTICOS ===")
                    texto_completo.extend(dados['diagnosticos'])
                    texto_completo.append("")
                
                if dados['prescricoes']:
                    texto_completo.append("=== PRESCRIÇÕES ===")
                    texto_completo.extend(dados['prescricoes'])
                    texto_completo.append("")
                
                if dados['procedimentos']:
                    texto_completo.append("=== PROCEDIMENTOS ===")
                    texto_completo.extend(dados['procedimentos'])
                
                # Criar consulta
                cur.execute("""
                    INSERT INTO consultas (
                        paciente_id, data_consulta, 
                        motivo, observacoes
                    ) VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    paciente_id,
                    dados['data'] or datetime.now().date(),
                    f"Episódio clínico #{episode_id} - " + (dados['diagnosticos'][0] if dados['diagnosticos'] else "Consulta"),
                    '\n'.join(texto_completo)
                ))
                
                consultas_criadas += 1
                
                if consultas_criadas % 50 == 0:
                    print(f"   📝 {consultas_criadas} episódios processados...")
                
            except Exception as e:
                print(f"⚠️  Erro no episódio {episode_id}: {str(e)[:80]}")
                conn.rollback()
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n✅ {consultas_criadas} episódios importados com sucesso!")
        
        if pacientes_nao_encontrados:
            print(f"⚠️  {len(pacientes_nao_encontrados)} pacientes não encontrados")
            for nome in pacientes_nao_encontrados[:5]:
                print(f"   - {nome}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def processar_anexos(arquivo_csv):
    """Processa referências aos anexos (fotos, PDFs)"""
    print("\n📎 PROCESSANDO ANEXOS...")
    print("=" * 60)
    
    try:
        # Ler CSV
        df = pd.read_csv(arquivo_csv, delimiter=';', encoding='utf-8-sig')
        print(f"📋 Total de anexos: {len(df)}")
        
        conn = conectar_db()
        cur = conn.cursor()
        
        # Criar tabela de anexos se não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS anexos_doctoralia (
                id SERIAL PRIMARY KEY,
                patient_id VARCHAR(50),
                episode_id VARCHAR(50),
                nome_arquivo VARCHAR(255),
                tipo_arquivo VARCHAR(50),
                importado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Importar referências
        anexos_importados = 0
        
        for idx, row in df.iterrows():
            try:
                nome_arquivo = row['attachment name']
                tipo = 'PDF' if nome_arquivo.endswith('.pdf') else 'Imagem'
                
                cur.execute("""
                    INSERT INTO anexos_doctoralia (
                        patient_id, episode_id, nome_arquivo, tipo_arquivo
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    str(row['patientId']),
                    str(row['episodeId']),
                    nome_arquivo,
                    tipo
                ))
                
                anexos_importados += 1
                
            except Exception as e:
                print(f"⚠️  Erro no anexo {idx}: {str(e)[:80]}")
                conn.rollback()
                continue
        
        conn.commit()
        
        # Estatísticas
        cur.execute("SELECT tipo_arquivo, COUNT(*) FROM anexos_doctoralia GROUP BY tipo_arquivo")
        tipos = cur.fetchall()
        
        print(f"\n✅ {anexos_importados} anexos registrados!")
        print("\n📊 Tipos de anexos:")
        for tipo, count in tipos:
            print(f"   - {tipo}: {count}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def estatisticas_episodios(arquivo_csv):
    """Mostra estatísticas dos episódios"""
    try:
        df = pd.read_csv(arquivo_csv, delimiter=';', encoding='utf-8-sig')
        
        print("\n📊 ESTATÍSTICAS DOS EPISÓDIOS:")
        print(f"Total de registros: {len(df)}")
        
        # Tipos de informação
        print("\n📋 Tipos de informação:")
        tipos = df['title'].value_counts()
        for tipo, count in tipos.items():
            print(f"  - {tipo}: {count}")
        
        # Episódios únicos
        episodios_unicos = df['episodeId'].nunique()
        pacientes_unicos = df['patientId'].nunique()
        
        print(f"\n📊 Resumo:")
        print(f"  - Episódios únicos: {episodios_unicos}")
        print(f"  - Pacientes únicos: {pacientes_unicos}")
        print(f"  - Média de registros por episódio: {len(df) / episodios_unicos:.1f}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar estatísticas: {str(e)}")

if __name__ == "__main__":
    arquivo_episodios = "/root/.clawdbot/media/inbound/54a85e98-b709-4c1b-8703-9a5ad2f6eaf4.csv"
    arquivo_anexos = "/root/.clawdbot/media/inbound/969d35ff-f644-4998-866a-06717afd5979.csv"
    
    print("🏥 IMPORTADOR DE EPISÓDIOS CLÍNICOS - DR. FELIPE")
    print("=" * 60)
    print("1. Ver estatísticas dos episódios")
    print("2. Importar episódios clínicos")
    print("3. Importar anexos")
    print("4. Importar tudo (episódios + anexos)")
    
    opcao = input("\nEscolha [1-4]: ").strip()
    
    if opcao == "1":
        estatisticas_episodios(arquivo_episodios)
    elif opcao == "2":
        processar_episodios(arquivo_episodios)
    elif opcao == "3":
        processar_anexos(arquivo_anexos)
    elif opcao == "4":
        estatisticas_episodios(arquivo_episodios)
        print("\n" + "=" * 60 + "\n")
        if input("Continuar com importação? [S/n]: ").strip().lower() != 'n':
            processar_episodios(arquivo_episodios)
            processar_anexos(arquivo_anexos)
    else:
        print("❌ Opção inválida!")
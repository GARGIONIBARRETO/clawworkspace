#!/usr/bin/env python3
"""
Gerenciador de upload de exames e anexos
"""

import os
import shutil
from datetime import datetime
import psycopg2

def criar_estrutura_pastas():
    """Cria estrutura de pastas para anexos"""
    base_path = "/root/clawd/anexos"
    subdirs = ["exames_imagem", "laudos", "prescricoes", "outros"]
    
    for subdir in subdirs:
        path = os.path.join(base_path, subdir)
        os.makedirs(path, exist_ok=True)
        
    return base_path

def salvar_anexo(paciente_id, nome_paciente, arquivo_path, tipo="exame"):
    """Salva anexo na pasta do paciente"""
    base_path = criar_estrutura_pastas()
    
    # Criar pasta do paciente
    nome_limpo = "".join(c for c in nome_paciente if c.isalnum() or c in (' ', '-', '_')).strip()
    paciente_folder = f"{paciente_id}_{nome_limpo}"
    paciente_path = os.path.join(base_path, paciente_folder)
    os.makedirs(paciente_path, exist_ok=True)
    
    # Copiar arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(arquivo_path)
    nome_final = f"{timestamp}_{tipo}_{filename}"
    destino = os.path.join(paciente_path, nome_final)
    
    shutil.copy2(arquivo_path, destino)
    
    # Registrar no banco
    try:
        conn = psycopg2.connect(
            dbname="clinica_dr_felipe",
            user="clinica_admin",
            password="clinica2026!",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        
        # Criar tabela de anexos se não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS anexos (
                id SERIAL PRIMARY KEY,
                paciente_id INTEGER REFERENCES pacientes(id),
                tipo VARCHAR(50),
                nome_arquivo VARCHAR(255),
                caminho_arquivo TEXT,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                descricao TEXT
            )
        """)
        
        # Inserir registro
        cur.execute("""
            INSERT INTO anexos (paciente_id, tipo, nome_arquivo, caminho_arquivo)
            VALUES (%s, %s, %s, %s)
        """, (paciente_id, tipo, nome_final, destino))
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao registrar no banco: {e}")
        
    return destino
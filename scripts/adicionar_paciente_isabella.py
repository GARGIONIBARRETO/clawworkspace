#!/usr/bin/env python3
"""
Script para adicionar a paciente Isabella e seus exames no banco de dados
"""

import os
import sys
import psycopg2
import json
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append('/root/clawd')

# Configurações do banco local
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'clinica_dr_felipe',
    'user': 'clinica_admin',
    'password': 'clinica2026!'
}

def conectar_banco():
    """Conecta ao banco PostgreSQL local"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def adicionar_paciente():
    """Adiciona a paciente Isabella no banco"""
    conn = conectar_banco()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        # Verificar se paciente já existe
        cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", ('47690246818',))
        paciente = cursor.fetchone()
        
        if paciente:
            print(f"✅ Paciente já existe com ID: {paciente[0]}")
            return paciente[0]
        
        # Inserir nova paciente
        cursor.execute("""
            INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, email, endereco)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            'Isabella Fernanda Munhoz Soares',
            '47690246818',
            '1998-07-12',
            '',
            '',
            ''
        ))
        
        paciente_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Paciente criada com ID: {paciente_id}")
        return paciente_id
        
    except Exception as e:
        print(f"❌ Erro ao adicionar paciente: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def adicionar_exame(paciente_id):
    """Adiciona o exame laboratorial da paciente"""
    conn = conectar_banco()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Dados dos exames (principais alterações)
    parametros = {
        "hemograma": {
            "eritrocitos": {"valor": 4.28, "unidade": "10^6/µL", "referencia": "3,80-4,80", "status": "normal"},
            "hemoglobina": {"valor": 13.1, "unidade": "g/dL", "referencia": "12,0-15,0", "status": "normal"},
            "hematocrito": {"valor": 38.4, "unidade": "%", "referencia": "36,0-46,0", "status": "normal"},
            "leucocitos": {"valor": 4980, "unidade": "/µL", "referencia": "4.000-10.000", "status": "normal"},
            "plaquetas": {"valor": 237000, "unidade": "/µL", "referencia": "150.000-450.000", "status": "normal"}
        },
        "bioquimica": {
            "glicose": {"valor": 89, "unidade": "mg/dL", "referencia": "70-99", "status": "normal"},
            "hba1c": {"valor": 5.2, "unidade": "%", "referencia": "<5,7", "status": "normal"},
            "ureia": {"valor": 27, "unidade": "mg/dL", "referencia": "19-49", "status": "normal"},
            "creatinina": {"valor": 1.03, "unidade": "mg/dL", "referencia": "0,50-1,10", "status": "limite_superior"},
            "egfr": {"valor": 76, "unidade": "mL/min/1,73m²", "referencia": ">90", "status": "reduzida"}
        },
        "lipidograma": {
            "colesterol_total": {"valor": 175, "unidade": "mg/dL", "referencia": "<190", "status": "normal"},
            "ldl": {"valor": 112, "unidade": "mg/dL", "referencia": "<130", "status": "normal"},
            "hdl": {"valor": 46, "unidade": "mg/dL", "referencia": ">40", "status": "normal"},
            "triglicerides": {"valor": 76, "unidade": "mg/dL", "referencia": "<150", "status": "normal"}
        },
        "vitaminas": {
            "acido_folico": {"valor": 5.37, "unidade": "ng/mL", "referencia": ">5,38", "status": "limitrofe"},
            "vitamina_b12": {"valor": 661, "unidade": "pg/mL", "referencia": "223-672", "status": "normal"},
            "vitamina_d": {"valor": 50, "unidade": "ng/mL", "referencia": ">30", "status": "adequada"}
        },
        "hormonios": {
            "tsh": {"valor": 2.0, "unidade": "µUI/mL", "referencia": "0,40-4,30", "status": "normal"},
            "t4_livre": {"valor": 1.61, "unidade": "ng/dL", "referencia": "0,89-1,76", "status": "normal"},
            "testosterona_livre": {"valor": 0.16, "unidade": "ng/dL", "referencia": "0,18-1,68", "status": "baixa"}
        },
        "alteracoes": [
            "Ácido fólico limítrofe (5,37 ng/mL)",
            "Transferrina baixa (212 mg/dL)",
            "Testosterona livre baixa (0,16 ng/dL)", 
            "Cloro discretamente elevado (109 mmol/L)",
            "Lipase no limite superior (54 U/L)"
        ]
    }
    
    try:
        cursor.execute("""
            INSERT INTO exames_laboratoriais (paciente_id, data_exame, laboratorio, tipo_exame, parametros)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            paciente_id,
            '2026-02-11',
            'DASA',
            'Check-up Completo',
            json.dumps(parametros, ensure_ascii=False, indent=2)
        ))
        
        conn.commit()
        print("✅ Exame adicionado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar exame: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal"""
    print("🏥 Adicionando paciente Isabella Munhoz Soares")
    print("=" * 50)
    
    # Adicionar paciente
    paciente_id = adicionar_paciente()
    if not paciente_id:
        print("❌ Não foi possível adicionar a paciente")
        return
    
    # Adicionar exame
    if adicionar_exame(paciente_id):
        print("✅ Dados inseridos com sucesso!")
        print(f"📋 Arquivo de acompanhamento: /root/clawd/pacientes/Isabella_Munhoz_Soares_acompanhamento.md")
    else:
        print("❌ Erro ao inserir exames")

if __name__ == "__main__":
    main()
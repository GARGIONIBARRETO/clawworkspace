#!/usr/bin/env python3
"""
Gerador de Templates CSV - Standalone
Não precisa de conexão com banco
"""

import pandas as pd
import os
from datetime import date

def gerar_templates():
    """Gera todos os templates CSV"""
    
    # Cria diretório
    os.makedirs("/root/clawd/templates", exist_ok=True)
    
    # Template de pacientes
    pacientes_data = {
        'nome': ['João Silva Santos', 'Maria Oliveira Costa', 'Pedro Ferreira Lima'],
        'cpf': ['12345678901', '98765432100', '45612378945'],
        'data_nascimento': ['1980-05-15', '1975-12-03', '1990-08-22'],
        'telefone': ['(11) 99999-9999', '(11) 88888-8888', '(11) 77777-7777'],
        'email': ['joao@email.com', 'maria@email.com', 'pedro@email.com'],
        'endereco': ['Rua das Flores, 123 - Vila Madalena', 'Av Paulista, 456 - Bela Vista', 'Rua Oscar Freire, 789 - Jardins'],
        'observacoes': ['Paciente regular - histórico de lombalgia', 'Primeira consulta - dor cervical', 'Retorno pós-operatório']
    }
    
    df_pacientes = pd.DataFrame(pacientes_data)
    df_pacientes.to_csv("/root/clawd/templates/pacientes_template.csv", index=False)
    
    # Template de bioimpedância  
    bio_data = {
        'paciente_id': [1, 1, 1, 2, 2, 3],
        'data_medicao': ['2026-01-15', '2026-02-15', '2026-03-01', '2026-01-20', '2026-02-20', '2026-01-25'],
        'peso': [75.5, 74.8, 74.2, 68.2, 67.8, 82.1],
        'altura': [175, 175, 175, 162, 162, 180],
        'imc': [24.6, 24.4, 24.2, 26.0, 25.8, 25.3],
        'gordura_corporal': [15.2, 14.8, 14.5, 22.3, 21.8, 18.7],
        'massa_muscular': [35.8, 36.1, 36.4, 28.5, 28.8, 42.2],
        'massa_ossea': [3.2, 3.2, 3.2, 2.8, 2.8, 3.6],
        'agua_corporal': [55.8, 56.2, 56.5, 52.1, 52.6, 57.2],
        'metabolismo_basal': [1650, 1655, 1660, 1320, 1325, 1890],
        'gordura_visceral': [8, 7, 7, 12, 11, 9],
        'observacoes': ['Primeira medição - início do tratamento', 'Evolução positiva após 1 mês', 'Excelente progresso', 'Primeira avaliação', 'Melhora na composição', 'Atleta amador']
    }
    
    df_bio = pd.DataFrame(bio_data)
    df_bio.to_csv("/root/clawd/templates/bioimpedancia_template.csv", index=False)
    
    # Template de exames laboratoriais
    exames_data = {
        'paciente_id': [1, 1, 1, 2, 2, 3],
        'data_exame': ['2026-01-15', '2026-02-15', '2026-03-01', '2026-01-18', '2026-02-18', '2026-01-22'],
        'laboratorio': ['Lab Central', 'Lab Central', 'Lab Central', 'Fleury', 'Fleury', 'Delboni'],
        'tipo_exame': ['Perfil Lipídico', 'Hemograma Completo', 'Perfil Metabólico', 'Glicemia e HbA1c', 'Vitamina D', 'Check-up Executivo'],
        'parametros': [
            '{"colesterol_total": 180, "hdl": 45, "ldl": 120, "triglicerideos": 150, "colesterol_nao_hdl": 135}',
            '{"hemoglobina": 14.2, "hematocrito": 42, "leucocitos": 7200, "plaquetas": 285000, "vhs": 12}',
            '{"glicemia_jejum": 85, "insulina": 8.5, "homa_ir": 1.8, "creatinina": 0.9, "ureia": 35}',
            '{"glicemia_jejum": 95, "hba1c": 5.8, "frutosamina": 245}',
            '{"vitamina_d": 28, "pth": 45, "calcio": 9.8, "fosforo": 3.2}',
            '{"colesterol_total": 160, "hdl": 55, "triglicerideos": 80, "glicemia": 82, "creatinina": 0.8}'
        ],
        'arquivo_pdf': ['perfil_lipidico_joao_jan26.pdf', '', 'perfil_metabolico_joao_mar26.pdf', 'glicemia_maria_jan26.pdf', '', ''],
        'observacoes': ['Colesterol limítrofe - orientar dieta', 'Hemograma normal', 'Resistência insulínica leve', 'Pré-diabetes - atenção', 'Vitamina D insuficiente', 'Exames excelentes']
    }
    
    df_exames = pd.DataFrame(exames_data)
    df_exames.to_csv("/root/clawd/templates/exames_template.csv", index=False)
    
    print("✅ Templates CSV gerados com sucesso!")
    print("📁 Localização: /root/clawd/templates/")
    print("📋 Arquivos criados:")
    print("  - pacientes_template.csv")
    print("  - bioimpedancia_template.csv") 
    print("  - exames_template.csv")

if __name__ == "__main__":
    gerar_templates()
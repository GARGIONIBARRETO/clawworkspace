#!/usr/bin/env python3
"""
Sistema de Importação de Dados - Dr. Felipe
Importa exames de CSV/Excel e bioimpedância
"""

import pandas as pd
import json
from datetime import datetime, date
from pacientes_manager import PacientesManager
import os

class ImportadorDados:
    def __init__(self):
        self.manager = PacientesManager()
    
    def importar_pacientes_csv(self, arquivo_csv: str) -> int:
        """Importa lista de pacientes de CSV"""
        
        print(f"📥 Importando pacientes de: {arquivo_csv}")
        
        try:
            df = pd.read_csv(arquivo_csv)
            
            # Colunas esperadas: nome, cpf, data_nascimento, telefone, email, endereco
            colunas_obrigatorias = ['nome']
            
            for col in colunas_obrigatorias:
                if col not in df.columns:
                    print(f"❌ Coluna obrigatória '{col}' não encontrada")
                    return 0
            
            importados = 0
            erros = 0
            
            for _, row in df.iterrows():
                try:
                    # Converte data se existir
                    data_nascimento = None
                    if 'data_nascimento' in row and pd.notna(row['data_nascimento']):
                        data_nascimento = pd.to_datetime(row['data_nascimento']).date()
                    
                    paciente_id = self.manager.adicionar_paciente(
                        nome=str(row['nome']),
                        cpf=str(row['cpf']) if 'cpf' in row and pd.notna(row['cpf']) else None,
                        data_nascimento=data_nascimento,
                        telefone=str(row['telefone']) if 'telefone' in row and pd.notna(row['telefone']) else None,
                        email=str(row['email']) if 'email' in row and pd.notna(row['email']) else None,
                        endereco=str(row['endereco']) if 'endereco' in row and pd.notna(row['endereco']) else None,
                        observacoes=str(row['observacoes']) if 'observacoes' in row and pd.notna(row['observacoes']) else None
                    )
                    
                    if paciente_id:
                        importados += 1
                    else:
                        erros += 1
                
                except Exception as e:
                    print(f"❌ Erro ao importar linha: {e}")
                    erros += 1
            
            print(f"✅ Importação concluída: {importados} pacientes, {erros} erros")
            return importados
        
        except Exception as e:
            print(f"❌ Erro na importação: {e}")
            return 0
    
    def importar_bioimpedancia_csv(self, arquivo_csv: str) -> int:
        """Importa bioimpedância de CSV"""
        
        print(f"📥 Importando bioimpedância de: {arquivo_csv}")
        
        try:
            df = pd.read_csv(arquivo_csv)
            
            # Colunas esperadas
            cols_obrigatorias = ['paciente_id', 'data_medicao']
            cols_opcionais = ['peso', 'altura', 'imc', 'gordura_corporal', 'massa_muscular', 
                            'massa_ossea', 'agua_corporal', 'metabolismo_basal', 'gordura_visceral']
            
            for col in cols_obrigatorias:
                if col not in df.columns:
                    print(f"❌ Coluna obrigatória '{col}' não encontrada")
                    return 0
            
            importados = 0
            erros = 0
            
            for _, row in df.iterrows():
                try:
                    # Converte data
                    data_medicao = pd.to_datetime(row['data_medicao']).date()
                    
                    # Prepara dados
                    dados_bio = {
                        'paciente_id': int(row['paciente_id']),
                        'data_medicao': data_medicao
                    }
                    
                    # Adiciona colunas opcionais se existirem
                    for col in cols_opcionais:
                        if col in row and pd.notna(row[col]):
                            if col in ['metabolismo_basal', 'gordura_visceral']:
                                dados_bio[col] = int(row[col])
                            else:
                                dados_bio[col] = float(row[col])
                    
                    if 'observacoes' in row and pd.notna(row['observacoes']):
                        dados_bio['observacoes'] = str(row['observacoes'])
                    
                    bio_id = self.manager.adicionar_bioimpedancia(**dados_bio)
                    
                    if bio_id:
                        importados += 1
                    else:
                        erros += 1
                
                except Exception as e:
                    print(f"❌ Erro ao importar bioimpedância: {e}")
                    erros += 1
            
            print(f"✅ Bioimpedância importada: {importados} registros, {erros} erros")
            return importados
        
        except Exception as e:
            print(f"❌ Erro na importação: {e}")
            return 0
    
    def importar_exames_laboratoriais_csv(self, arquivo_csv: str) -> int:
        """Importa exames laboratoriais de CSV"""
        
        print(f"📥 Importando exames de: {arquivo_csv}")
        
        try:
            df = pd.read_csv(arquivo_csv)
            
            # Colunas obrigatórias
            cols_obrigatorias = ['paciente_id', 'data_exame', 'tipo_exame', 'parametros']
            
            for col in cols_obrigatorias:
                if col not in df.columns:
                    print(f"❌ Coluna obrigatória '{col}' não encontrada")
                    return 0
            
            importados = 0
            erros = 0
            
            for _, row in df.iterrows():
                try:
                    # Converte data
                    data_exame = pd.to_datetime(row['data_exame']).date()
                    
                    # Processa parâmetros (deve estar em formato JSON)
                    parametros = {}
                    if pd.notna(row['parametros']):
                        try:
                            parametros = json.loads(str(row['parametros']))
                        except:
                            # Se não é JSON válido, tenta como string simples
                            parametros = {"resultado": str(row['parametros'])}
                    
                    exame_id = self.manager.adicionar_exame_laboratorial(
                        paciente_id=int(row['paciente_id']),
                        data_exame=data_exame,
                        laboratorio=str(row['laboratorio']) if 'laboratorio' in row and pd.notna(row['laboratorio']) else "Não informado",
                        tipo_exame=str(row['tipo_exame']),
                        parametros=parametros,
                        arquivo_pdf=str(row['arquivo_pdf']) if 'arquivo_pdf' in row and pd.notna(row['arquivo_pdf']) else None,
                        observacoes=str(row['observacoes']) if 'observacoes' in row and pd.notna(row['observacoes']) else None
                    )
                    
                    if exame_id:
                        importados += 1
                    else:
                        erros += 1
                
                except Exception as e:
                    print(f"❌ Erro ao importar exame: {e}")
                    erros += 1
            
            print(f"✅ Exames importados: {importados} registros, {erros} erros")
            return importados
        
        except Exception as e:
            print(f"❌ Erro na importação: {e}")
            return 0
    
    def gerar_template_pacientes_csv(self, arquivo: str = "/root/clawd/templates/pacientes_template.csv"):
        """Gera template CSV para importação de pacientes"""
        
        template_data = {
            'nome': ['João da Silva', 'Maria Santos', 'Pedro Costa'],
            'cpf': ['12345678901', '98765432100', '45612378945'],
            'data_nascimento': ['1980-05-15', '1975-12-03', '1990-08-22'],
            'telefone': ['(11) 99999-9999', '(11) 88888-8888', '(11) 77777-7777'],
            'email': ['joao@email.com', 'maria@email.com', 'pedro@email.com'],
            'endereco': ['Rua A, 123', 'Av B, 456', 'Rua C, 789'],
            'observacoes': ['Paciente regular', 'Primeira consulta', 'Retorno']
        }
        
        df = pd.DataFrame(template_data)
        
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        
        df.to_csv(arquivo, index=False)
        print(f"📋 Template de pacientes salvo em: {arquivo}")
    
    def gerar_template_bioimpedancia_csv(self, arquivo: str = "/root/clawd/templates/bioimpedancia_template.csv"):
        """Gera template CSV para bioimpedância"""
        
        template_data = {
            'paciente_id': [1, 1, 2],
            'data_medicao': ['2026-01-15', '2026-02-15', '2026-01-20'],
            'peso': [75.5, 74.8, 68.2],
            'altura': [175, 175, 162],
            'imc': [24.6, 24.4, 26.0],
            'gordura_corporal': [15.2, 14.8, 22.3],
            'massa_muscular': [35.8, 36.1, 28.5],
            'massa_ossea': [3.2, 3.2, 2.8],
            'agua_corporal': [55.8, 56.2, 52.1],
            'metabolismo_basal': [1650, 1655, 1320],
            'gordura_visceral': [8, 7, 12],
            'observacoes': ['Primeira medição', 'Evolução positiva', 'Início tratamento']
        }
        
        df = pd.DataFrame(template_data)
        
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        df.to_csv(arquivo, index=False)
        print(f"📋 Template de bioimpedância salvo em: {arquivo}")
    
    def gerar_template_exames_csv(self, arquivo: str = "/root/clawd/templates/exames_template.csv"):
        """Gera template CSV para exames laboratoriais"""
        
        template_data = {
            'paciente_id': [1, 1, 2],
            'data_exame': ['2026-01-15', '2026-02-15', '2026-01-18'],
            'laboratorio': ['Lab Central', 'Lab Central', 'Fleury'],
            'tipo_exame': ['Perfil Lipídico', 'Hemograma', 'Glicemia'],
            'parametros': [
                '{"colesterol_total": 180, "hdl": 45, "ldl": 120, "triglicerideos": 150}',
                '{"hemoglobina": 14.2, "hematocritos": 42, "leucocitos": 7200}',
                '{"glicemia_jejum": 85, "hba1c": 5.4}'
            ],
            'arquivo_pdf': ['exame1.pdf', '', 'glicemia_joao.pdf'],
            'observacoes': ['Dentro da normalidade', 'Leve anemia', 'Excelente controle glicêmico']
        }
        
        df = pd.DataFrame(template_data)
        
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        df.to_csv(arquivo, index=False)
        print(f"📋 Template de exames salvo em: {arquivo}")

# Exemplo de uso
if __name__ == "__main__":
    importador = ImportadorDados()
    
    # Gera templates
    importador.gerar_template_pacientes_csv()
    importador.gerar_template_bioimpedancia_csv()
    importador.gerar_template_exames_csv()
    
    print("✅ Templates gerados! Edite os arquivos em /root/clawd/templates/ e importe com:")
    print("python3 import_dados.py")
    
    # Exemplo de importação (descomentado quando necessário)
    # importador.importar_pacientes_csv("/root/clawd/templates/pacientes_template.csv")
    # importador.importar_bioimpedancia_csv("/root/clawd/templates/bioimpedancia_template.csv")
    # importador.importar_exames_laboratoriais_csv("/root/clawd/templates/exames_template.csv")
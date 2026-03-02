#!/usr/bin/env python3
"""
Sistema completo de importação de dados da clínica
Importa pacientes, consultas, episódios clínicos e anexos
"""

import os
import sys
import json
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime
import uuid

# Adicionar path dos scripts
sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

class ImportadorCompleto:
    def __init__(self):
        self.base_path = Path('/root/clawd/importacao')
        self.anexos_path = Path('/root/clawd/anexos_pacientes')
        self.anexos_path.mkdir(exist_ok=True)
        
        # Conectar ao banco local
        self.db = PostgreSQLLocal()
        if not self.db:
            print("❌ Erro: Não foi possível conectar ao PostgreSQL")
            sys.exit(1)
        
        # Garantir que tabelas existem
        self.db.create_tables()
        
        self.log = []
    
    def log_acao(self, mensagem):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}"
        self.log.append(log_entry)
        print(log_entry)
    
    def importar_pacientes(self):
        """Importa dados dos pacientes"""
        pasta_pacientes = self.base_path / 'pacientes'
        arquivos_csv = list(pasta_pacientes.glob('*.csv'))
        
        if not arquivos_csv:
            self.log_acao("⚠️  Nenhum arquivo CSV encontrado na pasta pacientes/")
            return
        
        total_importados = 0
        
        for arquivo in arquivos_csv:
            self.log_acao(f"📄 Processando: {arquivo.name}")
            
            try:
                df = pd.read_csv(arquivo)
                
                # Validar colunas obrigatórias
                colunas_obrigatorias = ['nome', 'cpf']
                for col in colunas_obrigatorias:
                    if col not in df.columns:
                        self.log_acao(f"❌ Erro: Coluna '{col}' não encontrada em {arquivo.name}")
                        continue
                
                # Processar cada linha
                for index, row in df.iterrows():
                    try:
                        dados_paciente = {
                            'nome': row['nome'],
                            'cpf': str(row['cpf']).replace('.', '').replace('-', ''),
                            'rg': str(row.get('rg', '')),
                            'telefone': str(row.get('telefone', '')),
                            'email': str(row.get('email', '')),
                            'endereco': str(row.get('endereco', '')),
                            'data_nascimento': row.get('data_nascimento'),
                            'convenio': str(row.get('convenio', 'Particular')),
                            'created_at': datetime.now().isoformat()
                        }
                        
                        # Inserir no banco
                        insert_sql = """
                        INSERT INTO pacientes (nome, cpf, rg, telefone, email, endereco, data_nascimento, convenio, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        self.db.cursor.execute(insert_sql, (
                            dados_paciente['nome'],
                            dados_paciente['cpf'],
                            dados_paciente['rg'],
                            dados_paciente['telefone'],
                            dados_paciente['email'],
                            dados_paciente['endereco'],
                            dados_paciente['data_nascimento'],
                            dados_paciente['convenio'],
                            dados_paciente['created_at']
                        ))
                        self.db.connection.commit()
                        
                        total_importados += 1
                        self.log_acao(f"✅ Paciente importado: {dados_paciente['nome']} (CPF: {dados_paciente['cpf']})")
                        
                    except Exception as e:
                        self.log_acao(f"❌ Erro ao importar linha {index+1}: {str(e)}")
                        
            except Exception as e:
                self.log_acao(f"❌ Erro ao processar {arquivo.name}: {str(e)}")
        
        self.log_acao(f"📊 Total de pacientes importados: {total_importados}")
    
    def importar_consultas(self):
        """Importa histórico de consultas"""
        pasta_consultas = self.base_path / 'consultas'
        arquivos_csv = list(pasta_consultas.glob('*.csv'))
        
        if not arquivos_csv:
            self.log_acao("⚠️  Nenhum arquivo CSV encontrado na pasta consultas/")
            return
        
        total_importadas = 0
        
        for arquivo in arquivos_csv:
            self.log_acao(f"📄 Processando consultas: {arquivo.name}")
            
            try:
                df = pd.read_csv(arquivo)
                
                # Validar colunas
                colunas_obrigatorias = ['cpf_paciente', 'data_consulta']
                for col in colunas_obrigatorias:
                    if col not in df.columns:
                        self.log_acao(f"❌ Erro: Coluna '{col}' não encontrada em {arquivo.name}")
                        continue
                
                for index, row in df.iterrows():
                    try:
                        cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
                        
                        # Verificar se paciente existe
                        self.db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
                        paciente = self.db.cursor.fetchone()
                        
                        if not paciente:
                            self.log_acao(f"⚠️  Paciente com CPF {cpf} não encontrado - pulando consulta")
                            continue
                        
                        # Inserir consulta
                        insert_sql = """
                        INSERT INTO consultas (paciente_id, data_consulta, medico, motivo, observacoes, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        self.db.cursor.execute(insert_sql, (
                            paciente[0],
                            row['data_consulta'],
                            str(row.get('medico', 'Dr. Felipe')),
                            str(row.get('motivo', '')),
                            str(row.get('observacoes', '')),
                            datetime.now().isoformat()
                        ))
                        self.db.connection.commit()
                        
                        total_importadas += 1
                        self.log_acao(f"✅ Consulta importada para paciente CPF: {cpf}")
                        
                    except Exception as e:
                        self.log_acao(f"❌ Erro ao importar consulta linha {index+1}: {str(e)}")
                        
            except Exception as e:
                self.log_acao(f"❌ Erro ao processar {arquivo.name}: {str(e)}")
        
        self.log_acao(f"📊 Total de consultas importadas: {total_importadas}")
    
    def importar_episodios_clinicos(self):
        """Importa episódios clínicos detalhados"""
        pasta_episodios = self.base_path / 'episodios_clinicos'
        arquivos_csv = list(pasta_episodios.glob('*.csv'))
        
        if not arquivos_csv:
            self.log_acao("⚠️  Nenhum arquivo CSV encontrado na pasta episodios_clinicos/")
            return
        
        total_importados = 0
        
        for arquivo in arquivos_csv:
            self.log_acao(f"📄 Processando episódios: {arquivo.name}")
            
            try:
                df = pd.read_csv(arquivo)
                
                for index, row in df.iterrows():
                    try:
                        cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
                        
                        # Verificar se paciente existe
                        self.db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
                        paciente = self.db.cursor.fetchone()
                        
                        if not paciente:
                            continue
                        
                        # Inserir como consulta detalhada
                        observacoes = f"DESCRIÇÃO: {row.get('descricao', '')}\\n\\nDIAGNÓSTICO: {row.get('diagnostico', '')}\\n\\nTRATAMENTO: {row.get('tratamento', '')}"
                        
                        insert_sql = """
                        INSERT INTO consultas (paciente_id, data_consulta, motivo, observacoes, medico, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        self.db.cursor.execute(insert_sql, (
                            paciente[0],
                            row.get('data_episodio', datetime.now().strftime('%Y-%m-%d')),
                            str(row.get('tipo_episodio', 'Episódio clínico')),
                            observacoes,
                            'Dr. Felipe',
                            datetime.now().isoformat()
                        ))
                        self.db.connection.commit()
                        
                        total_importados += 1
                        self.log_acao(f"✅ Episódio clínico importado para CPF: {cpf}")
                        
                    except Exception as e:
                        self.log_acao(f"❌ Erro ao importar episódio linha {index+1}: {str(e)}")
                        
            except Exception as e:
                self.log_acao(f"❌ Erro ao processar {arquivo.name}: {str(e)}")
        
        self.log_acao(f"📊 Total de episódios importados: {total_importados}")
    
    def organizar_anexos(self):
        """Organiza anexos por paciente"""
        pasta_anexos = self.base_path / 'anexos'
        
        if not pasta_anexos.exists():
            self.log_acao("⚠️  Pasta de anexos não encontrada")
            return
        
        total_organizados = 0
        
        # Processar cada subpasta de anexos
        for tipo_anexo in ['exames_imagem', 'fotos_exames']:
            pasta_tipo = pasta_anexos / tipo_anexo
            
            if not pasta_tipo.exists():
                continue
            
            self.log_acao(f"📁 Organizando {tipo_anexo}...")
            
            # Buscar todas as pastas organizadas por CPF
            for pasta_cpf in pasta_tipo.iterdir():
                if pasta_cpf.is_dir():
                    cpf = pasta_cpf.name
                    
                    # Verificar se paciente existe
                    self.db.cursor.execute("SELECT id, nome FROM pacientes WHERE cpf = %s", (cpf,))
                    paciente = self.db.cursor.fetchone()
                    
                    if not paciente:
                        self.log_acao(f"⚠️  Paciente com CPF {cpf} não encontrado - pulando anexos")
                        continue
                    
                    paciente_id = paciente[0]
                    paciente_nome = paciente[1]
                    
                    # Criar pasta de destino
                    pasta_destino = self.anexos_path / f"paciente_{paciente_id}_{cpf}" / tipo_anexo
                    pasta_destino.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar todos os arquivos
                    arquivos_copiados = 0
                    for arquivo in pasta_cpf.iterdir():
                        if arquivo.is_file():
                            destino = pasta_destino / arquivo.name
                            shutil.copy2(arquivo, destino)
                            arquivos_copiados += 1
                    
                    if arquivos_copiados > 0:
                        self.log_acao(f"✅ {arquivos_copiados} arquivos organizados para {paciente_nome} (CPF: {cpf})")
                        total_organizados += arquivos_copiados
        
        self.log_acao(f"📊 Total de anexos organizados: {total_organizados}")
    
    def executar_importacao_completa(self):
        """Executa todo o processo de importação"""
        self.log_acao("🚀 Iniciando importação completa...")
        
        # 1. Importar pacientes primeiro
        self.log_acao("\\n=== IMPORTANDO PACIENTES ===")
        self.importar_pacientes()
        
        # 2. Importar consultas
        self.log_acao("\\n=== IMPORTANDO CONSULTAS ===")
        self.importar_consultas()
        
        # 3. Importar episódios clínicos
        self.log_acao("\\n=== IMPORTANDO EPISÓDIOS CLÍNICOS ===")
        self.importar_episodios_clinicos()
        
        # 4. Organizar anexos
        self.log_acao("\\n=== ORGANIZANDO ANEXOS ===")
        self.organizar_anexos()
        
        # 5. Salvar log
        self.salvar_log()
        
        # 6. Fechar conexão
        self.db.close()
        
        self.log_acao("\\n✅ IMPORTAÇÃO COMPLETA FINALIZADA!")
    
    def salvar_log(self):
        """Salva log da importação"""
        log_file = f"/root/clawd/logs/importacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("/root/clawd/logs", exist_ok=True)
        
        with open(log_file, 'w') as f:
            f.write("\\n".join(self.log))
        
        self.log_acao(f"📝 Log salvo em: {log_file}")

def main():
    print("🏥 Sistema de Importação Completa - Clínica Dr. Felipe")
    print("=" * 50)
    
    importador = ImportadorCompleto()
    
    if len(sys.argv) > 1:
        tipo = sys.argv[1].lower()
        
        if tipo == 'pacientes':
            importador.importar_pacientes()
        elif tipo == 'consultas':
            importador.importar_consultas()
        elif tipo == 'episodios':
            importador.importar_episodios_clinicos()
        elif tipo == 'anexos':
            importador.organizar_anexos()
        else:
            print("Tipo inválido. Use: pacientes, consultas, episodios, anexos")
    else:
        # Importação completa
        importador.executar_importacao_completa()

if __name__ == "__main__":
    main()
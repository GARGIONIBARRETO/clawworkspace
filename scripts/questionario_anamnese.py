#!/usr/bin/env python3
"""
Módulo de Integração de Questionário de Anamnese
Permite receber dados de questionários e integrar ao prontuário
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, Optional, List
from db_manager import DatabaseManager

class QuestionarioAnamnese:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        
    def criar_tabela_anamnese(self):
        """Cria tabela para armazenar respostas de anamnese"""
        
        sql = """
        CREATE TABLE IF NOT EXISTS anamnese (
            id SERIAL PRIMARY KEY,
            paciente_id INTEGER REFERENCES pacientes(id),
            data_preenchimento DATE DEFAULT CURRENT_DATE,
            hora_preenchimento TIME DEFAULT CURRENT_TIME,
            tipo_questionario VARCHAR(50) DEFAULT 'anamnese_geral',
            
            -- Queixa principal e HDA
            queixa_principal TEXT,
            historia_doenca_atual TEXT,
            tempo_sintomas VARCHAR(100),
            
            -- Revisão de sistemas
            sintomas_gerais TEXT,
            sintomas_neurologicos TEXT,
            sintomas_cardiovasculares TEXT,
            sintomas_respiratorios TEXT,
            sintomas_gastrointestinais TEXT,
            sintomas_genitourinarios TEXT,
            sintomas_musculoesqueleticos TEXT,
            
            -- Antecedentes
            antecedentes_pessoais TEXT,
            antecedentes_familiares TEXT,
            antecedentes_cirurgicos TEXT,
            
            -- Medicações
            medicacoes_atuais TEXT,
            alergias TEXT,
            
            -- Hábitos
            tabagismo VARCHAR(100),
            etilismo VARCHAR(100),
            atividade_fisica VARCHAR(100),
            sono_qualidade VARCHAR(50),
            
            -- Dados adicionais JSON
            dados_extras JSON,
            
            -- Controle
            status VARCHAR(20) DEFAULT 'pendente', -- pendente, revisado, integrado
            revisado_por VARCHAR(100),
            data_revisao TIMESTAMP,
            observacoes_revisao TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_anamnese_paciente ON anamnese(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_anamnese_data ON anamnese(data_preenchimento);
        CREATE INDEX IF NOT EXISTS idx_anamnese_status ON anamnese(status);
        """
        
        try:
            self.db.cursor.execute(sql)
            self.db.connection.commit()
            logging.info("✅ Tabela de anamnese criada/verificada")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao criar tabela anamnese: {e}")
            return False
    
    def importar_questionario_json(self, dados_json: Dict, paciente_id: int) -> Optional[int]:
        """
        Importa dados de questionário em formato JSON
        
        Estrutura esperada do JSON:
        {
            "queixa_principal": "texto",
            "historia_doenca_atual": "texto",
            "sintomas": {
                "gerais": "texto",
                "neurologicos": "texto",
                ...
            },
            "antecedentes": {...},
            "medicacoes": [...],
            "habitos": {...}
        }
        """
        
        try:
            sql = """
            INSERT INTO anamnese (
                paciente_id,
                queixa_principal,
                historia_doenca_atual,
                tempo_sintomas,
                sintomas_gerais,
                sintomas_neurologicos,
                sintomas_cardiovasculares,
                sintomas_respiratorios,
                sintomas_gastrointestinais,
                sintomas_genitourinarios,
                sintomas_musculoesqueleticos,
                antecedentes_pessoais,
                antecedentes_familiares,
                antecedentes_cirurgicos,
                medicacoes_atuais,
                alergias,
                tabagismo,
                etilismo,
                atividade_fisica,
                sono_qualidade,
                dados_extras
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            # Extrai sintomas
            sintomas = dados_json.get('sintomas', {})
            antecedentes = dados_json.get('antecedentes', {})
            habitos = dados_json.get('habitos', {})
            
            # Processa medicações (pode vir como lista ou texto)
            medicacoes = dados_json.get('medicacoes', '')
            if isinstance(medicacoes, list):
                medicacoes = '\n'.join(medicacoes)
            
            valores = (
                paciente_id,
                dados_json.get('queixa_principal'),
                dados_json.get('historia_doenca_atual'),
                dados_json.get('tempo_sintomas'),
                sintomas.get('gerais'),
                sintomas.get('neurologicos'),
                sintomas.get('cardiovasculares'),
                sintomas.get('respiratorios'),
                sintomas.get('gastrointestinais'),
                sintomas.get('genitourinarios'),
                sintomas.get('musculoesqueleticos'),
                antecedentes.get('pessoais'),
                antecedentes.get('familiares'),
                antecedentes.get('cirurgicos'),
                medicacoes,
                dados_json.get('alergias'),
                habitos.get('tabagismo'),
                habitos.get('etilismo'),
                habitos.get('atividade_fisica'),
                habitos.get('sono_qualidade'),
                json.dumps(dados_json.get('dados_extras', {}))
            )
            
            self.db.cursor.execute(sql, valores)
            anamnese_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            
            logging.info(f"✅ Anamnese importada com ID: {anamnese_id}")
            return anamnese_id
            
        except Exception as e:
            logging.error(f"❌ Erro ao importar anamnese: {e}")
            self.db.connection.rollback()
            return None
    
    def processar_formulario_web(self, form_data: Dict) -> Optional[int]:
        """
        Processa dados de formulário web (ex: TypeForm, Google Forms)
        Converte para formato padrão e importa
        """
        
        # Mapeia campos do formulário para estrutura padrão
        dados_padrao = {
            "queixa_principal": form_data.get('complaint', form_data.get('queixa')),
            "historia_doenca_atual": form_data.get('history', form_data.get('historia')),
            "tempo_sintomas": form_data.get('duration', form_data.get('duracao')),
            "sintomas": {
                "gerais": form_data.get('general_symptoms', ''),
                "neurologicos": form_data.get('neuro_symptoms', ''),
                # ... mapear outros sintomas
            },
            "medicacoes": form_data.get('medications', []),
            "alergias": form_data.get('allergies', ''),
            "habitos": {
                "tabagismo": form_data.get('smoking', ''),
                "etilismo": form_data.get('alcohol', ''),
                "atividade_fisica": form_data.get('exercise', ''),
                "sono_qualidade": form_data.get('sleep', '')
            }
        }
        
        # Identifica paciente (por CPF ou email)
        paciente_id = self._buscar_paciente_por_dados(form_data)
        
        if not paciente_id:
            logging.error("❌ Paciente não encontrado para o formulário")
            return None
        
        return self.importar_questionario_json(dados_padrao, paciente_id)
    
    def _buscar_paciente_por_dados(self, form_data: Dict) -> Optional[int]:
        """Busca paciente por CPF ou email no formulário"""
        
        cpf = form_data.get('cpf', '').strip()
        email = form_data.get('email', '').strip()
        
        if cpf:
            sql = "SELECT id FROM pacientes WHERE cpf = %s"
            self.db.cursor.execute(sql, (cpf,))
            resultado = self.db.cursor.fetchone()
            if resultado:
                return resultado[0]
        
        if email:
            sql = "SELECT id FROM pacientes WHERE email = %s"
            self.db.cursor.execute(sql, (email,))
            resultado = self.db.cursor.fetchone()
            if resultado:
                return resultado[0]
        
        return None
    
    def integrar_ao_prontuario(self, anamnese_id: int) -> bool:
        """
        Integra anamnese ao prontuário do paciente
        Cria entrada na tabela de consultas com dados da anamnese
        """
        
        try:
            # Busca dados da anamnese
            sql = """
            SELECT a.*, p.nome 
            FROM anamnese a 
            JOIN pacientes p ON a.paciente_id = p.id 
            WHERE a.id = %s
            """
            self.db.cursor.execute(sql, (anamnese_id,))
            anamnese = self.db.cursor.fetchone()
            
            if not anamnese:
                logging.error("❌ Anamnese não encontrada")
                return False
            
            # Cria texto estruturado para o prontuário
            prontuario_texto = f"""
ANAMNESE - {date.today().strftime('%d/%m/%Y')}

QUEIXA PRINCIPAL:
{anamnese['queixa_principal'] or 'Não informado'}

HISTÓRIA DA DOENÇA ATUAL:
{anamnese['historia_doenca_atual'] or 'Não informado'}

TEMPO DE SINTOMAS: {anamnese['tempo_sintomas'] or 'Não informado'}

REVISÃO DE SISTEMAS:
- Gerais: {anamnese['sintomas_gerais'] or 'Nega'}
- Neurológicos: {anamnese['sintomas_neurologicos'] or 'Nega'}
- Cardiovasculares: {anamnese['sintomas_cardiovasculares'] or 'Nega'}
- Respiratórios: {anamnese['sintomas_respiratorios'] or 'Nega'}
- Gastrointestinais: {anamnese['sintomas_gastrointestinais'] or 'Nega'}
- Genitourinários: {anamnese['sintomas_genitourinarios'] or 'Nega'}
- Musculoesqueléticos: {anamnese['sintomas_musculoesqueleticos'] or 'Nega'}

ANTECEDENTES PESSOAIS:
{anamnese['antecedentes_pessoais'] or 'Nega'}

ANTECEDENTES FAMILIARES:
{anamnese['antecedentes_familiares'] or 'Nega'}

ANTECEDENTES CIRÚRGICOS:
{anamnese['antecedentes_cirurgicos'] or 'Nega'}

MEDICAÇÕES EM USO:
{anamnese['medicacoes_atuais'] or 'Nega'}

ALERGIAS:
{anamnese['alergias'] or 'Nega'}

HÁBITOS:
- Tabagismo: {anamnese['tabagismo'] or 'Nega'}
- Etilismo: {anamnese['etilismo'] or 'Nega'}
- Atividade física: {anamnese['atividade_fisica'] or 'Sedentário'}
- Qualidade do sono: {anamnese['sono_qualidade'] or 'Não informado'}
"""
            
            # Cria entrada na tabela de consultas
            sql_consulta = """
            INSERT INTO consultas (
                paciente_id,
                data_consulta,
                tipo_consulta,
                anamnese,
                observacoes
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            valores_consulta = (
                anamnese['paciente_id'],
                date.today(),
                'anamnese_inicial',
                prontuario_texto,
                'Anamnese importada automaticamente do questionário'
            )
            
            self.db.cursor.execute(sql_consulta, valores_consulta)
            consulta_id = self.db.cursor.fetchone()[0]
            
            # Atualiza status da anamnese
            sql_update = """
            UPDATE anamnese 
            SET status = 'integrado', 
                data_revisao = CURRENT_TIMESTAMP,
                observacoes_revisao = %s
            WHERE id = %s
            """
            self.db.cursor.execute(sql_update, (
                f'Integrado ao prontuário - Consulta ID: {consulta_id}',
                anamnese_id
            ))
            
            self.db.connection.commit()
            
            logging.info(f"✅ Anamnese integrada ao prontuário - Consulta ID: {consulta_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro ao integrar anamnese: {e}")
            self.db.connection.rollback()
            return False
    
    def listar_anamneses_pendentes(self) -> List[Dict]:
        """Lista anamneses que ainda não foram integradas"""
        
        sql = """
        SELECT a.id, a.data_preenchimento, a.hora_preenchimento, 
               p.nome, a.queixa_principal
        FROM anamnese a
        JOIN pacientes p ON a.paciente_id = p.id
        WHERE a.status = 'pendente'
        ORDER BY a.data_preenchimento DESC, a.hora_preenchimento DESC;
        """
        
        self.db.cursor.execute(sql)
        
        resultados = []
        for row in self.db.cursor.fetchall():
            resultados.append({
                'id': row[0],
                'data': row[1],
                'hora': row[2],
                'paciente': row[3],
                'queixa': row[4]
            })
        
        return resultados
    
    def exportar_anamnese_pdf(self, anamnese_id: int) -> Optional[str]:
        """Exporta anamnese para PDF (futura implementação)"""
        # TODO: Implementar exportação para PDF
        logging.info("📄 Exportação para PDF será implementada em breve")
        return None

if __name__ == "__main__":
    # Teste do módulo
    qa = QuestionarioAnamnese()
    
    # Criar tabela
    qa.criar_tabela_anamnese()
    
    # Exemplo de importação
    dados_teste = {
        "queixa_principal": "Dor lombar há 3 meses",
        "historia_doenca_atual": "Paciente refere dor em região lombar baixa...",
        "tempo_sintomas": "3 meses",
        "sintomas": {
            "gerais": "Nega febre ou perda de peso",
            "neurologicos": "Parestesias em MMII ocasionais",
            "musculoesqueleticos": "Dor lombar que piora com movimento"
        },
        "medicacoes": ["Dipirona 500mg", "Ciclobenzaprina 10mg"],
        "alergias": "Nega",
        "habitos": {
            "tabagismo": "Nega",
            "etilismo": "Social",
            "atividade_fisica": "Sedentário",
            "sono_qualidade": "Regular"
        }
    }
    
    print("✅ Módulo de Questionário de Anamnese configurado!")
    print("📋 Funcionalidades disponíveis:")
    print("  - Importar questionários JSON")
    print("  - Processar formulários web")
    print("  - Integrar ao prontuário")
    print("  - Listar anamneses pendentes")
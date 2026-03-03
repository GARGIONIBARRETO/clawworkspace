#!/usr/bin/env python3
"""
Módulo de Geração de Pedidos Cirúrgicos
Gera pedidos completos com códigos de tabela e informações do paciente
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, Optional, List
from db_manager import DatabaseManager
from pacientes_manager import PacientesManager

class PedidosCirurgicos:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        self.pacientes = PacientesManager()
        
    def criar_tabelas(self):
        """Cria tabelas para pedidos cirúrgicos e templates"""
        
        sql_templates = """
        CREATE TABLE IF NOT EXISTS pedidos_templates (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            tipo_cirurgia VARCHAR(100),
            especialidade VARCHAR(50) DEFAULT 'neurocirurgia_coluna',
            
            -- Dados do template
            diagnostico_padrao TEXT,
            procedimento_padrao TEXT,
            justificativa_padrao TEXT,
            materiais_padrao TEXT,
            observacoes_padrao TEXT,
            
            -- Códigos de tabela
            codigos_procedimento JSON, -- [{codigo, descricao, tabela}]
            codigos_material JSON,     -- [{codigo, descricao, quantidade}]
            
            -- Controle
            ativo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS pedidos_cirurgicos (
            id SERIAL PRIMARY KEY,
            paciente_id INTEGER REFERENCES pacientes(id),
            template_id INTEGER REFERENCES pedidos_templates(id),
            data_pedido DATE DEFAULT CURRENT_DATE,
            data_cirurgia DATE,
            
            -- Dados do pedido
            numero_pedido VARCHAR(50),
            convenio VARCHAR(100),
            matricula VARCHAR(50),
            
            -- Diagnóstico
            cid_principal VARCHAR(10),
            cid_secundario VARCHAR(10),
            diagnostico TEXT NOT NULL,
            
            -- Procedimento
            procedimento_principal TEXT NOT NULL,
            procedimentos_adicionais TEXT,
            justificativa TEXT,
            
            -- Materiais
            materiais_especiais TEXT,
            opme_detalhada JSON, -- Órteses, Próteses e Materiais Especiais
            
            -- Equipe
            cirurgiao_principal VARCHAR(100),
            crm_cirurgiao VARCHAR(20),
            auxiliares TEXT,
            anestesista VARCHAR(100),
            
            -- Informações adicionais
            tempo_cirurgico_estimado VARCHAR(20),
            tipo_anestesia VARCHAR(50),
            necessita_uti BOOLEAN DEFAULT FALSE,
            dias_internacao_previstos INTEGER,
            
            -- Observações
            observacoes TEXT,
            exames_pre_operatorios TEXT,
            
            -- Códigos finais
            codigos_procedimento JSON,
            codigos_material JSON,
            
            -- Status
            status VARCHAR(20) DEFAULT 'rascunho', -- rascunho, enviado, autorizado, negado
            data_envio TIMESTAMP,
            data_autorizacao TIMESTAMP,
            numero_autorizacao VARCHAR(50),
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS tabela_procedimentos (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(20) NOT NULL,
            descricao TEXT NOT NULL,
            tabela_origem VARCHAR(20) DEFAULT 'TUSS', -- TUSS, AMB, CBHPM
            especialidade VARCHAR(50),
            porte VARCHAR(20),
            valor_referencia DECIMAL(10,2),
            observacoes TEXT,
            ativo BOOLEAN DEFAULT TRUE
        );
        
        CREATE INDEX IF NOT EXISTS idx_pedidos_paciente ON pedidos_cirurgicos(paciente_id);
        CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos_cirurgicos(status);
        CREATE INDEX IF NOT EXISTS idx_procedimentos_codigo ON tabela_procedimentos(codigo);
        """
        
        try:
            self.db.cursor.execute(sql_templates)
            self.db.connection.commit()
            logging.info("✅ Tabelas de pedidos cirúrgicos criadas/verificadas")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    def adicionar_template(self, nome: str, dados: Dict) -> Optional[int]:
        """Adiciona um template de pedido cirúrgico"""
        
        sql = """
        INSERT INTO pedidos_templates (
            nome, tipo_cirurgia, especialidade,
            diagnostico_padrao, procedimento_padrao, justificativa_padrao,
            materiais_padrao, observacoes_padrao,
            codigos_procedimento, codigos_material
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        valores = (
            nome,
            dados.get('tipo_cirurgia'),
            dados.get('especialidade', 'neurocirurgia_coluna'),
            dados.get('diagnostico_padrao'),
            dados.get('procedimento_padrao'),
            dados.get('justificativa_padrao'),
            dados.get('materiais_padrao'),
            dados.get('observacoes_padrao'),
            json.dumps(dados.get('codigos_procedimento', [])),
            json.dumps(dados.get('codigos_material', []))
        )
        
        try:
            self.db.cursor.execute(sql, valores)
            template_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            logging.info(f"✅ Template '{nome}' adicionado com ID: {template_id}")
            return template_id
        except Exception as e:
            logging.error(f"❌ Erro ao adicionar template: {e}")
            self.db.connection.rollback()
            return None
    
    def gerar_pedido_cirurgico(self, paciente_id: int, template_id: Optional[int] = None, 
                               dados_customizados: Optional[Dict] = None) -> Optional[int]:
        """
        Gera um pedido cirúrgico completo
        Pode usar template ou dados customizados
        """
        
        try:
            # Busca dados do paciente
            paciente = self.pacientes.buscar_paciente_por_id(paciente_id)
            if not paciente:
                logging.error("❌ Paciente não encontrado")
                return None
            
            # Se usar template, carrega dados padrão
            dados_pedido = {}
            if template_id:
                sql = "SELECT * FROM pedidos_templates WHERE id = %s"
                self.db.cursor.execute(sql, (template_id,))
                template = self.db.cursor.fetchone()
                if template:
                    dados_pedido = {
                        'diagnostico': template['diagnostico_padrao'],
                        'procedimento_principal': template['procedimento_padrao'],
                        'justificativa': template['justificativa_padrao'],
                        'materiais_especiais': template['materiais_padrao'],
                        'observacoes': template['observacoes_padrao'],
                        'codigos_procedimento': json.loads(template['codigos_procedimento']),
                        'codigos_material': json.loads(template['codigos_material'])
                    }
            
            # Sobrescreve com dados customizados se fornecidos
            if dados_customizados:
                dados_pedido.update(dados_customizados)
            
            # Busca última consulta para complementar diagnóstico
            sql_consulta = """
            SELECT anamnese, exame_fisico, hipotese_diagnostica
            FROM consultas
            WHERE paciente_id = %s
            ORDER BY data_consulta DESC
            LIMIT 1;
            """
            self.db.cursor.execute(sql_consulta, (paciente_id,))
            ultima_consulta = self.db.cursor.fetchone()
            
            # Gera número do pedido
            numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{paciente_id}"
            
            # Insere pedido
            sql_pedido = """
            INSERT INTO pedidos_cirurgicos (
                paciente_id, template_id, numero_pedido,
                convenio, matricula,
                cid_principal, cid_secundario, diagnostico,
                procedimento_principal, procedimentos_adicionais, justificativa,
                materiais_especiais, opme_detalhada,
                cirurgiao_principal, crm_cirurgiao,
                tempo_cirurgico_estimado, tipo_anestesia,
                necessita_uti, dias_internacao_previstos,
                observacoes, exames_pre_operatorios,
                codigos_procedimento, codigos_material,
                data_cirurgia
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            valores_pedido = (
                paciente_id,
                template_id,
                numero_pedido,
                dados_pedido.get('convenio'),
                dados_pedido.get('matricula'),
                dados_pedido.get('cid_principal'),
                dados_pedido.get('cid_secundario'),
                dados_pedido.get('diagnostico', ''),
                dados_pedido.get('procedimento_principal', ''),
                dados_pedido.get('procedimentos_adicionais'),
                dados_pedido.get('justificativa'),
                dados_pedido.get('materiais_especiais'),
                json.dumps(dados_pedido.get('opme_detalhada', {})),
                dados_pedido.get('cirurgiao_principal', 'Dr. Felipe G Barreto'),
                dados_pedido.get('crm_cirurgiao'),
                dados_pedido.get('tempo_cirurgico_estimado'),
                dados_pedido.get('tipo_anestesia'),
                dados_pedido.get('necessita_uti', False),
                dados_pedido.get('dias_internacao_previstos'),
                dados_pedido.get('observacoes'),
                dados_pedido.get('exames_pre_operatorios'),
                json.dumps(dados_pedido.get('codigos_procedimento', [])),
                json.dumps(dados_pedido.get('codigos_material', [])),
                dados_pedido.get('data_cirurgia')
            )
            
            self.db.cursor.execute(sql_pedido, valores_pedido)
            pedido_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            
            logging.info(f"✅ Pedido cirúrgico gerado - ID: {pedido_id} | Número: {numero_pedido}")
            return pedido_id
            
        except Exception as e:
            logging.error(f"❌ Erro ao gerar pedido: {e}")
            self.db.connection.rollback()
            return None
    
    def gerar_pdf_pedido(self, pedido_id: int) -> Optional[str]:
        """Gera PDF formatado do pedido cirúrgico"""
        
        try:
            # Busca dados completos do pedido
            sql = """
            SELECT pc.*, p.nome, p.cpf, p.data_nascimento, p.telefone,
                   pt.nome as template_nome
            FROM pedidos_cirurgicos pc
            JOIN pacientes p ON pc.paciente_id = p.id
            LEFT JOIN pedidos_templates pt ON pc.template_id = pt.id
            WHERE pc.id = %s
            """
            self.db.cursor.execute(sql, (pedido_id,))
            pedido = self.db.cursor.fetchone()
            
            if not pedido:
                logging.error("❌ Pedido não encontrado")
                return None
            
            # Calcula idade
            if pedido['data_nascimento']:
                idade = (date.today() - pedido['data_nascimento']).days // 365
            else:
                idade = "N/I"
            
            # Monta HTML do pedido
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Pedido Cirúrgico - {pedido['numero_pedido']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .section {{ margin: 20px 0; }}
                    .section-title {{ font-weight: bold; font-size: 14px; margin: 10px 0; 
                                     background: #f0f0f0; padding: 5px; }}
                    .field {{ margin: 5px 0; }}
                    .label {{ font-weight: bold; display: inline-block; width: 150px; }}
                    .value {{ display: inline-block; }}
                    .procedimentos, .materiais {{ margin: 10px 0; padding: 10px; 
                                                  border: 1px solid #ddd; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background: #f0f0f0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>PEDIDO DE AUTORIZAÇÃO CIRÚRGICA</h2>
                    <p>Número: {pedido['numero_pedido']}</p>
                    <p>Data: {pedido['data_pedido'].strftime('%d/%m/%Y')}</p>
                </div>
                
                <div class="section">
                    <div class="section-title">DADOS DO PACIENTE</div>
                    <div class="field">
                        <span class="label">Nome:</span>
                        <span class="value">{pedido['nome']}</span>
                    </div>
                    <div class="field">
                        <span class="label">CPF:</span>
                        <span class="value">{pedido['cpf'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Idade:</span>
                        <span class="value">{idade} anos</span>
                    </div>
                    <div class="field">
                        <span class="label">Telefone:</span>
                        <span class="value">{pedido['telefone'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Convênio:</span>
                        <span class="value">{pedido['convenio'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Matrícula:</span>
                        <span class="value">{pedido['matricula'] or 'N/I'}</span>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">DIAGNÓSTICO</div>
                    <div class="field">
                        <span class="label">CID Principal:</span>
                        <span class="value">{pedido['cid_principal'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">CID Secundário:</span>
                        <span class="value">{pedido['cid_secundario'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Diagnóstico:</span><br>
                        <span class="value">{pedido['diagnostico']}</span>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">PROCEDIMENTO PROPOSTO</div>
                    <div class="procedimentos">
                        <p><strong>Procedimento Principal:</strong><br>
                        {pedido['procedimento_principal']}</p>
                        
                        {f'<p><strong>Procedimentos Adicionais:</strong><br>{pedido["procedimentos_adicionais"]}</p>' 
                         if pedido['procedimentos_adicionais'] else ''}
                    </div>
                    
                    <div class="field">
                        <span class="label">Justificativa:</span><br>
                        <span class="value">{pedido['justificativa'] or 'N/I'}</span>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">CÓDIGOS DOS PROCEDIMENTOS</div>
                    <table>
                        <tr>
                            <th>Código</th>
                            <th>Descrição</th>
                            <th>Tabela</th>
                        </tr>
            """
            
            # Adiciona códigos de procedimento
            codigos_proc = json.loads(pedido['codigos_procedimento'] or '[]')
            for codigo in codigos_proc:
                html_content += f"""
                        <tr>
                            <td>{codigo.get('codigo', '')}</td>
                            <td>{codigo.get('descricao', '')}</td>
                            <td>{codigo.get('tabela', 'TUSS')}</td>
                        </tr>
                """
            
            html_content += """
                    </table>
                </div>
                
                <div class="section">
                    <div class="section-title">MATERIAIS ESPECIAIS / OPME</div>
            """
            
            if pedido['materiais_especiais']:
                html_content += f"<p>{pedido['materiais_especiais']}</p>"
            
            # Adiciona tabela de materiais se houver
            codigos_mat = json.loads(pedido['codigos_material'] or '[]')
            if codigos_mat:
                html_content += """
                    <table>
                        <tr>
                            <th>Código</th>
                            <th>Descrição</th>
                            <th>Quantidade</th>
                        </tr>
                """
                for material in codigos_mat:
                    html_content += f"""
                        <tr>
                            <td>{material.get('codigo', '')}</td>
                            <td>{material.get('descricao', '')}</td>
                            <td>{material.get('quantidade', '1')}</td>
                        </tr>
                    """
                html_content += "</table>"
            
            html_content += f"""
                </div>
                
                <div class="section">
                    <div class="section-title">INFORMAÇÕES CIRÚRGICAS</div>
                    <div class="field">
                        <span class="label">Data prevista:</span>
                        <span class="value">{pedido['data_cirurgia'].strftime('%d/%m/%Y') 
                                            if pedido['data_cirurgia'] else 'A definir'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Tempo estimado:</span>
                        <span class="value">{pedido['tempo_cirurgico_estimado'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Tipo de anestesia:</span>
                        <span class="value">{pedido['tipo_anestesia'] or 'N/I'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Necessita UTI:</span>
                        <span class="value">{'Sim' if pedido['necessita_uti'] else 'Não'}</span>
                    </div>
                    <div class="field">
                        <span class="label">Dias de internação:</span>
                        <span class="value">{pedido['dias_internacao_previstos'] or 'N/I'}</span>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">EQUIPE CIRÚRGICA</div>
                    <div class="field">
                        <span class="label">Cirurgião:</span>
                        <span class="value">{pedido['cirurgiao_principal'] or 'Dr. Felipe G Barreto'}</span>
                    </div>
                    <div class="field">
                        <span class="label">CRM:</span>
                        <span class="value">{pedido['crm_cirurgiao'] or 'N/I'}</span>
                    </div>
                </div>
                
                {f'<div class="section"><div class="section-title">OBSERVAÇÕES</div><p>{pedido["observacoes"]}</p></div>' 
                 if pedido['observacoes'] else ''}
                
                {f'<div class="section"><div class="section-title">EXAMES PRÉ-OPERATÓRIOS</div><p>{pedido["exames_pre_operatorios"]}</p></div>' 
                 if pedido['exames_pre_operatorios'] else ''}
                
                <div style="margin-top: 50px; text-align: center;">
                    <p>_____________________________________</p>
                    <p>{pedido['cirurgiao_principal'] or 'Dr. Felipe G Barreto'}<br>
                    CRM: {pedido['crm_cirurgiao'] or ''}</p>
                </div>
            </body>
            </html>
            """
            
            # Salva HTML
            import os
            os.makedirs('/root/clawd/pedidos', exist_ok=True)
            
            arquivo_html = f"/root/clawd/pedidos/pedido_{pedido['numero_pedido']}.html"
            with open(arquivo_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"✅ Pedido exportado: {arquivo_html}")
            
            # TODO: Converter HTML para PDF usando wkhtmltopdf ou similar
            return arquivo_html
            
        except Exception as e:
            logging.error(f"❌ Erro ao gerar PDF: {e}")
            return None
    
    def carregar_codigos_tabela(self, arquivo_csv: str) -> int:
        """Carrega códigos de procedimentos de arquivo CSV"""
        
        import csv
        contador = 0
        
        try:
            with open(arquivo_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    sql = """
                    INSERT INTO tabela_procedimentos 
                    (codigo, descricao, tabela_origem, especialidade, porte)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """
                    
                    valores = (
                        row.get('codigo'),
                        row.get('descricao'),
                        row.get('tabela', 'TUSS'),
                        row.get('especialidade'),
                        row.get('porte')
                    )
                    
                    self.db.cursor.execute(sql, valores)
                    contador += 1
            
            self.db.connection.commit()
            logging.info(f"✅ {contador} códigos carregados na tabela")
            return contador
            
        except Exception as e:
            logging.error(f"❌ Erro ao carregar códigos: {e}")
            self.db.connection.rollback()
            return 0
    
    def buscar_codigo_procedimento(self, termo: str) -> List[Dict]:
        """Busca códigos de procedimento por termo"""
        
        sql = """
        SELECT codigo, descricao, tabela_origem, porte
        FROM tabela_procedimentos
        WHERE descricao ILIKE %s OR codigo = %s
        LIMIT 10;
        """
        
        termo_busca = f"%{termo}%"
        self.db.cursor.execute(sql, (termo_busca, termo))
        
        resultados = []
        for row in self.db.cursor.fetchall():
            resultados.append({
                'codigo': row[0],
                'descricao': row[1],
                'tabela': row[2],
                'porte': row[3]
            })
        
        return resultados

# Templates padrão de cirurgias comuns
TEMPLATES_PADRAO = {
    "hernia_discal_lombar": {
        "nome": "Hérnia Discal Lombar - Microdiscectomia",
        "tipo_cirurgia": "Microdiscectomia",
        "diagnostico_padrao": "Hérnia discal lombar com radiculopatia",
        "procedimento_padrao": "Microdiscectomia lombar com descompressão radicular",
        "justificativa_padrao": "Paciente com hérnia discal lombar confirmada por RNM, apresentando radiculopatia com déficit neurológico progressivo, refratário ao tratamento conservador por mais de 6 semanas.",
        "materiais_padrao": "Microscópio cirúrgico, material de hemostasia",
        "codigos_procedimento": [
            {"codigo": "31403047", "descricao": "Microdiscectomia lombar", "tabela": "TUSS"},
            {"codigo": "31403055", "descricao": "Descompressão radicular", "tabela": "TUSS"}
        ],
        "tempo_cirurgico_estimado": "2 horas",
        "tipo_anestesia": "Geral",
        "dias_internacao_previstos": 1
    },
    
    "estenose_canal": {
        "nome": "Estenose de Canal - Laminectomia",
        "tipo_cirurgia": "Laminectomia descompressiva",
        "diagnostico_padrao": "Estenose de canal lombar com claudicação neurogênica",
        "procedimento_padrao": "Laminectomia descompressiva multinível",
        "justificativa_padrao": "Paciente com estenose de canal lombar severa documentada em exames de imagem, apresentando claudicação neurogênica limitante, sem melhora com tratamento conservador.",
        "materiais_padrao": "Drill de alta rotação, material de hemostasia",
        "codigos_procedimento": [
            {"codigo": "31403039", "descricao": "Laminectomia descompressiva", "tabela": "TUSS"}
        ],
        "tempo_cirurgico_estimado": "3 horas",
        "tipo_anestesia": "Geral",
        "dias_internacao_previstos": 2
    },
    
    "artrodese_posterior": {
        "nome": "Artrodese Lombar Posterior com Instrumentação",
        "tipo_cirurgia": "Artrodese posterior",
        "diagnostico_padrao": "Espondilolistese com instabilidade segmentar",
        "procedimento_padrao": "Artrodese lombar posterior com instrumentação pedicular",
        "justificativa_padrao": "Paciente com espondilolistese e instabilidade segmentar documentada, com falha do tratamento conservador, apresentando dor incapacitante e/ou déficit neurológico progressivo.",
        "materiais_padrao": """06 Parafusos pediculares poliaxiais
04 Barras de titânio
06 Bloqueadores
01 Enxerto ósseo sintético
01 Hemostático absorvível
01 Kit de brocas""",
        "codigos_procedimento": [
            {"codigo": "30712114", "descricao": "Espondilolistese - tratamento cirúrgico", "tabela": "TUSS", "quantidade": 2},
            {"codigo": "30715016", "descricao": "Artrodese da coluna com instrumentação por segmento", "tabela": "TUSS", "quantidade": 2},
            {"codigo": "30732026", "descricao": "Enxerto ósseo", "tabela": "TUSS", "quantidade": 1},
            {"codigo": "40811026", "descricao": "Radioscopia para acompanhamento de procedimento cirúrgico", "tabela": "TUSS"}
        ],
        "codigos_material": [
            {"codigo": "07020902", "descricao": "Parafuso pedicular", "quantidade": 6},
            {"codigo": "07020910", "descricao": "Barra de conexão", "quantidade": 4},
            {"codigo": "07020929", "descricao": "Bloqueador", "quantidade": 6},
            {"codigo": "07010478", "descricao": "Agente hemostático absorvível", "quantidade": 1}
        ],
        "tempo_cirurgico_estimado": "4 horas",
        "tipo_anestesia": "Geral",
        "necessita_uti": True,
        "dias_internacao_previstos": 3,
        "observacoes_padrao": "Monitorização eletrofisiológica intraoperatória. Reservar hemoderivados (2 CH). Radioscopia disponível."
    },
    
    "artrodese_anterior": {
        "nome": "Artrodese Lombar Anterior (ALIF)",
        "tipo_cirurgia": "Artrodese anterior",
        "diagnostico_padrao": "Discopatia degenerativa com colapso do espaço discal",
        "procedimento_padrao": "Artrodese lombar via anterior (ALIF) com cage intersomático",
        "justificativa_padrao": "Paciente com discopatia degenerativa severa, colapso do espaço discal e instabilidade segmentar, com falha do tratamento conservador.",
        "materiais_padrao": """01 Cage intersomático ALIF
01 Placa anterior de fixação
04 Parafusos de fixação
01 Enxerto ósseo/substituto ósseo
01 Hemostático
Material de acesso vascular""",
        "codigos_procedimento": [
            {"codigo": "30714024", "descricao": "Artrodese de coluna via anterior ou póstero-lateral", "tabela": "TUSS", "quantidade": 1},
            {"codigo": "30715016", "descricao": "Artrodese da coluna com instrumentação por segmento", "tabela": "TUSS"},
            {"codigo": "30732026", "descricao": "Enxerto ósseo", "tabela": "TUSS"}
        ],
        "codigos_material": [
            {"codigo": "07020937", "descricao": "Cage intersomático", "quantidade": 1},
            {"codigo": "07020945", "descricao": "Placa anterior", "quantidade": 1},
            {"codigo": "07020953", "descricao": "Parafuso de placa", "quantidade": 4}
        ],
        "tempo_cirurgico_estimado": "3 horas",
        "tipo_anestesia": "Geral",
        "dias_internacao_previstos": 2,
        "observacoes_padrao": "Cirurgião vascular de apoio. Radioscopia em duas incidências."
    },
    
    "artrodese_360": {
        "nome": "Artrodese 360° (Anterior + Posterior)",
        "tipo_cirurgia": "Artrodese combinada",
        "diagnostico_padrao": "Espondilolistese de alto grau com instabilidade severa",
        "procedimento_padrao": "Artrodese lombar 360 graus - via anterior (ALIF) + posterior com instrumentação",
        "justificativa_padrao": "Paciente com instabilidade severa, espondilolistese de alto grau ou pseudoartrose, necessitando fusão circunferencial para adequada estabilização.",
        "materiais_padrao": """ANTERIOR:
01 Cage intersomático ALIF
01 Placa anterior
04 Parafusos de placa

POSTERIOR:
06-08 Parafusos pediculares
04 Barras
06-08 Bloqueadores
02 Cross-links
01 Enxerto ósseo
02 Hemostáticos""",
        "codigos_procedimento": [
            {"codigo": "30714024", "descricao": "Artrodese via anterior", "tabela": "TUSS", "quantidade": 2},
            {"codigo": "30715016", "descricao": "Artrodese com instrumentação por segmento", "tabela": "TUSS", "quantidade": 4},
            {"codigo": "30712114", "descricao": "Espondilolistese - tratamento cirúrgico", "tabela": "TUSS", "quantidade": 2},
            {"codigo": "30732026", "descricao": "Enxerto ósseo", "tabela": "TUSS", "quantidade": 2}
        ],
        "tempo_cirurgico_estimado": "6-8 horas",
        "tipo_anestesia": "Geral",
        "necessita_uti": True,
        "dias_internacao_previstos": 4,
        "observacoes_padrao": "Procedimento em dois tempos cirúrgicos. Monitorização neurofisiológica. Reservar 4 CH. Equipe vascular para acesso anterior."
    },
    
    "artrodese_iliaco": {
        "nome": "Artrodese com Extensão ao Ilíaco",
        "tipo_cirurgia": "Artrodese lombo-pélvica",
        "diagnostico_padrao": "Instabilidade lombo-sacra com falha de artrodese prévia",
        "procedimento_padrao": "Artrodese lombar com extensão ao ilíaco bilateral",
        "justificativa_padrao": "Paciente com falha de fusão L5-S1, instabilidade lombo-sacra ou necessidade de construção longa com ancoragem pélvica para adequada distribuição de cargas.",
        "materiais_padrao": """06 Parafusos pediculares
02 Parafusos ilíacos
08 Bloqueadores
04 Barras
02 Conectores/Offset
02 Cross-links
01 Enxerto ósseo volumoso
02 Hemostáticos
01 Substituto dural (se necessário)""",
        "codigos_procedimento": [
            {"codigo": "30712114", "descricao": "Espondilolistese - tratamento cirúrgico", "tabela": "TUSS", "quantidade": 2},
            {"codigo": "30715016", "descricao": "Artrodese com instrumentação por segmento", "tabela": "TUSS", "quantidade": 3},
            {"codigo": "30715091", "descricao": "Descompressão medular e/ou cauda equina", "tabela": "TUSS", "quantidade": 2},
            {"codigo": "30732026", "descricao": "Enxerto ósseo", "tabela": "TUSS"}
        ],
        "codigos_material": [
            {"codigo": "07020902", "descricao": "Parafuso pedicular", "quantidade": 6},
            {"codigo": "07020961", "descricao": "Parafuso ilíaco", "quantidade": 2},
            {"codigo": "07020970", "descricao": "Conector/Offset", "quantidade": 2},
            {"codigo": "07020988", "descricao": "Cross-link", "quantidade": 2}
        ],
        "tempo_cirurgico_estimado": "5-6 horas",
        "tipo_anestesia": "Geral",
        "necessita_uti": True,
        "dias_internacao_previstos": 4,
        "observacoes_padrao": "Monitorização neurofisiológica obrigatória. Reservar 4 CH. Radioscopia. Cell saver recomendado."
    },
    
    "endoscopia_percutanea": {
        "nome": "Tratamento Endoscópico Percutâneo - Hérnia Discal",
        "tipo_cirurgia": "Endoscopia percutânea",
        "diagnostico_padrao": "Hérnia discal com radiculopatia refratária",
        "procedimento_padrao": "Discectomia endoscópica percutânea transforaminal",
        "justificativa_padrao": "Paciente com hérnia discal sintomática, radiculopatia persistente apesar do tratamento conservador adequado. Indicado procedimento minimamente invasivo para preservação da anatomia e recuperação precoce.",
        "materiais_padrao": """01 Kit endoscopia de coluna
01 Pinça endoscópica
01 Probe de radiofrequência
01 Cânula de trabalho
01 Agulha de punção
Material de hemostasia""",
        "codigos_procedimento": [
            {"codigo": "31403063", "descricao": "Discectomia percutânea (qualquer técnica)", "tabela": "TUSS"},
            {"codigo": "40811026", "descricao": "Radioscopia para acompanhamento", "tabela": "TUSS"}
        ],
        "tempo_cirurgico_estimado": "2 horas",
        "tipo_anestesia": "Local com sedação",
        "dias_internacao_previstos": 1,
        "observacoes_padrao": "Radioscopia obrigatória. Antibioticoprofilaxia. Day hospital possível em casos selecionados."
    },
    
    "rizotomia_percutanea": {
        "nome": "Rizotomia Percutânea por Radiofrequência",
        "tipo_cirurgia": "Procedimento percutâneo",
        "diagnostico_padrao": "Síndrome facetária lombar",
        "procedimento_padrao": "Rizotomia percutânea por radiofrequência dos ramos mediais",
        "justificativa_padrao": "Paciente com dor facetária confirmada por bloqueio diagnóstico prévio com melhora > 50%. Indicada denervação por radiofrequência para alívio prolongado.",
        "materiais_padrao": """01 Kit de radiofrequência
02-04 Eletrodos de RF
01 Gerador de radiofrequência
Agulhas especiais RF""",
        "codigos_procedimento": [
            {"codigo": "31401058", "descricao": "Rizotomia percutânea por radiofrequência", "tabela": "TUSS"},
            {"codigo": "40811026", "descricao": "Radioscopia", "tabela": "TUSS"}
        ],
        "tempo_cirurgico_estimado": "1-2 horas",
        "tipo_anestesia": "Local com sedação",
        "dias_internacao_previstos": 0,
        "observacoes_padrao": "Procedimento ambulatorial/day hospital. Radioscopia. Monitorização durante procedimento."
    },
    
    "nucleoplastia": {
        "nome": "Nucleoplastia - Descompressão Discal Percutânea",
        "tipo_cirurgia": "Procedimento percutâneo",
        "diagnostico_padrao": "Hérnia discal contida com dor discogênica",
        "procedimento_padrao": "Nucleoplastia por radiofrequência (coblation)",
        "justificativa_padrao": "Paciente com hérnia discal contida, dor discogênica confirmada, sem déficit neurológico significativo. Candidato a descompressão percutânea.",
        "materiais_padrao": """01 Kit nucleoplastia
01 Wand de coblation
01 Gerador específico
Agulha introdutora""",
        "codigos_procedimento": [
            {"codigo": "31403063", "descricao": "Discectomia percutânea", "tabela": "TUSS"},
            {"codigo": "40811026", "descricao": "Radioscopia", "tabela": "TUSS"}
        ],
        "tempo_cirurgico_estimado": "1 hora",
        "tipo_anestesia": "Local com sedação",
        "dias_internacao_previstos": 0,
        "observacoes_padrao": "Day hospital. Radioscopia obrigatória. Contraindicado em hérnias extrusas."
    },
    
    "bloqueio_epidural": {
        "nome": "Bloqueio Epidural Interlaminar/Transforaminal",
        "tipo_cirurgia": "Procedimento percutâneo",
        "diagnostico_padrao": "Radiculopatia por hérnia discal ou estenose",
        "procedimento_padrao": "Infiltração epidural com corticoide e anestésico",
        "justificativa_padrao": "Paciente com radiculopatia aguda/subaguda, para alívio da dor e redução do processo inflamatório radicular.",
        "materiais_padrao": """01 Kit para bloqueio epidural
01 Agulha epidural/Tuohy
Corticoide depot
Anestésico local
Contraste (se fluoroscopia)""",
        "codigos_procedimento": [
            {"codigo": "31401074", "descricao": "Bloqueio anestésico de nervo periférico", "tabela": "TUSS"},
            {"codigo": "40811026", "descricao": "Radioscopia", "tabela": "TUSS", "opcional": True}
        ],
        "tempo_cirurgico_estimado": "30 minutos",
        "tipo_anestesia": "Local",
        "dias_internacao_previstos": 0,
        "observacoes_padrao": "Procedimento ambulatorial. Observação pós-procedimento 1-2h. Fluoroscopia recomendada."
    },
    
    "vertebroplastia": {
        "nome": "Vertebroplastia Percutânea",
        "tipo_cirurgia": "Procedimento percutâneo",
        "diagnostico_padrao": "Fratura vertebral osteoporótica dolorosa",
        "procedimento_padrao": "Vertebroplastia percutânea com cimento ósseo (PMMA)",
        "justificativa_padrao": "Paciente com fratura vertebral por compressão, dor refratária ao tratamento conservador, sem sinais de instabilidade.",
        "materiais_padrao": """02 Kits vertebroplastia
02-04 Ampolas cimento PMMA
02 Agulhas vertebroplastia
Sistema de mistura/injeção""",
        "codigos_procedimento": [
            {"codigo": "31403071", "descricao": "Vertebroplastia percutânea", "tabela": "TUSS"},
            {"codigo": "40811026", "descricao": "Radioscopia", "tabela": "TUSS"}
        ],
        "codigos_material": [
            {"codigo": "07021496", "descricao": "Kit vertebroplastia", "quantidade": 2},
            {"codigo": "07021500", "descricao": "Cimento ósseo PMMA", "quantidade": 4}
        ],
        "tempo_cirurgico_estimado": "1-2 horas",
        "tipo_anestesia": "Local com sedação",
        "dias_internacao_previstos": 1,
        "observacoes_padrao": "Radioscopia biplanar obrigatória. Monitorização contínua. Observar extravasamento de cimento."
    }
}

if __name__ == "__main__":
    # Teste do módulo
    pc = PedidosCirurgicos()
    
    # Criar tabelas
    pc.criar_tabelas()
    
    print("✅ Módulo de Pedidos Cirúrgicos configurado!")
    print("📋 Funcionalidades disponíveis:")
    print("  - Gerar pedidos com templates")
    print("  - Buscar códigos de procedimentos")
    print("  - Exportar pedidos em PDF/HTML")
    print("  - Gerenciar autorizações")
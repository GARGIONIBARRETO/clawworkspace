#!/usr/bin/env python3
"""
Integração de Pedidos de Cirurgia com Banco de Dados
Sistema de armazenamento e recuperação de pedidos
"""

import psycopg2
import json
from datetime import datetime
from gerador_pedido_cirurgia import GeradorPedidoCirurgia
from db_manager import get_db_connection

class IntegracaoPedidosCirurgiaDB:
    def __init__(self):
        self.gerador = GeradorPedidoCirurgia()
        
    def criar_tabelas(self):
        """Cria tabelas necessárias para pedidos de cirurgia"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Tabela de pedidos de cirurgia
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos_cirurgia (
                    id SERIAL PRIMARY KEY,
                    paciente_id INTEGER REFERENCES pacientes(id),
                    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    template_usado VARCHAR(100),
                    nome_procedimento VARCHAR(200),
                    niveis VARCHAR(50),
                    procedimentos JSONB,
                    observacoes TEXT,
                    tempo_estimado_horas DECIMAL(4,1),
                    validacao JSONB,
                    status VARCHAR(50) DEFAULT 'pendente',
                    medico_solicitante VARCHAR(200),
                    data_cirurgia_prevista DATE,
                    criado_por VARCHAR(100),
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de histórico de validações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_validacoes (
                    id SERIAL PRIMARY KEY,
                    pedido_id INTEGER REFERENCES pedidos_cirurgia(id),
                    data_validacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resultado JSONB,
                    validado_por VARCHAR(100)
                )
            """)
            
            # Tabela de templates customizados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates_cirurgia (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) UNIQUE,
                    descricao VARCHAR(500),
                    template_json JSONB,
                    especialidade VARCHAR(50),
                    ativo BOOLEAN DEFAULT TRUE,
                    criado_por VARCHAR(100),
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Tabelas de pedidos de cirurgia criadas com sucesso!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar tabelas: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def salvar_pedido(self, paciente_id, pedido_dict, medico_solicitante, data_prevista=None):
        """Salva pedido de cirurgia no banco"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO pedidos_cirurgia 
                (paciente_id, template_usado, nome_procedimento, niveis, 
                 procedimentos, observacoes, tempo_estimado_horas, validacao,
                 medico_solicitante, data_cirurgia_prevista, criado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                paciente_id,
                pedido_dict.get('template_usado'),
                pedido_dict.get('nome_procedimento'),
                pedido_dict.get('niveis'),
                json.dumps(pedido_dict.get('procedimentos', [])),
                pedido_dict.get('observacoes'),
                pedido_dict.get('tempo_estimado_horas'),
                json.dumps(pedido_dict.get('validacao', {})),
                medico_solicitante,
                data_prevista,
                'sistema'
            ))
            
            pedido_id = cursor.fetchone()[0]
            
            # Salvar histórico de validação
            if 'validacao' in pedido_dict:
                cursor.execute("""
                    INSERT INTO historico_validacoes (pedido_id, resultado, validado_por)
                    VALUES (%s, %s, %s)
                """, (
                    pedido_id,
                    json.dumps(pedido_dict['validacao']),
                    'sistema_automatico'
                ))
            
            conn.commit()
            print(f"✅ Pedido de cirurgia #{pedido_id} salvo com sucesso!")
            return pedido_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao salvar pedido: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def buscar_pedidos_paciente(self, paciente_id, incluir_finalizados=False):
        """Busca pedidos de cirurgia de um paciente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    pc.id,
                    pc.data_pedido,
                    pc.nome_procedimento,
                    pc.niveis,
                    pc.procedimentos,
                    pc.status,
                    pc.medico_solicitante,
                    pc.data_cirurgia_prevista,
                    pc.tempo_estimado_horas,
                    pc.validacao
                FROM pedidos_cirurgia pc
                WHERE pc.paciente_id = %s
            """
            
            if not incluir_finalizados:
                query += " AND pc.status != 'finalizado'"
            
            query += " ORDER BY pc.data_pedido DESC"
            
            cursor.execute(query, (paciente_id,))
            
            pedidos = []
            for row in cursor.fetchall():
                pedido = {
                    'id': row[0],
                    'data_pedido': row[1].isoformat() if row[1] else None,
                    'nome_procedimento': row[2],
                    'niveis': row[3],
                    'procedimentos': row[4],
                    'status': row[5],
                    'medico_solicitante': row[6],
                    'data_cirurgia_prevista': row[7].isoformat() if row[7] else None,
                    'tempo_estimado_horas': float(row[8]) if row[8] else None,
                    'validacao': row[9]
                }
                pedidos.append(pedido)
            
            return pedidos
            
        except Exception as e:
            print(f"❌ Erro ao buscar pedidos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def atualizar_status_pedido(self, pedido_id, novo_status):
        """Atualiza status de um pedido"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        status_validos = ['pendente', 'autorizado', 'negado', 'agendado', 'realizado', 'cancelado', 'finalizado']
        
        if novo_status not in status_validos:
            print(f"❌ Status inválido: {novo_status}")
            return False
        
        try:
            cursor.execute("""
                UPDATE pedidos_cirurgia 
                SET status = %s, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (novo_status, pedido_id))
            
            conn.commit()
            print(f"✅ Status do pedido #{pedido_id} atualizado para: {novo_status}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao atualizar status: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def revalidar_pedido(self, pedido_id):
        """Revalida um pedido existente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar pedido
            cursor.execute("""
                SELECT procedimentos, niveis, template_usado
                FROM pedidos_cirurgia
                WHERE id = %s
            """, (pedido_id,))
            
            row = cursor.fetchone()
            if not row:
                print(f"❌ Pedido #{pedido_id} não encontrado")
                return None
            
            procedimentos = row[0]
            
            # Recriar estrutura do pedido para validação
            pedido_para_validar = {
                "procedimentos": procedimentos,
                "niveis": row[1]
            }
            
            # Validar
            resultado_validacao = self.gerador.validador.validar_pedido(pedido_para_validar)
            
            # Atualizar validação
            cursor.execute("""
                UPDATE pedidos_cirurgia 
                SET validacao = %s, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (json.dumps(resultado_validacao), pedido_id))
            
            # Salvar no histórico
            cursor.execute("""
                INSERT INTO historico_validacoes (pedido_id, resultado, validado_por)
                VALUES (%s, %s, %s)
            """, (
                pedido_id,
                json.dumps(resultado_validacao),
                'revalidacao_manual'
            ))
            
            conn.commit()
            print(f"✅ Pedido #{pedido_id} revalidado!")
            return resultado_validacao
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao revalidar: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def salvar_template_customizado(self, nome, descricao, template_json, especialidade='coluna'):
        """Salva template customizado no banco"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO templates_cirurgia 
                (nome, descricao, template_json, especialidade, criado_por)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (nome) 
                DO UPDATE SET 
                    descricao = EXCLUDED.descricao,
                    template_json = EXCLUDED.template_json,
                    especialidade = EXCLUDED.especialidade
                RETURNING id
            """, (
                nome,
                descricao,
                json.dumps(template_json),
                especialidade,
                'sistema'
            ))
            
            template_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"✅ Template '{nome}' salvo com sucesso! ID: {template_id}")
            return template_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao salvar template: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def gerar_relatorio_pedidos(self, data_inicio=None, data_fim=None):
        """Gera relatório de pedidos de cirurgia"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    pc.nome_procedimento,
                    pc.status,
                    COUNT(*) as quantidade,
                    AVG(pc.tempo_estimado_horas) as tempo_medio
                FROM pedidos_cirurgia pc
                WHERE 1=1
            """
            
            params = []
            if data_inicio:
                query += " AND pc.data_pedido >= %s"
                params.append(data_inicio)
            if data_fim:
                query += " AND pc.data_pedido <= %s"
                params.append(data_fim)
            
            query += " GROUP BY pc.nome_procedimento, pc.status ORDER BY quantidade DESC"
            
            cursor.execute(query, params)
            
            relatorio = {
                'periodo': {
                    'inicio': data_inicio or 'início',
                    'fim': data_fim or 'atual'
                },
                'estatisticas': []
            }
            
            for row in cursor.fetchall():
                relatorio['estatisticas'].append({
                    'procedimento': row[0],
                    'status': row[1],
                    'quantidade': row[2],
                    'tempo_medio_horas': float(row[3]) if row[3] else None
                })
            
            # Buscar códigos mais utilizados
            cursor.execute("""
                SELECT 
                    p.value->>'codigo' as codigo,
                    p.value->>'descricao' as descricao,
                    COUNT(*) as frequencia
                FROM pedidos_cirurgia pc,
                     jsonb_array_elements(pc.procedimentos) as p
                WHERE 1=1
                GROUP BY p.value->>'codigo', p.value->>'descricao'
                ORDER BY frequencia DESC
                LIMIT 10
            """)
            
            relatorio['codigos_mais_utilizados'] = []
            for row in cursor.fetchall():
                relatorio['codigos_mais_utilizados'].append({
                    'codigo': row[0],
                    'descricao': row[1],
                    'frequencia': row[2]
                })
            
            return relatorio
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            return None
        finally:
            cursor.close()
            conn.close()


# Exemplo de uso
if __name__ == "__main__":
    integracao = IntegracaoPedidosCirurgiaDB()
    
    # Criar tabelas
    integracao.criar_tabelas()
    
    # Gerar e salvar um pedido
    gerador = GeradorPedidoCirurgia()
    pedido = gerador.gerar_pedido("hernia_lombar_simples", {
        "niveis": "L4-L5",
        "condicoes": ["laminectomia_necessaria"],
        "observacoes": "Paciente com história de lombalgia crônica"
    })
    
    # Salvar no banco (exemplo com paciente_id=1)
    pedido_id = integracao.salvar_pedido(
        paciente_id=1,
        pedido_dict=pedido,
        medico_solicitante="Dr. Felipe Barreto",
        data_prevista="2026-03-10"
    )
    
    # Buscar pedidos do paciente
    pedidos = integracao.buscar_pedidos_paciente(1)
    print(f"\n📋 Pedidos encontrados: {len(pedidos)}")
    
    # Gerar relatório
    relatorio = integracao.gerar_relatorio_pedidos()
    if relatorio:
        print("\n📊 Relatório de Pedidos:")
        print(f"Período: {relatorio['periodo']['inicio']} a {relatorio['periodo']['fim']}")
        print("\nCódigos mais utilizados:")
        for codigo in relatorio['codigos_mais_utilizados'][:5]:
            print(f"  {codigo['codigo']} - {codigo['descricao']} (usado {codigo['frequencia']}x)")
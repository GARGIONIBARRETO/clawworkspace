#!/usr/bin/env python3
"""
Adaptador de banco de dados para a interface web
Conecta ao PostgreSQL local e fornece métodos compatíveis
"""

import psycopg2
import psycopg2.extras
import json
from datetime import datetime, date

class PacientesManager:
    """Gerenciador de pacientes compatível com a interface web"""
    
    def __init__(self):
        """Inicializa conexão com PostgreSQL local"""
        try:
            self.conn = psycopg2.connect(
                dbname="clinica_dr_felipe",
                user="clinica_admin",
                password="clinica2026!",
                host="localhost",
                port="5432"
            )
            self.conectado = True
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            self.conectado = False
            self.cursor = None
            
    def fechar_conexao(self):
        """Fecha conexão com o banco"""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            
    def close(self):
        """Alias para fechar_conexao (compatibilidade)"""
        self.fechar_conexao()
            
    def buscar_paciente(self, termo=''):
        """Busca pacientes por nome ou CPF"""
        if not self.conectado:
            return []
            
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if termo:
                cur.execute("""
                    SELECT id, nome, cpf, telefone, email, data_nascimento, convenio,
                           created_at as data_cadastro
                    FROM pacientes 
                    WHERE LOWER(nome) LIKE LOWER(%s) 
                       OR cpf LIKE %s
                    ORDER BY nome
                    LIMIT 50
                """, (f'%{termo}%', f'%{termo}%'))
            else:
                # Se não há termo, retorna todos (com limite)
                cur.execute("""
                    SELECT id, nome, cpf, telefone, email, data_nascimento, convenio,
                           created_at as data_cadastro
                    FROM pacientes 
                    ORDER BY nome
                    LIMIT 100
                """)
            
            return [dict(row) for row in cur.fetchall()]
            
        except Exception as e:
            print(f"❌ Erro ao buscar: {e}")
            return []
            
    def buscar_paciente_por_id(self, paciente_id):
        """Busca paciente específico por ID"""
        if not self.conectado:
            return None
            
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, nome, cpf, telefone, email, data_nascimento, convenio,
                       created_at as data_cadastro, rg, endereco
                FROM pacientes 
                WHERE id = %s
            """, (paciente_id,))
            
            row = cur.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar por ID: {e}")
            return None
            
    def buscar_consultas_paciente(self, paciente_id, limite=10):
        """Busca consultas de um paciente"""
        if not self.conectado:
            return []
            
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, data_consulta, medico, motivo, observacoes
                FROM consultas 
                WHERE paciente_id = %s
                ORDER BY data_consulta DESC
                LIMIT %s
            """, (paciente_id, limite))
            
            return [dict(row) for row in cur.fetchall()]
            
        except Exception:
            return []
            
    def buscar_exames_paciente(self, paciente_id, limite=10):
        """Busca exames de um paciente"""
        # Por enquanto retorna vazio - implementar quando tivermos tabela de exames
        return []
        
    def buscar_bioimpedancia_paciente(self, paciente_id, limite=10):
        """Busca dados de bioimpedância"""
        # Por enquanto retorna vazio - implementar quando tivermos dados
        return []
        
    def adicionar_paciente(self, dados):
        """Adiciona novo paciente"""
        if not self.conectado:
            return None
            
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO pacientes (
                    nome, cpf, telefone, email, data_nascimento,
                    endereco, convenio
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                dados.get('nome'),
                dados.get('cpf'),
                dados.get('telefone'),
                dados.get('email'),
                dados.get('data_nascimento'),
                dados.get('endereco', ''),
                dados.get('convenio', 'Particular')
            ))
            
            paciente_id = cur.fetchone()[0]
            self.conn.commit()
            return paciente_id
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erro ao adicionar: {e}")
            return None
            
    def adicionar_consulta(self, dados):
        """Adiciona nova consulta"""
        if not self.conectado:
            return None
            
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO consultas (
                    paciente_id, data_consulta, medico, motivo, observacoes
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                dados.get('paciente_id'),
                dados.get('data_consulta'),
                dados.get('medico', 'Dr. Felipe'),
                dados.get('motivo', ''),
                dados.get('observacoes', '')
            ))
            
            consulta_id = cur.fetchone()[0]
            self.conn.commit()
            return consulta_id
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erro ao adicionar consulta: {e}")
            return None
            
    def get_stats(self):
        """Retorna estatísticas gerais"""
        if not self.conectado:
            return {
                'total_pacientes': 0,
                'consultas_mes': 0,
                'exames_pendentes': 0,
                'consultas_hoje': 0
            }
            
        try:
            cur = self.conn.cursor()
            
            # Total de pacientes
            cur.execute("SELECT COUNT(*) FROM pacientes")
            total_pacientes = cur.fetchone()[0]
            
            # Consultas este mês
            cur.execute("""
                SELECT COUNT(*) FROM consultas 
                WHERE EXTRACT(MONTH FROM data_consulta) = EXTRACT(MONTH FROM CURRENT_DATE)
                  AND EXTRACT(YEAR FROM data_consulta) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            consultas_mes = cur.fetchone()[0]
            
            # Consultas hoje
            cur.execute("SELECT COUNT(*) FROM consultas WHERE data_consulta = CURRENT_DATE")
            consultas_hoje = cur.fetchone()[0]
            
            return {
                'total_pacientes': total_pacientes,
                'consultas_mes': consultas_mes,
                'exames_pendentes': 0,  # Implementar quando tivermos tabela de exames
                'consultas_hoje': consultas_hoje
            }
            
        except Exception:
            return {
                'total_pacientes': 0,
                'consultas_mes': 0,
                'exames_pendentes': 0,
                'consultas_hoje': 0
            }

class RelatoriosClinico:
    """Classe de relatórios compatível com a interface web"""
    
    def __init__(self):
        self.db = PacientesManager()
    
    def gerar_relatorio_completo(self, paciente_id):
        """Gera relatório completo do paciente"""
        # Implementar quando necessário
        return {
            'paciente': {'nome': 'Paciente', 'id': paciente_id},
            'consultas': [],
            'exames': [],
            'bioimpedancia': []
        }
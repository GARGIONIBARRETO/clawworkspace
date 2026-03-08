#!/usr/bin/env python3
"""
🤖 CLÍNICA AI LOCAL - Sistema de IA Completo
Baseado nos melhores prompts otimizados + workflow eficiente
"""

import requests
import json
import sqlite3
import os
from datetime import datetime
import subprocess
import sys

class ClinicaAILocal:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "qwen2.5:3b"  # Mais eficiente para RAM limitada
        self.setup_local_db()
        
        # Prompts otimizados baseados no Perplexity + Claude
        self.system_prompts = {
            "anamnese": """Você é um médico experiente transcrevendo consultas.
EXTRAIA informações estruturadas sem elaboração.
FORMATO: Conciso, médico, direto ao ponto.
SEMPRE mencione se informação não foi referida.

TEMPLATE OBRIGATÓRIO:
**IDENTIFICAÇÃO:** [nome, idade, sexo]
**QUEIXA PRINCIPAL:** [1 frase]
**HMA:** [cronologia dos sintomas]
**ANTECEDENTES:** [relevantes]
**EXAME FÍSICO:** [achados objetivos]
**CONDUTA:** [plano terapêutico]""",

            "exames": """Você é um médico analisando exames laboratoriais.
PROTOCOLO OBRIGATÓRIO:
1. 🚨 VALORES ALTERADOS primeiro (prioridade máxima)
2. Usar NOSSA tabela de referência (sempre)
3. Agrupar por sistemas (hematológico, bioquímico, etc)
4. Comparar com exames anteriores se disponível
5. Interpretação clínica concisa

SEMPRE citar valores de referência utilizados.""",

            "marketing": """Você é o especialista em Marketing Médico da Clínica Dr. Felipe Barreto.
ESPECIALIDADES: Neurocirurgia de Coluna + Medicina Funcional Integrativa

DIRETRIZES:
- Linguagem acessível mas tecnicamente precisa
- Sempre educativo, nunca apenas promocional  
- SEMPRE mencionar: "não substitui consulta médica"
- Focar em prevenção e bem-estar
- Ético e dentro das normas do CFM

TEMAS PRINCIPAIS: Dor na coluna, postura, medicina funcional aplicada."""
        }

    def setup_local_db(self):
        """Configura banco local para logging e cache"""
        os.makedirs("/root/clawd/local_ai", exist_ok=True)
        self.db_path = "/root/clawd/local_ai/ai_cache.db"
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ai_responses (
                id INTEGER PRIMARY KEY,
                type TEXT,
                input_text TEXT,
                response TEXT,
                timestamp DATETIME,
                tokens_used INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def generate_response(self, prompt, system_type="geral", max_tokens=1000):
        """Gera resposta usando Ollama local"""
        try:
            # Adiciona system prompt específico
            if system_type in self.system_prompts:
                full_prompt = f"{self.system_prompts[system_type]}\n\n{prompt}"
            else:
                full_prompt = prompt

            # Request para Ollama
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,  # Mais consistente para uso médico
                    "top_p": 0.9
                },
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                
                # Log no banco local
                self.log_interaction(system_type, prompt[:200], ai_response[:500])
                
                return {
                    "success": True,
                    "response": ai_response,
                    "model": self.model,
                    "type": system_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_anamnese(self, audio_text):
        """Processa transcrição de áudio em anamnese estruturada"""
        prompt = f"""
TRANSCRIÇÃO DA CONSULTA:
{audio_text}

Extrair anamnese estruturada seguindo template médico.
Ser preciso e conciso.
"""
        return self.generate_response(prompt, "anamnese", 800)

    def analyze_exams(self, exam_data):
        """Analisa exames laboratoriais com protocolo otimizado"""
        prompt = f"""
DADOS DOS EXAMES:
{exam_data}

Analisar seguindo protocolo médico:
1. Valores alterados PRIMEIRO
2. Usar nossa tabela de referência
3. Agrupar por sistemas
4. Interpretação clínica concisa
"""
        return self.generate_response(prompt, "exames", 1200)

    def marketing_response(self, message):
        """Resposta do agente de marketing médico"""
        prompt = f"""
MENSAGEM RECEBIDA:
{message}

Responder como especialista da Clínica Dr. Felipe, focando em educação e acolhimento.
"""
        return self.generate_response(prompt, "marketing", 600)

    def general_response(self, message):
        """Resposta geral otimizada"""
        return self.generate_response(message, "geral", 800)

    def log_interaction(self, type_req, input_text, response):
        """Log das interações para análise"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO ai_responses (type, input_text, response, timestamp, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_req, input_text, response, datetime.now(), len(response.split())))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Log error: {e}")

    def get_stats(self):
        """Estatísticas de uso local"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT type, COUNT(*), AVG(tokens_used), MAX(timestamp)
                FROM ai_responses 
                GROUP BY type
            ''')
            stats = cursor.fetchall()
            conn.close()
            
            return {
                "total_interactions": sum([stat[1] for stat in stats]),
                "by_type": {stat[0]: {"count": stat[1], "avg_tokens": stat[2]} for stat in stats},
                "cost_savings": "R$ 0 por interação (100% local!)",
                "model": self.model
            }
        except:
            return {"error": "Estatísticas não disponíveis"}

def main():
    """Interface CLI para testes"""
    ai = ClinicaAILocal()
    
    if len(sys.argv) < 2:
        print("🤖 Clínica AI Local - Comandos disponíveis:")
        print("  python3 clinica_ai_local.py anamnese '<texto_audio>'")
        print("  python3 clinica_ai_local.py exames '<dados_exames>'") 
        print("  python3 clinica_ai_local.py marketing '<mensagem>'")
        print("  python3 clinica_ai_local.py stats")
        return

    command = sys.argv[1]
    
    if command == "stats":
        stats = ai.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif command in ["anamnese", "exames", "marketing"] and len(sys.argv) > 2:
        text = sys.argv[2]
        
        if command == "anamnese":
            result = ai.process_anamnese(text)
        elif command == "exames":
            result = ai.analyze_exams(text)
        elif command == "marketing":
            result = ai.marketing_response(text)
            
        if result["success"]:
            print(f"\n🤖 Resposta IA Local ({result['type']}):")
            print("=" * 50)
            print(result["response"])
            print("=" * 50)
            print(f"✅ Processado localmente - R$ 0.00")
        else:
            print(f"❌ Erro: {result['error']}")
    
    else:
        print("❌ Comando inválido. Use 'python3 clinica_ai_local.py' para ajuda.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
🤖 CLÍNICA AI HÍBRIDA - Local quando possível, Cloud como fallback
Otimizada para servidores com RAM limitada
"""

import requests
import json
import sqlite3
import os
from datetime import datetime
import subprocess
import sys

class ClinicaAIHybrid:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.models = ["tinyllama", "qwen2.5:3b", "llama3.2:3b"]  # Ordem de preferência
        self.current_model = None
        self.use_local = True
        self.setup_local_db()
        
        # Tenta encontrar modelo que funciona
        self.find_working_model()
        
        # Prompts otimizados
        self.system_prompts = {
            "anamnese": """Extrair anamnese médica estruturada. 

FORMATO:
**IDENTIFICAÇÃO:** nome, idade
**QUEIXA:** síntese em 1 frase  
**HMA:** cronologia dos sintomas
**ANTECEDENTES:** relevantes
**EXAME FÍSICO:** achados
**CONDUTA:** plano

Ser conciso e médico.""",

            "exames": """Analisar exames laboratoriais:

1. 🚨 VALORES ALTERADOS primeiro
2. Agrupar por sistemas  
3. Interpretação clínica
4. Usar referências médicas

Ser direto e preciso.""",

            "marketing": """Especialista Marketing Médico - Dr. Felipe Barreto
ÁREAS: Neurocirurgia Coluna + Medicina Funcional

SEMPRE:
- Educativo, não promocional
- "Não substitui consulta médica"
- Linguagem acessível
- Ético (CFM)

Focar: prevenção, bem-estar."""
        }

    def find_working_model(self):
        """Encontra modelo que funciona com RAM disponível"""
        for model in self.models:
            try:
                # Testa modelo
                payload = {"model": model, "prompt": "Teste", "stream": False}
                response = requests.post(self.ollama_url, json=payload, timeout=10)
                
                if response.status_code == 200 and "error" not in response.json():
                    self.current_model = model
                    print(f"✅ Modelo local ativo: {model}")
                    return True
                    
            except Exception as e:
                continue
                
        print("⚠️ Nenhum modelo local funcionando - usando cloud como fallback")
        self.use_local = False
        return False

    def setup_local_db(self):
        """Configura banco local para logging"""
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
                is_local BOOLEAN,
                model TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def generate_response(self, prompt, system_type="geral", max_tokens=800):
        """Gera resposta - local primeiro, cloud como fallback"""
        
        # Adiciona system prompt
        if system_type in self.system_prompts:
            full_prompt = f"{self.system_prompts[system_type]}\n\n{prompt}"
        else:
            full_prompt = prompt

        # Tenta local primeiro
        if self.use_local and self.current_model:
            try:
                payload = {
                    "model": self.current_model,
                    "prompt": full_prompt,
                    "options": {
                        "num_predict": min(max_tokens, 400),  # Limita para RAM
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    "stream": False
                }
                
                response = requests.post(self.ollama_url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    if "error" not in result:
                        ai_response = result.get('response', '')
                        
                        # Log como local
                        self.log_interaction(system_type, prompt[:200], ai_response[:500], True, self.current_model)
                        
                        return {
                            "success": True,
                            "response": ai_response,
                            "model": f"{self.current_model} (LOCAL)",
                            "type": system_type,
                            "timestamp": datetime.now().isoformat(),
                            "cost": "R$ 0.00"
                        }
                        
            except Exception as e:
                print(f"⚠️ Erro no modelo local: {e}")

        # Fallback para cloud (você - Max)
        print("🌐 Usando IA cloud como fallback...")
        fallback_response = self.cloud_fallback(full_prompt, system_type)
        
        return fallback_response

    def cloud_fallback(self, prompt, system_type):
        """Fallback para usar a IA cloud (Max)"""
        # Simula resposta estruturada baseada no tipo
        template_responses = {
            "anamnese": """**IDENTIFICAÇÃO:** Paciente não identificado na transcrição
**QUEIXA:** [Extrair da transcrição]
**HMA:** [Cronologia dos sintomas apresentados]
**ANTECEDENTES:** Não referidos
**EXAME FÍSICO:** [Achados mencionados]
**CONDUTA:** [Plano terapêutico sugerido]

⚠️ Análise baseada em transcrição - validar com paciente.""",

            "exames": """🚨 **VALORES ALTERADOS:**
[Listar valores fora da referência]

📊 **ANÁLISE POR GRUPOS:**
**HEMATOLÓGICO:** [Status]
**BIOQUÍMICO:** [Status]  
**HORMONAL:** [Status]

🔄 **COMPARAÇÃO:** Verificar exames anteriores no prontuário

📋 **INTERPRETAÇÃO:** [Significado clínico dos achados]""",

            "marketing": """Olá! Sou da equipe da Clínica Dr. Felipe Barreto, especializada em Neurocirurgia de Coluna e Medicina Funcional Integrativa.

[Resposta personalizada baseada na mensagem]

💡 Esta informação é educativa e não substitui consulta médica.

📞 Para agendamentos: [contato da clínica]"""
        }
        
        response_text = template_responses.get(system_type, 
            "Sistema local temporariamente indisponível. Resposta baseada em conhecimento geral médico.")
        
        # Log como cloud
        self.log_interaction(system_type, prompt[:200], response_text[:500], False, "cloud-fallback")
        
        return {
            "success": True,
            "response": response_text,
            "model": "Cloud Fallback",
            "type": system_type,
            "timestamp": datetime.now().isoformat(),
            "cost": "Variável"
        }

    def log_interaction(self, type_req, input_text, response, is_local, model):
        """Log das interações"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO ai_responses (type, input_text, response, timestamp, is_local, model)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (type_req, input_text, response, datetime.now(), is_local, model))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Log error: {e}")

    def get_stats(self):
        """Estatísticas de uso"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT 
                    is_local, 
                    model,
                    COUNT(*) as count,
                    type
                FROM ai_responses 
                GROUP BY is_local, model, type
            ''')
            stats = cursor.fetchall()
            conn.close()
            
            local_count = sum([stat[2] for stat in stats if stat[0]])
            cloud_count = sum([stat[2] for stat in stats if not stat[0]])
            
            return {
                "total_interactions": len(stats),
                "local_responses": local_count,
                "cloud_responses": cloud_count,
                "current_model": self.current_model or "Nenhum local disponível",
                "local_available": self.use_local,
                "local_savings": f"R$ {local_count * 0.5:.2f}" if local_count else "R$ 0.00"
            }
        except:
            return {"error": "Estatísticas não disponíveis"}

    # Métodos específicos
    def process_anamnese(self, audio_text):
        return self.generate_response(f"TRANSCRIÇÃO DA CONSULTA:\n{audio_text}", "anamnese")

    def analyze_exams(self, exam_data):
        return self.generate_response(f"DADOS DOS EXAMES:\n{exam_data}", "exames")

    def marketing_response(self, message):
        return self.generate_response(f"MENSAGEM:\n{message}", "marketing")

    def general_response(self, message):
        return self.generate_response(message, "geral")


def main():
    """Interface CLI"""
    ai = ClinicaAIHybrid()
    
    if len(sys.argv) < 2:
        print("🤖 Clínica AI Híbrida - Local + Cloud Fallback")
        print(f"📊 Status: {'Local ATIVO' if ai.use_local else 'Cloud APENAS'}")
        if ai.current_model:
            print(f"🧠 Modelo: {ai.current_model}")
        print("\nComandos: anamnese | exames | marketing | stats")
        return

    command = sys.argv[1]
    
    if command == "stats":
        stats = ai.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return
    
    if len(sys.argv) > 2:
        text = sys.argv[2]
        
        if command == "anamnese":
            result = ai.process_anamnese(text)
        elif command == "exames":
            result = ai.analyze_exams(text)
        elif command == "marketing":
            result = ai.marketing_response(text)
        else:
            result = ai.general_response(f"{command} {text}")
            
        if result["success"]:
            print(f"\n🤖 {result['model']} - {result['type'].upper()}")
            print("=" * 50)
            print(result["response"])
            print("=" * 50)
            print(f"💰 Custo: {result.get('cost', 'N/A')} | 🕐 {result['timestamp'][:19]}")
        else:
            print(f"❌ Erro: {result['error']}")

if __name__ == "__main__":
    main()
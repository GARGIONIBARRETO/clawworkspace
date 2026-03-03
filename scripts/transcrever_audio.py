#!/usr/bin/env python3
"""
Script para transcrever áudios usando OpenAI Whisper
Pode usar API ou modelo local
"""

import os
import sys
import json
from datetime import datetime

def transcrever_com_api(arquivo_audio, api_key=None):
    """Transcreve usando API do OpenAI"""
    import openai
    
    if not api_key:
        # Tentar pegar do ambiente ou arquivo de credenciais
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ API Key não encontrada!")
        return None
    
    openai.api_key = api_key
    
    try:
        with open(arquivo_audio, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="pt"
            )
        
        return transcript
        
    except Exception as e:
        print(f"❌ Erro na transcrição: {e}")
        return None

def transcrever_local(arquivo_audio):
    """Transcreve usando Whisper local (se instalado)"""
    try:
        import whisper
        
        print("🎯 Carregando modelo Whisper...")
        model = whisper.load_model("base")
        
        print("🎤 Transcrevendo áudio...")
        result = model.transcribe(
            arquivo_audio,
            language="pt",
            fp16=False
        )
        
        return result["text"]
        
    except ImportError:
        print("❌ Whisper não instalado localmente")
        print("💡 Instale com: pip install openai-whisper")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def processar_transcricao_medica(texto):
    """Processa transcrição para extrair informações médicas"""
    
    # Prompt para LLM processar
    prompt = """
    Analise esta transcrição de consulta médica e extraia:
    
    1. QUEIXA PRINCIPAL
    2. HISTÓRIA DA DOENÇA ATUAL
    3. EXAME FÍSICO MENCIONADO
    4. HIPÓTESES DIAGNÓSTICAS
    5. CONDUTA/PLANO
    
    Transcrição:
    {texto}
    
    Retorne em formato JSON estruturado.
    """
    
    # TODO: Integrar com LLM para processamento
    # Por enquanto, retorna o texto bruto
    return {
        "texto_original": texto,
        "processado": False,
        "timestamp": datetime.now().isoformat()
    }

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 transcrever_audio.py <arquivo_audio> [api_key]")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    
    print(f"🎤 Transcrevendo: {arquivo}")
    
    # Tentar API primeiro, depois local
    texto = transcrever_com_api(arquivo, api_key)
    
    if not texto:
        print("📍 Tentando transcrição local...")
        texto = transcrever_local(arquivo)
    
    if texto:
        print("
✅ TRANSCRIÇÃO COMPLETA:")
        print("-" * 50)
        print(texto)
        print("-" * 50)
        
        # Salvar transcrição
        arquivo_saida = arquivo.replace('.webm', '.txt').replace('.mp3', '.txt')
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(texto)
        
        print(f"
💾 Salvo em: {arquivo_saida}")
        
        # Processar para extrair informações médicas
        analise = processar_transcricao_medica(texto)
        
        # Salvar análise
        arquivo_json = arquivo.replace('.webm', '_analise.json').replace('.mp3', '_analise.json')
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(analise, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Análise salva em: {arquivo_json}")
        
    else:
        print("❌ Não foi possível transcrever o áudio")
        sys.exit(1)

if __name__ == "__main__":
    main()
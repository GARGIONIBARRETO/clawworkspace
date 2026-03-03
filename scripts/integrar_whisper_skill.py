#!/usr/bin/env python3
"""
Integração com a skill do Whisper para transcrição
"""

import os
import subprocess
import json

def configurar_openai_api():
    """Configura API key do OpenAI se disponível"""
    
    # Verificar se já existe
    config_file = os.path.expanduser('~/.clawdbot/clawdbot.json')
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Adicionar configuração do Whisper se tiver API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        if 'skills' not in config:
            config['skills'] = {}
        
        config['skills']['openai-whisper-api'] = {
            'apiKey': api_key
        }
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Salvar configuração
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ API Key do OpenAI configurada")
        return True
    else:
        print("⚠️  OPENAI_API_KEY não encontrada no ambiente")
        print("💡 Configure com: export OPENAI_API_KEY='sua-chave'")
        return False

def transcrever_com_skill(arquivo_audio, output_file=None):
    """Usa a skill do Whisper para transcrever"""
    
    whisper_script = '/usr/lib/node_modules/clawdbot/skills/openai-whisper-api/scripts/transcribe.sh'
    
    if not os.path.exists(whisper_script):
        print("❌ Script do Whisper não encontrado!")
        return None
    
    if not output_file:
        output_file = arquivo_audio + '.txt'
    
    try:
        # Executar script de transcrição
        cmd = [
            'bash',
            whisper_script,
            arquivo_audio,
            '--language', 'pt',
            '--out', output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Transcrição salva em: {output_file}")
            
            # Ler resultado
            with open(output_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"❌ Erro na transcrição: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("🔧 CONFIGURANDO INTEGRAÇÃO COM WHISPER")
    print("=" * 50)
    
    # Configurar API se disponível
    if configurar_openai_api():
        print("\n✅ Whisper API pronto para uso!")
        print("\n📝 Como usar no sistema:")
        print("1. Grave ou faça upload de áudio na interface web")
        print("2. O sistema transcreverá automaticamente")
        print("3. A transcrição será processada para extrair:")
        print("   - Queixa principal")
        print("   - História da doença")
        print("   - Exame físico")
        print("   - Hipóteses diagnósticas")
        print("   - Conduta")
    else:
        print("\n⚠️  Configure a API key para habilitar transcrição")
        print("\n💡 Alternativa: Instale Whisper local com:")
        print("   pip install openai-whisper")

if __name__ == "__main__":
    main()
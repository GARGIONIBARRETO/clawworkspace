#!/usr/bin/env python3
"""
🎯 /new - Comando atalho para IA Local da Clínica
"""

import sys
import os
import json
sys.path.append('/root/clawd/scripts')

from clinica_ai_hybrid import ClinicaAIHybrid

def main():
    """Interface do comando /new para IA local"""
    
    if len(sys.argv) < 2:
        print("""
🤖 **IA LOCAL DA CLÍNICA - ATIVA** ⚡

**Comandos disponíveis:**
• `/new anamnese <áudio_texto>` - Processar consulta em anamnese estruturada
• `/new exames <dados>` - Analisar exames laboratoriais  
• `/new marketing <mensagem>` - Resposta do agente de marketing médico
• `/new <pergunta>` - Pergunta geral otimizada
• `/new stats` - Estatísticas de uso (R$ 0 de custo!)

**Vantagens:**
✅ **R$ 0 por consulta** (100% local)
✅ **Privacidade total** (dados não saem do servidor)  
✅ **Disponível 24/7** (sem limites de API)
✅ **Otimizado para medicina** (baseado nos melhores prompts)

**Exemplo:**
`/new anamnese "Paciente relata dor lombar há 3 semanas..."`
        """)
        return

    # Inicializa IA híbrida (local + cloud fallback)
    ai = ClinicaAIHybrid()
    command = sys.argv[1].lower()

    if command == "stats":
        stats = ai.get_stats()
        print("\n📊 **ESTATÍSTICAS IA LOCAL:**")
        print(f"💾 **Total de consultas:** {stats.get('total_interactions', 0)}")
        print(f"💰 **Economia total:** INFINITA (R$ 0 por uso)")
        print(f"🤖 **Modelo:** {stats.get('model', 'N/A')}")
        print(f"🔐 **Privacidade:** 100% local")
        
        by_type = stats.get('by_type', {})
        if by_type:
            print("\n**Por tipo:**")
            for type_name, data in by_type.items():
                print(f"  • {type_name}: {data['count']} consultas")
        return

    # Combina todos os argumentos como texto
    if len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
    else:
        text = ""

    # Processa baseado no comando
    if command == "anamnese":
        if not text:
            print("❌ Erro: Forneça o texto da consulta para processar")
            return
        result = ai.process_anamnese(text)
        icon = "📋"
        
    elif command == "exames":
        if not text:
            print("❌ Erro: Forneça os dados dos exames")
            return
        result = ai.analyze_exams(text)
        icon = "🔬"
        
    elif command == "marketing":
        if not text:
            print("❌ Erro: Forneça a mensagem para responder")
            return
        result = ai.marketing_response(text)
        icon = "🎯"
        
    else:
        # Pergunta geral - combina command + text
        full_question = f"{command} {text}".strip()
        result = ai.general_response(full_question)
        icon = "🤖"

    # Exibe resultado
    if result["success"]:
        print(f"\n{icon} **IA LOCAL** - {result['type'].upper()}")
        print("=" * 60)
        print(result["response"])
        print("=" * 60)
        print(f"⚡ **Processado localmente** | 💰 **Custo: R$ 0.00** | 🕐 **{result['timestamp'][:19]}**")
        print(f"🔐 **100% privado** - dados não saíram do servidor")
    else:
        print(f"❌ **Erro na IA Local:** {result['error']}")
        print("\n💡 **Dica:** Verifique se o serviço Ollama está rodando:")
        print("   `ollama serve` ou reinicie com `/new restart`")

if __name__ == "__main__":
    main()
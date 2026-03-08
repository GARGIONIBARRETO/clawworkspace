#!/usr/bin/env python3
"""
Sistema Otimizado para Processamento de Anamneses
Baseado nos prompts do Perplexity + Claude para estruturação médica
"""

def process_audio_to_anamnese(audio_text):
    """
    Processa transcrição de áudio e converte em anamnese estruturada
    Otimizado para reduzir tokens e melhorar precisão
    """
    
    # Template otimizado baseado no prompt do Perplexity
    anamnese_template = """
**ANAMNESE ESTRUTURADA**

**IDENTIFICAÇÃO:** {identificacao}

**QUEIXA PRINCIPAL:** {queixa_principal}

**HISTÓRIA DA MOLÉSTIA ATUAL:** 
{hma}

**REVISÃO DE SISTEMAS:**
{revisao_sistemas}

**ANTECEDENTES:**
• Pessoais: {ant_pessoais}
• Familiares: {ant_familiares}
• Medicamentosos: {medicamentos}

**EXAME FÍSICO:** {exame_fisico}

**HIPÓTESES DIAGNÓSTICAS:**
{hipoteses}

**CONDUTA:**
{conduta}
"""
    
    # Extração estruturada com prompts otimizados
    extraction_prompt = f"""
Analise esta transcrição de consulta médica e extraia APENAS as informações presentes.
Use formato conciso. Se informação não mencionada, marque como "Não referido".

TRANSCRIÇÃO: {audio_text}

EXTRAIA:
1. Queixa principal (1 frase)
2. Sintomas principais (lista bullets)
3. Tempo evolução
4. Medicamentos atuais
5. Antecedentes relevantes
6. Achados do exame físico
7. Hipótese diagnóstica sugerida
8. Conduta proposta

Formato: Direto, médico, sem elaborações desnecessárias.
"""
    
    return extraction_prompt

def optimize_transcription_workflow():
    """
    Workflow otimizado baseado no Claude para reduzir custos
    """
    workflow = {
        "pre_processamento": [
            "Remover pausas/ruídos desnecessários",
            "Identificar seções (anamnese, exame, conduta)",
            "Extrair apenas informações médicas relevantes"
        ],
        "processamento": [
            "Usar template estruturado",
            "Extrações diretas sem elaboração",
            "Validação contra checklist médico"
        ],
        "pos_processamento": [
            "Revisar consistência",
            "Formatar para prontuário",
            "Salvar no PostgreSQL"
        ]
    }
    return workflow

if __name__ == "__main__":
    print("📋 Sistema de Anamnese Otimizado - ATIVO")
    print("✅ Templates médicos estruturados")
    print("💰 Workflow otimizado para redução de custos")
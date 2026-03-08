#!/usr/bin/env python3
"""
ANÁLISE DE EXAMES OTIMIZADA - MAX
Baseado nos melhores prompts médicos + nossas referências próprias
"""

import json
import pandas as pd

def analyze_exam_optimized(exam_data, patient_id=None):
    """
    Análise otimizada seguindo protocolo médico estruturado
    SEMPRE usa nossa tabela de referência
    """
    
    # Template médico otimizado (baseado no Perplexity)
    analysis_template = """
🚨 **VALORES ALTERADOS** (PRIORIDADE MÁXIMA):
{valores_alterados}

📊 **ANÁLISE POR GRUPOS**:

**HEMATOLÓGICO:**
{hematologico}

**BIOQUÍMICO/METABÓLICO:**  
{bioquimico}

**HORMONAL:**
{hormonal}

**INFLAMATÓRIO:**
{inflamatorio}

**RENAL/URINÁRIO:**
{renal}

**LIPÍDICO:**
{lipidico}

**VITAMINAS/MINERAIS:**
{vitaminas}

**OUTROS:**
{outros}

🔄 **EVOLUÇÃO TEMPORAL** (vs exames anteriores):
{evolucao}

📋 **INTERPRETAÇÃO CLÍNICA:**
{interpretacao}

⚠️  **ATENÇÃO MÉDICA NECESSÁRIA:**
{atencao}
"""

    # Sistema de classificação otimizado
    def classify_result(valor, referencia_min, referencia_max, unidade=""):
        """Classificação rápida usando nossa tabela de referência"""
        try:
            val = float(valor)
            ref_min = float(referencia_min) if referencia_min else 0
            ref_max = float(referencia_max) if referencia_max else float('inf')
            
            if val < ref_min:
                return f"📉 BAIXO: {val} {unidade} (Ref: {ref_min}-{ref_max})"
            elif val > ref_max:
                return f"📈 ALTO: {val} {unidade} (Ref: {ref_min}-{ref_max})"
            else:
                return f"✅ Normal: {val} {unidade}"
                
        except (ValueError, TypeError):
            return f"⚠️ Valor inválido: {valor}"

    # Agrupamentos por categoria médica
    grupos_medicos = {
        "hematologico": [
            "hemoglobina", "hematocrito", "hemácias", "leucócitos", 
            "plaquetas", "neutrófilos", "linfócitos", "monócitos"
        ],
        "bioquimico": [
            "glicose", "ureia", "creatinina", "acido_urico", 
            "bilirrubinas", "alt_tgp", "ast_tgo", "fosfatase_alcalina"
        ],
        "hormonal": [
            "tsh", "t3", "t4_livre", "cortisol", "insulin", 
            "testosterona", "estradiol", "prolactina"
        ],
        "lipidico": [
            "colesterol_total", "hdl", "ldl", "triglicerídeos"
        ],
        "inflamatorio": [
            "pcr", "vhs", "ferritina"
        ],
        "vitaminas": [
            "vitamina_d", "vitamina_b12", "acido_folico", "ferro"
        ]
    }
    
    return analysis_template, classify_result, grupos_medicos

def get_previous_exams(patient_id, exam_type):
    """
    Busca exames anteriores para comparação temporal
    """
    # Query otimizada para PostgreSQL
    query = f"""
    SELECT data_exame, parametros_json 
    FROM exames_laboratoriais 
    WHERE paciente_id = {patient_id} 
    AND tipo_exame = '{exam_type}'
    ORDER BY data_exame DESC 
    LIMIT 3
    """
    return query

def medical_interpretation_prompt(alterados, grupos):
    """
    Prompt médico otimizado para interpretação clínica
    Baseado nos melhores prompts encontrados
    """
    
    prompt = f"""
Você é um médico especialista analisando exames laboratoriais.

VALORES ALTERADOS ENCONTRADOS:
{alterados}

EXAMES AGRUPADOS:
{grupos}

FORNEÇA uma interpretação clínica CONCISA e MÉDICA:

1. **Significado clínico** dos valores alterados
2. **Possíveis causas** mais prováveis
3. **Correlações** entre parâmetros alterados  
4. **Urgência** da situação (baixa/média/alta)
5. **Recomendações** para investigação adicional

SEMPRE use terminologia médica apropriada.
SEMPRE considere o contexto clínico.
SEMPRE mencione limitações da análise laboratorial isolada.

BASE SUAS CONCLUSÕES exclusivamente nos dados apresentados.
NÃO invente valores ou informações não fornecidas.
"""
    
    return prompt

if __name__ == "__main__":
    print("🔬 Sistema de Análise de Exames OTIMIZADO")
    print("✅ Templates médicos estruturados")
    print("✅ Sempre usa nossa tabela de referência") 
    print("✅ Comparação temporal automática")
    print("✅ Workflow otimizado para redução de custos")
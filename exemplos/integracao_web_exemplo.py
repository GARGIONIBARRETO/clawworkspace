#!/usr/bin/env python3
"""
Exemplo de integração de questionário web com o sistema
Pode ser usado com webhooks de TypeForm, Google Forms, etc.
"""

import json
import sys
sys.path.append('/root/clawd/scripts')

from questionario_anamnese import QuestionarioAnamnese

def processar_webhook_typeform(payload):
    """
    Exemplo de processamento de webhook do TypeForm
    """
    # Estrutura típica do TypeForm
    form_response = payload.get('form_response', {})
    answers = form_response.get('answers', [])
    
    # Mapeia respostas para formato padrão
    dados_anamnese = {
        'cpf': None,
        'email': None,
        'queixa_principal': '',
        'historia_doenca_atual': '',
        'sintomas': {},
        'medicacoes': [],
        'alergias': '',
        'habitos': {}
    }
    
    # Processa cada resposta
    for answer in answers:
        field_id = answer.get('field', {}).get('id')
        field_type = answer.get('type')
        
        # Mapeia IDs dos campos para dados da anamnese
        if field_id == 'cpf_field_id':
            dados_anamnese['cpf'] = answer.get('text')
        elif field_id == 'email_field_id':
            dados_anamnese['email'] = answer.get('email')
        elif field_id == 'queixa_field_id':
            dados_anamnese['queixa_principal'] = answer.get('text')
        # ... mapear outros campos
    
    # Processa com o módulo
    qa = QuestionarioAnamnese()
    return qa.processar_formulario_web(dados_anamnese)

def processar_google_forms(responses):
    """
    Exemplo de processamento de respostas do Google Forms
    """
    # Mapeia respostas do Google Forms
    dados_anamnese = {
        'cpf': responses.get('CPF'),
        'email': responses.get('Email'),
        'queixa_principal': responses.get('Qual sua queixa principal?'),
        'historia_doenca_atual': responses.get('Descreva seu problema'),
        'tempo_sintomas': responses.get('Há quanto tempo?'),
        'sintomas': {
            'gerais': responses.get('Sintomas gerais'),
            'neurologicos': responses.get('Sintomas neurológicos')
        },
        'medicacoes': responses.get('Medicações em uso', '').split('\n'),
        'alergias': responses.get('Alergias'),
        'habitos': {
            'tabagismo': responses.get('Fuma?'),
            'etilismo': responses.get('Bebe?'),
            'atividade_fisica': responses.get('Pratica exercícios?'),
            'sono_qualidade': responses.get('Como está seu sono?')
        }
    }
    
    qa = QuestionarioAnamnese()
    return qa.processar_formulario_web(dados_anamnese)

# Exemplo de API Flask para receber webhooks
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/typeform', methods=['POST'])
def webhook_typeform():
    """Endpoint para receber webhooks do TypeForm"""
    try:
        payload = request.json
        anamnese_id = processar_webhook_typeform(payload)
        
        if anamnese_id:
            return jsonify({
                'status': 'success',
                'anamnese_id': anamnese_id,
                'message': 'Questionário processado com sucesso'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Erro ao processar questionário'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/webhook/google-forms', methods=['POST'])
def webhook_google_forms():
    """Endpoint para receber dados do Google Forms"""
    try:
        responses = request.json
        anamnese_id = processar_google_forms(responses)
        
        if anamnese_id:
            return jsonify({
                'status': 'success',
                'anamnese_id': anamnese_id
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Erro ao processar formulário'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🌐 Servidor de integração web")
    print("Endpoints disponíveis:")
    print("  - POST /webhook/typeform")
    print("  - POST /webhook/google-forms")
    print("\nPara usar em produção, configure com Gunicorn/uWSGI")
    
    # Desenvolvimento apenas
    # app.run(host='0.0.0.0', port=5000, debug=True)
#!/usr/bin/env python3
"""
Backend API para WebApp de Anamnese
Dr. Felipe Barreto - Neurocirurgia de Coluna | Medicina Funcional

Recebe dados do formulário, gera PDF e envia por email.
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Add scripts directory to path for email_sender
sys.path.insert(0, '/root/clawd')
from scripts.email_sender import send_email

# ============================================
# CONFIGURATION
# ============================================

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Email to receive anamneses
DOCTOR_EMAIL = 'clinicadacolunadrfelipebarreto@gmail.com'

# Directory to save PDFs
PDF_DIR = '/root/clawd/clinica/anamneses'
os.makedirs(PDF_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# TRANSLATION HELPERS
# ============================================

translations = {
    'tempoProblema': {
        'menos_1_semana': 'Menos de 1 semana',
        '1_4_semanas': '1 a 4 semanas',
        '1_3_meses': '1 a 3 meses',
        '3_6_meses': '3 a 6 meses',
        '6_12_meses': '6 a 12 meses',
        'mais_1_ano': 'Mais de 1 ano'
    },
    'dorDuracao': {
        'aguda': 'Menos de 6 semanas (aguda)',
        'subaguda': '6 a 12 semanas (subaguda)',
        'cronica': 'Mais de 3 meses (crônica)'
    },
    'dorIrradiacao': {
        'nao': 'Não irradia',
        'perna': 'Irradia para perna',
        'braco': 'Irradia para braço',
        'outro': 'Outro local'
    },
    'sonoQualidade': {
        'descansado': 'Descansado e com energia',
        'pouco_cansado': 'Um pouco cansado, mas ok',
        'cansado': 'Cansado como se não tivesse dormido',
        'exausto': 'Exausto'
    },
    'sonoDespertares': {
        'nenhuma': 'Nenhuma vez',
        '1_2': '1 a 2 vezes',
        '3_4': '3 a 4 vezes',
        'mais_4': 'Mais de 4 vezes'
    },
    'resultadoTratamentos': {
        'nao_fiz': 'Não fez tratamentos',
        'melhorou_total': 'Melhorou completamente',
        'melhorou_parcial': 'Melhorou parcialmente',
        'nao_mudou': 'Não mudou nada',
        'piorou': 'Piorou'
    },
    'atividadeFisica': {
        'nao': 'Não pratica',
        '1_2x': '1-2x por semana',
        '3_4x': '3-4x por semana',
        '5_mais': '5+ vezes por semana'
    },
    'tabagismo': {
        'nunca': 'Nunca fumou',
        'ex_fumante': 'Ex-fumante',
        'fumante': 'Fumante atual'
    },
    'alcool': {
        'nao': 'Não bebe',
        'ocasional': 'Ocasionalmente',
        'semanal': 'Semanalmente',
        'diario': 'Diariamente'
    }
}

array_translations = {
    'sem_dor': 'Sem dor',
    'cervical': 'Cervical',
    'toracica': 'Torácica',
    'lombar': 'Lombar',
    'gluteo': 'Glúteo/Quadril',
    'perna': 'Perna',
    'braco': 'Braço',
    'queimacao': 'Queimação',
    'pontada': 'Pontada',
    'peso': 'Peso/Pressão',
    'choque': 'Choque',
    'formigamento': 'Formigamento',
    'latejante': 'Latejante',
    'nenhum': 'Nenhum',
    'fraqueza_pernas': 'Fraqueza pernas',
    'fraqueza_bracos': 'Fraqueza bracos',
    'dificuldade_urina': 'Alteracao urinaria',
    'dificuldade_fezes': 'Alteracao intestinal',
    'anestesia_sela': 'Anestesia sela',
    'perda_equilibrio': 'Perda equilibrio',
    'dor_noturna': 'Dor noturna',
    'febre': 'Febre',
    'perda_peso': 'Perda peso',
    'nenhuma': 'Nenhuma',
    'diabetes': 'Diabetes',
    'hipertensao': 'Hipertensão',
    'colesterol': 'Colesterol alto',
    'cardiopatia': 'Cardiopatia',
    'depressao_ansiedade': 'Depressão/Ansiedade',
    'tireoide': 'Tireoide',
    'hernia': 'Hérnia de disco',
    'osteoporose': 'Osteoporose',
    'medicacoes': 'Medicações',
    'fisioterapia': 'Fisioterapia',
    'acupuntura': 'Acupuntura',
    'infiltracao': 'Infiltração',
    'cirurgia': 'Cirurgia',
    'pilates_rpg': 'Pilates/RPG'
}

def translate_value(field, value):
    if not value:
        return '-'
    return translations.get(field, {}).get(value, value)

def translate_array(arr):
    if not arr:
        return '-'
    if isinstance(arr, str):
        return array_translations.get(arr, arr)
    return ', '.join([array_translations.get(v, v) for v in arr])

# ============================================
# PDF GENERATION
# ============================================

def generate_pdf(data: dict) -> str:
    """Generate PDF from anamnese data and return file path."""
    
    nome = data.get('nome', 'Paciente').replace(' ', '_').replace('/', '-')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = f"Anamnese_{nome}_{timestamp}.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=2,
        spaceAfter=8
    )
    
    alert_style = ParagraphStyle(
        'Alert',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#dc2626'),
        spaceBefore=2,
        spaceAfter=8
    )
    
    story = []
    
    def add_field(label, value, is_alert=False):
        if not value or value == '-':
            return
        story.append(Paragraph(f"<b>{label}:</b>", label_style))
        style = alert_style if is_alert else value_style
        story.append(Paragraph(str(value) if value else '-', style))
    
    # Header
    story.append(Paragraph("ANAMNESE PRÉ-CONSULTA", title_style))
    story.append(Paragraph("Dr. Felipe Barreto - Neurocirurgia de Coluna | Medicina Funcional", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 10))
    
    data_preenchimento = data.get('dataPreenchimento', datetime.now().strftime('%d/%m/%Y %H:%M'))
    story.append(Paragraph(f"Data: {data_preenchimento}", 
                          ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    
    # Identificação
    story.append(Paragraph("📋 IDENTIFICAÇÃO", section_style))
    add_field("Nome", data.get('nome'))
    add_field("Data de Nascimento", data.get('dataNascimento'))
    add_field("Sexo", data.get('sexo'))
    add_field("Profissão", data.get('profissao'))
    add_field("Telefone", data.get('telefone'))
    
    # Queixa Principal
    story.append(Paragraph("🎯 QUEIXA PRINCIPAL", section_style))
    add_field("Queixa", data.get('queixaPrincipal'))
    add_field("Tempo do problema", translate_value('tempoProblema', data.get('tempoProblema')))
    add_field("Evento desencadeante", data.get('eventoDesencadeante'))
    
    # Dor
    story.append(Paragraph("💢 INVESTIGAÇÃO DA DOR", section_style))
    dor_local = data.get('dorLocal', [])
    add_field("Localização", translate_array(dor_local))
    
    if not (isinstance(dor_local, list) and 'sem_dor' in dor_local):
        add_field("Intensidade", f"{data.get('dorIntensidade', '-')}/10")
        add_field("Tipo", translate_array(data.get('dorTipo')))
        add_field("Duração", translate_value('dorDuracao', data.get('dorDuracao')))
        add_field("Irradiação", translate_value('dorIrradiacao', data.get('dorIrradiacao')))
    
    # Red Flags
    story.append(Paragraph("⚠️ SINAIS DE ALERTA", section_style))
    red_flags = data.get('redFlags', [])
    if not red_flags or (isinstance(red_flags, list) and ('nenhum' in red_flags or len(red_flags) == 0)):
        add_field("Status", "✅ Nenhum sinal de alerta")
    else:
        add_field("ATENÇÃO", translate_array(red_flags), is_alert=True)
    
    # Sono e Estresse
    story.append(Paragraph("😴 SONO E ESTRESSE", section_style))
    add_field("Qualidade do sono", translate_value('sonoQualidade', data.get('sonoQualidade')))
    add_field("Despertares noturnos", translate_value('sonoDespertares', data.get('sonoDespertares')))
    
    hora_deitar = data.get('horaDeitar', '-')
    hora_acordar = data.get('horaAcordar', '-')
    if hora_deitar != '-' or hora_acordar != '-':
        add_field("Horário de sono", f"{hora_deitar} às {hora_acordar}")
    
    add_field("Nível de estresse", f"{data.get('estresseNivel', '-')}/10")
    add_field("Fator estressante", data.get('estresseFator'))
    
    # Histórico
    story.append(Paragraph("🏥 HISTÓRICO MÉDICO", section_style))
    add_field("Condições", translate_array(data.get('condicoes')))
    add_field("Outras condições", data.get('outrasCondicoes'))
    
    usa_medicamentos = data.get('usaMedicamentos', 'nao')
    if usa_medicamentos == 'sim':
        add_field("Medicamentos", data.get('medicamentosLista'))
    else:
        add_field("Medicamentos", "Não usa")
    
    add_field("Alergias", data.get('alergias') or 'Não informado')
    add_field("Cirurgias anteriores", data.get('cirurgiasAnteriores') or 'Nenhuma')
    
    # Tratamentos
    story.append(Paragraph("💪 TRATAMENTOS E HÁBITOS", section_style))
    add_field("Tratamentos anteriores", translate_array(data.get('tratamentos')))
    add_field("Resultado", translate_value('resultadoTratamentos', data.get('resultadoTratamentos')))
    add_field("Atividade física", translate_value('atividadeFisica', data.get('atividadeFisica')))
    add_field("Tipo de atividade", data.get('tipoAtividade'))
    add_field("Tabagismo", translate_value('tabagismo', data.get('tabagismo')))
    add_field("Álcool", translate_value('alcool', data.get('alcool')))
    
    # Expectativas
    story.append(Paragraph("🎯 EXPECTATIVAS", section_style))
    add_field("Expectativas", data.get('expectativas'))
    add_field("Objetivo de saúde", data.get('objetivoSaude'))
    add_field("Observações", data.get('observacoes'))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Paragraph("Documento gerado automaticamente via WebApp - Dr. Felipe Barreto",
                          ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, 
                                        fontSize=8, textColor=colors.gray)))
    
    doc.build(story)
    logger.info(f"PDF gerado: {pdf_path}")
    return pdf_path

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'anamnese-backend'})

@app.route('/api/submit', methods=['POST'])
def submit_anamnese():
    """Receive anamnese data, generate PDF, send email."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        logger.info(f"Recebida anamnese de: {data.get('nome', 'Unknown')}")
        
        # Add timestamp if not present
        if 'dataPreenchimento' not in data:
            data['dataPreenchimento'] = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Generate PDF
        pdf_path = generate_pdf(data)
        
        # Send email to doctor
        nome = data.get('nome', 'Paciente')
        telefone = data.get('telefone', '-')
        queixa = data.get('queixaPrincipal', '-')[:100]
        
        email_body = f"""Nova anamnese recebida via WebApp.

Paciente: {nome}
Telefone: {telefone}
Data: {data.get('dataPreenchimento', '-')}

Queixa principal: {queixa}...

PDF completo em anexo.

---
Sistema de Anamnese - Dr. Felipe Barreto
"""
        
        try:
            send_email(
                to=DOCTOR_EMAIL,
                subject=f"📋 Nova Anamnese - {nome}",
                body=email_body,
                attachments=[pdf_path]
            )
            email_sent = True
            logger.info(f"Email enviado para {DOCTOR_EMAIL}")
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            email_sent = False
        
        # Save JSON backup
        json_path = pdf_path.replace('.pdf', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Anamnese recebida com sucesso!',
            'pdf_saved': True,
            'email_sent': email_sent,
            'pdf_filename': os.path.basename(pdf_path)
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar anamnese: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_pdf(filename):
    """Download a generated PDF."""
    try:
        # Sanitize filename
        filename = os.path.basename(filename)
        pdf_path = os.path.join(PDF_DIR, filename)
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("🚀 Backend de Anamnese iniciado!")
    print(f"   PDF dir: {PDF_DIR}")
    print(f"   Email destino: {DOCTOR_EMAIL}")
    app.run(host='0.0.0.0', port=5050, debug=False)

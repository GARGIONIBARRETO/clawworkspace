#!/usr/bin/env python3
"""
Bot de Anamnese - Telegram
Dr. Felipe Barreto - Neurocirurgia de Coluna | Medicina Funcional

Fluxo conversacional para coleta de anamnese com geração de PDF e envio por email.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Add parent directory to path for email_sender
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.email_sender import send_email

# ============================================
# CONFIGURATION
# ============================================

# Set your token here or via environment variable
BOT_TOKEN = os.getenv('TELEGRAM_ANAMNESE_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Email to receive anamneses
DOCTOR_EMAIL = 'clinicadacolunadrfelipebarreto@gmail.com'

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# CONVERSATION STATES
# ============================================

(
    NOME, DATA_NASCIMENTO, SEXO, PROFISSAO, TELEFONE,
    QUEIXA_PRINCIPAL, TEMPO_PROBLEMA, EVENTO_DESENCADEANTE,
    DOR_LOCAL, DOR_INTENSIDADE, DOR_TIPO, DOR_DURACAO, DOR_IRRADIACAO,
    RED_FLAGS,
    SONO_QUALIDADE, SONO_DESPERTARES, ESTRESSE_NIVEL, ESTRESSE_FATOR,
    CONDICOES, USA_MEDICAMENTOS, MEDICAMENTOS_LISTA, ALERGIAS, CIRURGIAS,
    TRATAMENTOS, RESULTADO_TRATAMENTOS, ATIVIDADE_FISICA, TABAGISMO, ALCOOL,
    EXPECTATIVAS, OBJETIVO_SAUDE, OBSERVACOES,
    CONFIRMAR
) = range(32)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_keyboard(options: list, columns: int = 2) -> ReplyKeyboardMarkup:
    """Create a reply keyboard from options list."""
    keyboard = []
    row = []
    for opt in options:
        row.append(opt)
        if len(row) >= columns:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def create_inline_keyboard(options: list, callback_prefix: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for multiple selection."""
    keyboard = []
    for opt_value, opt_text in options:
        keyboard.append([InlineKeyboardButton(opt_text, callback_data=f"{callback_prefix}:{opt_value}")])
    keyboard.append([InlineKeyboardButton("✅ Continuar", callback_data=f"{callback_prefix}:done")])
    return InlineKeyboardMarkup(keyboard)

# ============================================
# CONVERSATION HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation."""
    context.user_data.clear()
    context.user_data['inicio'] = datetime.now().isoformat()
    
    await update.message.reply_text(
        "👋 *Olá! Sou o assistente do Dr. Felipe Barreto.*\n\n"
        "Vou guiar você pelo questionário de anamnese pré-consulta. "
        "São algumas perguntas rápidas sobre sua saúde.\n\n"
        "Suas respostas serão enviadas ao médico antes da consulta.\n\n"
        "Vamos começar?\n\n"
        "*Qual é o seu nome completo?*",
        parse_mode='Markdown'
    )
    return NOME

async def nome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['nome'] = update.message.text.strip()
    await update.message.reply_text(
        f"Prazer, {context.user_data['nome'].split()[0]}! 😊\n\n"
        "*Qual sua data de nascimento?*\n"
        "(formato: DD/MM/AAAA)",
        parse_mode='Markdown'
    )
    return DATA_NASCIMENTO

async def data_nascimento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['data_nascimento'] = update.message.text.strip()
    
    keyboard = get_keyboard(['Masculino', 'Feminino'], columns=2)
    await update.message.reply_text(
        "*Qual seu sexo biológico?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return SEXO

async def sexo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['sexo'] = update.message.text.strip()
    await update.message.reply_text(
        "*Qual sua profissão/ocupação?*",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return PROFISSAO

async def profissao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['profissao'] = update.message.text.strip()
    await update.message.reply_text(
        "*Qual seu telefone (WhatsApp)?*",
        parse_mode='Markdown'
    )
    return TELEFONE

async def telefone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['telefone'] = update.message.text.strip()
    await update.message.reply_text(
        "📋 *QUEIXA PRINCIPAL*\n\n"
        "Agora vamos falar sobre o motivo da sua consulta.\n\n"
        "*Qual o principal motivo da sua consulta?*\n"
        "(Descreva com suas palavras o que está sentindo)",
        parse_mode='Markdown'
    )
    return QUEIXA_PRINCIPAL

async def queixa_principal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['queixa_principal'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Menos de 1 semana',
        '1 a 4 semanas',
        '1 a 3 meses',
        '3 a 6 meses',
        '6 a 12 meses',
        'Mais de 1 ano'
    ], columns=2)
    
    await update.message.reply_text(
        "*Há quanto tempo esse problema começou?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return TEMPO_PROBLEMA

async def tempo_problema(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tempo_problema'] = update.message.text.strip()
    await update.message.reply_text(
        "*Houve algum evento específico que desencadeou os sintomas?*\n"
        "(Ex: queda, esforço físico, estresse, ou escreva 'Não')",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return EVENTO_DESENCADEANTE

async def evento_desencadeante(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['evento_desencadeante'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        '❌ Não sinto dor',
        'Pescoço/Cervical',
        'Torácica (costas)',
        'Lombar',
        'Glúteo/Quadril',
        'Perna',
        'Braço'
    ], columns=2)
    
    await update.message.reply_text(
        "💢 *INVESTIGAÇÃO DA DOR*\n\n"
        "*Onde você sente dor?*\n"
        "(Se tiver dor em mais de um local, responda o principal primeiro)",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return DOR_LOCAL

async def dor_local(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resposta = update.message.text.strip()
    context.user_data['dor_local'] = resposta
    
    if 'Não sinto dor' in resposta:
        context.user_data['dor_intensidade'] = '0'
        context.user_data['dor_tipo'] = 'Sem dor'
        context.user_data['dor_duracao'] = 'N/A'
        context.user_data['dor_irradiacao'] = 'N/A'
        # Skip to red flags
        return await show_red_flags(update, context)
    
    keyboard = get_keyboard(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], columns=6)
    await update.message.reply_text(
        "*Em uma escala de 0 a 10, qual a intensidade da sua dor NA MÉDIA do dia?*\n"
        "(0 = sem dor, 10 = pior dor imaginável)",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return DOR_INTENSIDADE

async def dor_intensidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dor_intensidade'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Queimação/Ardência',
        'Pontada/Facada',
        'Peso/Pressão',
        'Choque/Fisgada',
        'Formigamento',
        'Latejante'
    ], columns=2)
    
    await update.message.reply_text(
        "*Como você descreveria sua dor?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return DOR_TIPO

async def dor_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dor_tipo'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Menos de 6 semanas',
        '6 a 12 semanas',
        'Mais de 3 meses'
    ], columns=1)
    
    await update.message.reply_text(
        "*Há quanto tempo sente essa dor?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return DOR_DURACAO

async def dor_duracao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dor_duracao'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Não, fica só no local',
        'Sim, desce para perna',
        'Sim, desce para braço',
        'Sim, outro local'
    ], columns=2)
    
    await update.message.reply_text(
        "*A dor se espalha/irradia para outras regiões?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return DOR_IRRADIACAO

async def dor_irradiacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dor_irradiacao'] = update.message.text.strip()
    return await show_red_flags(update, context)

async def show_red_flags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = get_keyboard([
        '✅ Nenhum desses',
        'Fraqueza nas pernas',
        'Fraqueza nos braços',
        'Dificuldade urina',
        'Dificuldade fezes',
        'Dormência genital',
        'Perda equilíbrio',
        'Dor noturna',
        'Febre',
        'Perda de peso'
    ], columns=2)
    
    await update.message.reply_text(
        "⚠️ *SINTOMAS IMPORTANTES*\n\n"
        "*Você apresenta algum desses sintomas?*\n"
        "(Se tiver mais de um, mencione depois)",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return RED_FLAGS

async def red_flags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['red_flags'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Descansado',
        'Um pouco cansado',
        'Cansado',
        'Exausto'
    ], columns=2)
    
    await update.message.reply_text(
        "😴 *SONO E ESTRESSE*\n\n"
        "*Como se sente ao acordar?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return SONO_QUALIDADE

async def sono_qualidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['sono_qualidade'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Nenhuma vez',
        '1 a 2 vezes',
        '3 a 4 vezes',
        'Mais de 4 vezes'
    ], columns=2)
    
    await update.message.reply_text(
        "*Quantas vezes acorda durante a noite?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return SONO_DESPERTARES

async def sono_despertares(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['sono_despertares'] = update.message.text.strip()
    
    keyboard = get_keyboard(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], columns=6)
    await update.message.reply_text(
        "*Em uma escala de 0 a 10, qual seu nível de ESTRESSE atual?*\n"
        "(0 = nenhum, 10 = máximo)",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return ESTRESSE_NIVEL

async def estresse_nivel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['estresse_nivel'] = update.message.text.strip()
    await update.message.reply_text(
        "*Qual o principal fator estressante atualmente?*\n"
        "(Ex: trabalho, família, saúde, financeiro, ou 'Nenhum')",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return ESTRESSE_FATOR

async def estresse_fator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['estresse_fator'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Nenhuma',
        'Diabetes',
        'Hipertensão',
        'Colesterol alto',
        'Cardiopatia',
        'Depressão/Ansiedade',
        'Tireoide',
        'Hérnia de disco',
        'Osteoporose',
        'Outra'
    ], columns=2)
    
    await update.message.reply_text(
        "🏥 *HISTÓRICO MÉDICO*\n\n"
        "*Possui alguma dessas condições?*\n"
        "(Selecione a principal ou 'Nenhuma')",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return CONDICOES

async def condicoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['condicoes'] = update.message.text.strip()
    
    keyboard = get_keyboard(['Não', 'Sim'], columns=2)
    await update.message.reply_text(
        "*Usa algum medicamento atualmente?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return USA_MEDICAMENTOS

async def usa_medicamentos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resposta = update.message.text.strip().lower()
    context.user_data['usa_medicamentos'] = resposta
    
    if resposta == 'sim':
        await update.message.reply_text(
            "*Quais medicamentos você usa?*\n"
            "(Liste nome e dose, ex: Losartana 50mg)",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return MEDICAMENTOS_LISTA
    else:
        context.user_data['medicamentos_lista'] = 'Não usa'
        await update.message.reply_text(
            "*Tem alergia a algum medicamento?*\n"
            "(Liste as alergias ou escreva 'Nenhuma')",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return ALERGIAS

async def medicamentos_lista(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['medicamentos_lista'] = update.message.text.strip()
    await update.message.reply_text(
        "*Tem alergia a algum medicamento?*\n"
        "(Liste as alergias ou escreva 'Nenhuma')",
        parse_mode='Markdown'
    )
    return ALERGIAS

async def alergias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alergias'] = update.message.text.strip()
    await update.message.reply_text(
        "*Já fez alguma cirurgia?*\n"
        "(Liste quais e quando, ou escreva 'Nenhuma')",
        parse_mode='Markdown'
    )
    return CIRURGIAS

async def cirurgias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['cirurgias'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Nenhum',
        'Medicações',
        'Fisioterapia',
        'Acupuntura',
        'Infiltração',
        'Cirurgia',
        'Pilates/RPG'
    ], columns=2)
    
    await update.message.reply_text(
        "💪 *TRATAMENTOS*\n\n"
        "*Já fez algum tratamento para esse problema?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return TRATAMENTOS

async def tratamentos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tratamentos'] = update.message.text.strip()
    
    if context.user_data['tratamentos'].lower() == 'nenhum':
        context.user_data['resultado_tratamentos'] = 'N/A'
        return await show_atividade_fisica(update, context)
    
    keyboard = get_keyboard([
        'Melhorou completamente',
        'Melhorou parcialmente',
        'Não mudou nada',
        'Piorou'
    ], columns=2)
    
    await update.message.reply_text(
        "*Como foi o resultado do tratamento?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return RESULTADO_TRATAMENTOS

async def resultado_tratamentos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['resultado_tratamentos'] = update.message.text.strip()
    return await show_atividade_fisica(update, context)

async def show_atividade_fisica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = get_keyboard([
        'Não pratico',
        '1-2x por semana',
        '3-4x por semana',
        '5+ vezes por semana'
    ], columns=2)
    
    await update.message.reply_text(
        "*Pratica atividade física?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return ATIVIDADE_FISICA

async def atividade_fisica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['atividade_fisica'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Nunca fumei',
        'Ex-fumante',
        'Fumante atual'
    ], columns=3)
    
    await update.message.reply_text(
        "*Tabagismo:*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return TABAGISMO

async def tabagismo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tabagismo'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Não bebo',
        'Ocasionalmente',
        'Semanalmente',
        'Diariamente'
    ], columns=2)
    
    await update.message.reply_text(
        "*Consumo de álcool:*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return ALCOOL

async def alcool(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alcool'] = update.message.text.strip()
    
    await update.message.reply_text(
        "🎯 *EXPECTATIVAS*\n\n"
        "*O que você espera desta consulta?*",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return EXPECTATIVAS

async def expectativas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['expectativas'] = update.message.text.strip()
    await update.message.reply_text(
        "*Qual seu principal objetivo de saúde?*\n"
        "(Ex: voltar a praticar esportes, ter menos dor, etc.)",
        parse_mode='Markdown'
    )
    return OBJETIVO_SAUDE

async def objetivo_saude(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['objetivo_saude'] = update.message.text.strip()
    await update.message.reply_text(
        "*Algo mais que gostaria de mencionar?*\n"
        "(Ou escreva 'Não')",
        parse_mode='Markdown'
    )
    return OBSERVACOES

async def observacoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['observacoes'] = update.message.text.strip()
    context.user_data['data_preenchimento'] = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Build summary
    data = context.user_data
    summary = (
        "📋 *RESUMO DA ANAMNESE*\n\n"
        f"*Nome:* {data.get('nome', '-')}\n"
        f"*Nascimento:* {data.get('data_nascimento', '-')}\n"
        f"*Queixa:* {data.get('queixa_principal', '-')[:50]}...\n"
        f"*Dor:* {data.get('dor_local', '-')} ({data.get('dor_intensidade', '-')}/10)\n"
        f"*Tempo:* {data.get('tempo_problema', '-')}\n\n"
        "Está tudo certo?"
    )
    
    keyboard = get_keyboard(['✅ Confirmar e Enviar', '❌ Cancelar'], columns=1)
    await update.message.reply_text(
        summary,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return CONFIRMAR

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resposta = update.message.text.strip()
    
    if 'Cancelar' in resposta:
        await update.message.reply_text(
            "❌ Anamnese cancelada.\n\n"
            "Digite /start para recomeçar.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "⏳ Gerando PDF e enviando para o médico...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    try:
        # Generate PDF
        pdf_path = generate_pdf(context.user_data)
        
        # Send email
        nome = context.user_data.get('nome', 'Paciente')
        send_email(
            to=DOCTOR_EMAIL,
            subject=f"Nova Anamnese - {nome}",
            body=f"Nova anamnese recebida via Telegram Bot.\n\nPaciente: {nome}\nData: {context.user_data.get('data_preenchimento', '-')}\n\nPDF em anexo.",
            attachments=[pdf_path]
        )
        
        # Send PDF to user too
        await update.message.reply_document(
            document=open(pdf_path, 'rb'),
            filename=f"Anamnese_{nome.replace(' ', '_')}.pdf",
            caption="📄 Seu PDF de anamnese"
        )
        
        await update.message.reply_text(
            "✅ *ANAMNESE ENVIADA COM SUCESSO!*\n\n"
            "O Dr. Felipe irá revisar suas respostas antes da consulta.\n\n"
            "🗓️ Nos vemos em breve!",
            parse_mode='Markdown'
        )
        
        # Cleanup
        os.remove(pdf_path)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"❌ Erro ao enviar: {str(e)}\n\n"
            "Por favor, tente novamente com /start"
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Anamnese cancelada.\n"
        "Digite /start para recomeçar.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ============================================
# PDF GENERATION
# ============================================

def generate_pdf(data: Dict[str, Any]) -> str:
    """Generate PDF from anamnese data."""
    
    nome = data.get('nome', 'Paciente').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = f"/tmp/Anamnese_{nome}_{timestamp}.pdf"
    
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
    
    story = []
    
    # Header
    story.append(Paragraph("ANAMNESE PRÉ-CONSULTA", title_style))
    story.append(Paragraph("Dr. Felipe Barreto - Neurocirurgia de Coluna | Medicina Funcional", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.gray)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Data: {data.get('data_preenchimento', '-')}", 
                          ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    
    # Sections
    def add_field(label, value):
        story.append(Paragraph(f"<b>{label}:</b>", label_style))
        story.append(Paragraph(str(value) if value else '-', value_style))
    
    # Identificação
    story.append(Paragraph("📋 IDENTIFICAÇÃO", section_style))
    add_field("Nome", data.get('nome'))
    add_field("Data de Nascimento", data.get('data_nascimento'))
    add_field("Sexo", data.get('sexo'))
    add_field("Profissão", data.get('profissao'))
    add_field("Telefone", data.get('telefone'))
    
    # Queixa Principal
    story.append(Paragraph("🎯 QUEIXA PRINCIPAL", section_style))
    add_field("Queixa", data.get('queixa_principal'))
    add_field("Tempo do problema", data.get('tempo_problema'))
    add_field("Evento desencadeante", data.get('evento_desencadeante'))
    
    # Dor
    story.append(Paragraph("💢 INVESTIGAÇÃO DA DOR", section_style))
    add_field("Localização", data.get('dor_local'))
    add_field("Intensidade", f"{data.get('dor_intensidade', '-')}/10")
    add_field("Tipo", data.get('dor_tipo'))
    add_field("Duração", data.get('dor_duracao'))
    add_field("Irradiação", data.get('dor_irradiacao'))
    
    # Red Flags
    story.append(Paragraph("⚠️ SINAIS DE ALERTA", section_style))
    red_flags = data.get('red_flags', 'Nenhum')
    if 'Nenhum' in red_flags:
        add_field("Status", "✅ Nenhum sinal de alerta")
    else:
        story.append(Paragraph(f"<b>ATENÇÃO:</b> <font color='red'>{red_flags}</font>", value_style))
    
    # Sono e Estresse
    story.append(Paragraph("😴 SONO E ESTRESSE", section_style))
    add_field("Qualidade do sono", data.get('sono_qualidade'))
    add_field("Despertares noturnos", data.get('sono_despertares'))
    add_field("Nível de estresse", f"{data.get('estresse_nivel', '-')}/10")
    add_field("Fator estressante", data.get('estresse_fator'))
    
    # Histórico
    story.append(Paragraph("🏥 HISTÓRICO MÉDICO", section_style))
    add_field("Condições", data.get('condicoes'))
    add_field("Medicamentos", data.get('medicamentos_lista'))
    add_field("Alergias", data.get('alergias'))
    add_field("Cirurgias anteriores", data.get('cirurgias'))
    
    # Tratamentos
    story.append(Paragraph("💪 TRATAMENTOS E HÁBITOS", section_style))
    add_field("Tratamentos anteriores", data.get('tratamentos'))
    add_field("Resultado", data.get('resultado_tratamentos'))
    add_field("Atividade física", data.get('atividade_fisica'))
    add_field("Tabagismo", data.get('tabagismo'))
    add_field("Álcool", data.get('alcool'))
    
    # Expectativas
    story.append(Paragraph("🎯 EXPECTATIVAS", section_style))
    add_field("Expectativas", data.get('expectativas'))
    add_field("Objetivo de saúde", data.get('objetivo_saude'))
    add_field("Observações", data.get('observacoes'))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Paragraph("Documento gerado automaticamente via Telegram Bot - Dr. Felipe Barreto",
                          ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, 
                                        fontSize=8, textColor=colors.gray)))
    
    doc.build(story)
    return pdf_path

# ============================================
# MAIN
# ============================================

def main():
    """Run the bot."""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Configure o BOT_TOKEN antes de iniciar!")
        print("   Edite o arquivo ou defina TELEGRAM_ANAMNESE_BOT_TOKEN")
        sys.exit(1)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nome)],
            DATA_NASCIMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, data_nascimento)],
            SEXO: [MessageHandler(filters.TEXT & ~filters.COMMAND, sexo)],
            PROFISSAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, profissao)],
            TELEFONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, telefone)],
            QUEIXA_PRINCIPAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, queixa_principal)],
            TEMPO_PROBLEMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, tempo_problema)],
            EVENTO_DESENCADEANTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, evento_desencadeante)],
            DOR_LOCAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, dor_local)],
            DOR_INTENSIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, dor_intensidade)],
            DOR_TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, dor_tipo)],
            DOR_DURACAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, dor_duracao)],
            DOR_IRRADIACAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, dor_irradiacao)],
            RED_FLAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, red_flags)],
            SONO_QUALIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sono_qualidade)],
            SONO_DESPERTARES: [MessageHandler(filters.TEXT & ~filters.COMMAND, sono_despertares)],
            ESTRESSE_NIVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, estresse_nivel)],
            ESTRESSE_FATOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, estresse_fator)],
            CONDICOES: [MessageHandler(filters.TEXT & ~filters.COMMAND, condicoes)],
            USA_MEDICAMENTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, usa_medicamentos)],
            MEDICAMENTOS_LISTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, medicamentos_lista)],
            ALERGIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, alergias)],
            CIRURGIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, cirurgias)],
            TRATAMENTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, tratamentos)],
            RESULTADO_TRATAMENTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, resultado_tratamentos)],
            ATIVIDADE_FISICA: [MessageHandler(filters.TEXT & ~filters.COMMAND, atividade_fisica)],
            TABAGISMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, tabagismo)],
            ALCOOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, alcool)],
            EXPECTATIVAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, expectativas)],
            OBJETIVO_SAUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, objetivo_saude)],
            OBSERVACOES: [MessageHandler(filters.TEXT & ~filters.COMMAND, observacoes)],
            CONFIRMAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    print("🤖 Bot de Anamnese iniciado!")
    print("   Aguardando mensagens...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

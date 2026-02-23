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
    # NDI - Neck Disability Index (se dor cervical)
    NDI_INTENSIDADE, NDI_CUIDADOS, NDI_LEVANTAR, NDI_LEITURA, NDI_CEFALEIA,
    NDI_CONCENTRACAO, NDI_TRABALHO, NDI_DIRIGIR, NDI_SONO, NDI_LAZER,
    # ODI - Oswestry Disability Index (se dor lombar)
    ODI_INTENSIDADE, ODI_CUIDADOS, ODI_LEVANTAR, ODI_CAMINHAR, ODI_SENTAR,
    ODI_FICAR_PE, ODI_SONO, ODI_VIDA_SEXUAL, ODI_VIDA_SOCIAL, ODI_VIAJAR,
    # Função Gastrointestinal (SIBO/Disbiose)
    GI_FREQUENCIA, GI_BRISTOL, GI_DISTENSAO, GI_FLATULENCIA,
    GI_SIBO_TRIGGERS, GI_FADIGA_POS, GI_HISTAMINA, GI_ANTIBIOTICOS,
    # Sono e Estresse
    SONO_QUALIDADE, SONO_DESPERTARES, ESTRESSE_NIVEL, ESTRESSE_FATOR,
    CONDICOES, USA_MEDICAMENTOS, MEDICAMENTOS_LISTA, ALERGIAS, CIRURGIAS,
    TRATAMENTOS, RESULTADO_TRATAMENTOS, ATIVIDADE_FISICA, TABAGISMO, ALCOOL,
    EXPECTATIVAS, OBJETIVO_SAUDE, OBSERVACOES,
    CONFIRMAR
) = range(60)

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
    
    # Verificar se tem dor cervical ou lombar para aplicar NDI/ODI
    dor_local = context.user_data.get('dor_local', '').lower()
    
    if 'cervical' in dor_local or 'pescoço' in dor_local:
        # Aplicar NDI
        await update.message.reply_text(
            "📊 *ÍNDICE DE INCAPACIDADE CERVICAL (NDI)*\n\n"
            "Vou fazer 10 perguntas rápidas sobre como a dor no pescoço afeta suas atividades.\n"
            "Responda com o número da opção (0-5).",
            parse_mode='Markdown'
        )
        keyboard = get_keyboard(['0-Sem dor', '1-Leve', '2-Moderada', '3-Forte', '4-Muito forte', '5-Pior possível'], columns=3)
        await update.message.reply_text(
            "*1/10 - Intensidade da dor no pescoço agora:*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return NDI_INTENSIDADE
    
    elif 'lombar' in dor_local or 'lombalgia' in dor_local or 'perna' in dor_local or 'glúteo' in dor_local:
        # Aplicar ODI
        await update.message.reply_text(
            "📊 *ÍNDICE DE INCAPACIDADE LOMBAR (ODI)*\n\n"
            "Vou fazer 10 perguntas rápidas sobre como a dor nas costas afeta suas atividades.\n"
            "Responda com o número da opção (0-5).",
            parse_mode='Markdown'
        )
        keyboard = get_keyboard(['0-Sem dor', '1-Leve', '2-Moderada', '3-Forte', '4-Muito forte', '5-Pior possível'], columns=3)
        await update.message.reply_text(
            "*1/10 - Intensidade da dor agora:*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return ODI_INTENSIDADE
    
    else:
        # Ir direto para GI
        return await go_to_gi(update, context)

async def go_to_gi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ir para seção de função gastrointestinal"""
    keyboard = get_keyboard([
        'Menos de 3x/semana',
        '3-7x (até 1x/dia)',
        '7-14x (1-2x/dia)',
        'Mais de 14x/semana'
    ], columns=2)
    
    await update.message.reply_text(
        "🦠 *FUNÇÃO GASTROINTESTINAL*\n\n"
        "*Quantas vezes você evacua por semana?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_FREQUENCIA

# ============================================
# NDI - NECK DISABILITY INDEX
# ============================================

NDI_OPTIONS = ['0', '1', '2', '3', '4', '5']

async def ndi_intensidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_1'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Com dor', '2-Lento', '3-Preciso ajuda', '4-Ajuda diária', '5-Não consigo'], columns=2)
    await update.message.reply_text("*2/10 - Cuidados pessoais (vestir-se, banho):*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_CUIDADOS

async def ndi_cuidados(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_2'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Pesados OK', '1-Com dor', '2-Médios OK', '3-Leves', '4-Muito leves', '5-Nada'], columns=2)
    await update.message.reply_text("*3/10 - Levantar objetos:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_LEVANTAR

async def ndi_levantar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_3'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Sem dor', '1-Dor leve', '2-Dor moderada', '3-Limitado', '4-Quase não', '5-Não consigo'], columns=2)
    await update.message.reply_text("*4/10 - Leitura:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_LEITURA

async def ndi_leitura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_4'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Sem cefaleia', '1-Leve rara', '2-Moderada rara', '3-Moderada freq', '4-Forte freq', '5-Sempre'], columns=2)
    await update.message.reply_text("*5/10 - Dores de cabeça:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_CEFALEIA

async def ndi_cefaleia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_5'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Leve dific', '2-Moderada', '3-Muita dific', '4-Extrema', '5-Não consigo'], columns=2)
    await update.message.reply_text("*6/10 - Concentração:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_CONCENTRACAO

async def ndi_concentracao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_6'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Só habitual', '2-Maior parte', '3-Não consigo', '4-Quase nada', '5-Nenhum'], columns=2)
    await update.message.reply_text("*7/10 - Trabalho:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_TRABALHO

async def ndi_trabalho(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_7'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Sem dor', '1-Dor leve', '2-Dor moderada', '3-Limitado', '4-Quase não', '5-Não consigo'], columns=2)
    await update.message.reply_text("*8/10 - Dirigir:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_DIRIGIR

async def ndi_dirigir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_8'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Leve perturb', '2-1-2h sem dormir', '3-2-3h', '4-3-5h', '5-5-7h'], columns=2)
    await update.message.reply_text("*9/10 - Sono:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_SONO

async def ndi_sono(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_9'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Com dor', '2-Maioria', '3-Algumas', '4-Quase nada', '5-Nenhuma'], columns=2)
    await update.message.reply_text("*10/10 - Lazer/recreação:*", parse_mode='Markdown', reply_markup=keyboard)
    return NDI_LAZER

async def ndi_lazer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ndi_10'] = update.message.text[0] if update.message.text else '0'
    
    # Calcular score NDI
    ndi_total = sum(int(context.user_data.get(f'ndi_{i}', '0')[0]) for i in range(1, 11))
    ndi_percent = (ndi_total / 50) * 100
    
    if ndi_percent <= 8:
        ndi_class = "Sem incapacidade"
    elif ndi_percent <= 28:
        ndi_class = "Incapacidade leve"
    elif ndi_percent <= 48:
        ndi_class = "Incapacidade moderada"
    elif ndi_percent <= 68:
        ndi_class = "Incapacidade severa"
    else:
        ndi_class = "Incapacidade completa"
    
    context.user_data['ndi_score'] = ndi_total
    context.user_data['ndi_percent'] = ndi_percent
    context.user_data['ndi_class'] = ndi_class
    
    await update.message.reply_text(
        f"📊 *Resultado NDI:* {ndi_total}/50 ({ndi_percent:.0f}%)\n"
        f"*Classificação:* {ndi_class}",
        parse_mode='Markdown'
    )
    
    # Verificar se também tem dor lombar
    dor_local = context.user_data.get('dor_local', '').lower()
    if 'lombar' in dor_local or 'perna' in dor_local or 'glúteo' in dor_local:
        await update.message.reply_text(
            "📊 *ÍNDICE DE INCAPACIDADE LOMBAR (ODI)*\n\n"
            "Agora vou avaliar a dor lombar.",
            parse_mode='Markdown'
        )
        keyboard = get_keyboard(['0-Sem dor', '1-Leve', '2-Moderada', '3-Forte', '4-Muito forte', '5-Pior possível'], columns=3)
        await update.message.reply_text("*1/10 - Intensidade da dor:*", parse_mode='Markdown', reply_markup=keyboard)
        return ODI_INTENSIDADE
    
    return await go_to_gi(update, context)

# ============================================
# ODI - OSWESTRY DISABILITY INDEX
# ============================================

async def odi_intensidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_1'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Com dor', '2-Lento', '3-Preciso ajuda', '4-Ajuda diária', '5-Acamado'], columns=2)
    await update.message.reply_text("*2/10 - Cuidados pessoais:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_CUIDADOS

async def odi_cuidados(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_2'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Pesados OK', '1-Com dor', '2-Médios OK', '3-Leves', '4-Muito leves', '5-Nada'], columns=2)
    await update.message.reply_text("*3/10 - Levantar objetos:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_LEVANTAR

async def odi_levantar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_3'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Qualquer dist', '1-Até 1.5km', '2-Até 800m', '3-Até 400m', '4-Com bengala', '5-Acamado'], columns=2)
    await update.message.reply_text("*4/10 - Caminhar:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_CAMINHAR

async def odi_caminhar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_4'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Sem limite', '1-Favorita OK', '2-Até 1h', '3-Até 30min', '4-Até 10min', '5-Não consigo'], columns=2)
    await update.message.reply_text("*5/10 - Sentar:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_SENTAR

async def odi_sentar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_5'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Sem limite', '1-Com dor', '2-Até 1h', '3-Até 30min', '4-Até 10min', '5-Não consigo'], columns=2)
    await update.message.reply_text("*6/10 - Ficar em pé:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_FICAR_PE

async def odi_ficar_pe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_6'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Ocasional', '2-<6h', '3-<4h', '4-<2h', '5-Não durmo'], columns=2)
    await update.message.reply_text("*7/10 - Sono:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_SONO

async def odi_sono(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_7'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Normal', '1-Com dor', '2-Muito dolorosa', '3-Limitada', '4-Quase nula', '5-Impossível', 'N/A'], columns=2)
    await update.message.reply_text("*8/10 - Vida sexual (se aplicável):*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_VIDA_SEXUAL

async def odi_vida_sexual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resp = update.message.text.strip()
    context.user_data['odi_8'] = resp[0] if resp and resp[0].isdigit() else 'NA'
    keyboard = get_keyboard(['0-Normal', '1-Com dor', '2-Sem intensas', '3-Restrita', '4-Só em casa', '5-Nenhuma'], columns=2)
    await update.message.reply_text("*9/10 - Vida social:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_VIDA_SOCIAL

async def odi_vida_social(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_9'] = update.message.text[0] if update.message.text else '0'
    keyboard = get_keyboard(['0-Sem dor', '1-Com dor', '2->2h OK', '3-<1h', '4-<30min', '5-Só tratamento'], columns=2)
    await update.message.reply_text("*10/10 - Viajar:*", parse_mode='Markdown', reply_markup=keyboard)
    return ODI_VIAJAR

async def odi_viajar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['odi_10'] = update.message.text[0] if update.message.text else '0'
    
    # Calcular score ODI
    odi_values = []
    max_score = 50
    for i in range(1, 11):
        val = context.user_data.get(f'odi_{i}', '0')
        if val == 'NA' or not val[0].isdigit():
            max_score -= 5  # Ajustar se N/A
        else:
            odi_values.append(int(val[0]))
    
    odi_total = sum(odi_values)
    odi_percent = (odi_total / max_score) * 100 if max_score > 0 else 0
    
    if odi_percent <= 20:
        odi_class = "Incapacidade mínima"
    elif odi_percent <= 40:
        odi_class = "Incapacidade moderada"
    elif odi_percent <= 60:
        odi_class = "Incapacidade severa"
    elif odi_percent <= 80:
        odi_class = "Incapacitado"
    else:
        odi_class = "Acamado"
    
    context.user_data['odi_score'] = odi_total
    context.user_data['odi_percent'] = odi_percent
    context.user_data['odi_class'] = odi_class
    
    await update.message.reply_text(
        f"📊 *Resultado ODI:* {odi_total}/{max_score} ({odi_percent:.0f}%)\n"
        f"*Classificação:* {odi_class}",
        parse_mode='Markdown'
    )
    
    return await go_to_gi(update, context)

# ============================================
# FUNÇÃO GASTROINTESTINAL (SIBO/DISBIOSE)
# ============================================

async def gi_frequencia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_frequencia'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Tipo 1-2 (duras)',
        'Tipo 3-4 (ideal)',
        'Tipo 5-6 (moles)',
        'Tipo 7 (líquidas)'
    ], columns=2)
    
    await update.message.reply_text(
        "*Como são suas fezes geralmente?* (Escala de Bristol)",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_BRISTOL

async def gi_bristol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_bristol'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Não',
        'Às vezes',
        'Frequentemente',
        'Sempre'
    ], columns=2)
    
    await update.message.reply_text(
        "*Sente barriga inchada (distensão), principalmente após refeições?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_DISTENSAO

async def gi_distensao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_distensao'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Normal',
        'Aumentado',
        'Muito aumentado',
        'Gases com odor forte'
    ], columns=2)
    
    await update.message.reply_text(
        "*Elimina muitos gases (flatulência)?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_FLATULENCIA

async def gi_flatulencia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_flatulencia'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Nenhum',
        'Carboidratos pioram',
        'Fibras pioram',
        'Jejum melhora',
        'Leite/derivados pioram',
        'Feijão/cebola pioram'
    ], columns=2)
    
    await update.message.reply_text(
        "*O que piora ou melhora seus sintomas digestivos?*\n"
        "(Selecione o mais relevante)",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_SIBO_TRIGGERS

async def gi_sibo_triggers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_sibo_triggers'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Não',
        'Às vezes',
        'Frequentemente'
    ], columns=3)
    
    await update.message.reply_text(
        "*Sente fadiga ou 'névoa mental' após as refeições?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_FADIGA_POS

async def gi_fadiga_pos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_fadiga_pos'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Nenhum',
        'Coceira na pele',
        'Rubor facial ao comer',
        'Congestão nasal',
        'Cefaleia por alimentos',
        'Vários desses'
    ], columns=2)
    
    await update.message.reply_text(
        "*Apresenta algum desses sintomas histamínicos?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_HISTAMINA

async def gi_histamina(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_histamina'] = update.message.text.strip()
    
    keyboard = get_keyboard([
        'Não',
        '1 vez',
        '2-3 vezes',
        'Mais de 3 vezes'
    ], columns=2)
    
    await update.message.reply_text(
        "*Usou antibióticos nos últimos 6 meses?*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return GI_ANTIBIOTICOS

async def gi_antibioticos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gi_antibioticos'] = update.message.text.strip()
    
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
    
    # NDI - se aplicável
    if data.get('ndi_score'):
        story.append(Paragraph("📊 NDI - ÍNDICE INCAPACIDADE CERVICAL", section_style))
        add_field("Pontuação", f"{data.get('ndi_score')}/50 ({data.get('ndi_percent', 0):.0f}%)")
        add_field("Classificação", data.get('ndi_class'))
    
    # ODI - se aplicável
    if data.get('odi_score'):
        story.append(Paragraph("📊 ODI - ÍNDICE INCAPACIDADE LOMBAR", section_style))
        add_field("Pontuação", f"{data.get('odi_score')}/50 ({data.get('odi_percent', 0):.0f}%)")
        add_field("Classificação", data.get('odi_class'))
    
    # Função Gastrointestinal (SIBO/Disbiose)
    story.append(Paragraph("🦠 FUNÇÃO GASTROINTESTINAL", section_style))
    add_field("Frequência evacuação", data.get('gi_frequencia'))
    add_field("Escala Bristol", data.get('gi_bristol'))
    add_field("Distensão abdominal", data.get('gi_distensao'))
    add_field("Flatulência", data.get('gi_flatulencia'))
    add_field("Triggers SIBO", data.get('gi_sibo_triggers'))
    add_field("Fadiga pós-refeição", data.get('gi_fadiga_pos'))
    add_field("Sintomas histamínicos", data.get('gi_histamina'))
    add_field("Antibióticos recentes", data.get('gi_antibioticos'))
    
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
            # NDI - Neck Disability Index
            NDI_INTENSIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_intensidade)],
            NDI_CUIDADOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_cuidados)],
            NDI_LEVANTAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_levantar)],
            NDI_LEITURA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_leitura)],
            NDI_CEFALEIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_cefaleia)],
            NDI_CONCENTRACAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_concentracao)],
            NDI_TRABALHO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_trabalho)],
            NDI_DIRIGIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_dirigir)],
            NDI_SONO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_sono)],
            NDI_LAZER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ndi_lazer)],
            # ODI - Oswestry Disability Index
            ODI_INTENSIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_intensidade)],
            ODI_CUIDADOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_cuidados)],
            ODI_LEVANTAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_levantar)],
            ODI_CAMINHAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_caminhar)],
            ODI_SENTAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_sentar)],
            ODI_FICAR_PE: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_ficar_pe)],
            ODI_SONO: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_sono)],
            ODI_VIDA_SEXUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_vida_sexual)],
            ODI_VIDA_SOCIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_vida_social)],
            ODI_VIAJAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, odi_viajar)],
            # Função Gastrointestinal
            GI_FREQUENCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_frequencia)],
            GI_BRISTOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_bristol)],
            GI_DISTENSAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_distensao)],
            GI_FLATULENCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_flatulencia)],
            GI_SIBO_TRIGGERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_sibo_triggers)],
            GI_FADIGA_POS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_fadiga_pos)],
            GI_HISTAMINA: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_histamina)],
            GI_ANTIBIOTICOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gi_antibioticos)],
            # Sono e Estresse
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

#!/usr/bin/env python3
"""
Bot de Anamnese - Fluxo Conversacional
Gerencia o questionário passo a passo via WhatsApp
"""

import json
from typing import Optional, Dict, Any, Tuple
from clinica_api import *

# ============================================================
# ESTRUTURA DO FLUXO
# ============================================================

FLUXO_ANAMNESE = [
    # Step 1: Identificação
    {
        "step": 1,
        "bloco": "identificacao",
        "pergunta": "Olá! 👋 Sou o assistente do Dr. Felipe Barreto.\n\nVamos iniciar sua anamnese pré-consulta.\n\n*Qual é o seu nome completo?*",
        "campo": "nome",
        "tipo": "texto"
    },
    {
        "step": 2,
        "bloco": "identificacao",
        "pergunta": "Qual sua *data de nascimento*?\n(formato: DD/MM/AAAA)",
        "campo": "data_nascimento",
        "tipo": "data"
    },
    {
        "step": 3,
        "bloco": "identificacao",
        "pergunta": "Qual seu *sexo biológico*?\n\n1️⃣ Masculino\n2️⃣ Feminino",
        "campo": "sexo",
        "tipo": "opcao",
        "opcoes": {"1": "masculino", "2": "feminino"}
    },
    {
        "step": 4,
        "bloco": "identificacao",
        "pergunta": "Qual sua *profissão/ocupação*?",
        "campo": "profissao",
        "tipo": "texto"
    },
    
    # Step 5: Queixa Principal
    {
        "step": 5,
        "bloco": "queixa",
        "pergunta": "📋 *QUEIXA PRINCIPAL*\n\nQual o *principal motivo* da sua consulta?\n(Descreva com suas palavras)",
        "campo": "queixa_principal",
        "tipo": "texto"
    },
    {
        "step": 6,
        "bloco": "queixa",
        "pergunta": "Há *quanto tempo* esse problema começou?\n\n1️⃣ Menos de 1 semana\n2️⃣ 1-4 semanas\n3️⃣ 1-3 meses\n4️⃣ 3-6 meses\n5️⃣ 6-12 meses\n6️⃣ Mais de 1 ano",
        "campo": "tempo_problema",
        "tipo": "opcao",
        "opcoes": {
            "1": "menos_1_semana",
            "2": "1_4_semanas", 
            "3": "1_3_meses",
            "4": "3_6_meses",
            "5": "6_12_meses",
            "6": "mais_1_ano"
        }
    },
    
    # Step 7-12: Investigação da Dor
    {
        "step": 7,
        "bloco": "dor",
        "pergunta": "🎯 *INVESTIGAÇÃO DA DOR*\n\nVocê sente dor? Se sim, *onde*?\n(pode marcar mais de uma, separado por vírgula)\n\n1️⃣ Não sinto dor\n2️⃣ Pescoço/cervical\n3️⃣ Região torácica (meio das costas)\n4️⃣ Lombar\n5️⃣ Glúteo/quadril\n6️⃣ Perna\n7️⃣ Braço",
        "campo": "dor_localizacao",
        "tipo": "multipla",
        "opcoes": {
            "1": "sem_dor",
            "2": "cervical",
            "3": "toracica",
            "4": "lombar",
            "5": "gluteo_quadril",
            "6": "perna",
            "7": "braco"
        }
    },
    {
        "step": 8,
        "bloco": "dor",
        "condicao": "tem_dor",
        "pergunta": "Em uma escala de *0 a 10*, qual a intensidade da sua dor *na média do dia*?\n(0 = sem dor, 10 = pior dor imaginável)",
        "campo": "dor_intensidade",
        "tipo": "numero",
        "min": 0,
        "max": 10
    },
    {
        "step": 9,
        "bloco": "dor",
        "condicao": "tem_dor",
        "pergunta": "Há *quanto tempo* sente essa dor?\n\n1️⃣ Menos de 6 semanas (aguda)\n2️⃣ 6-12 semanas (subaguda)\n3️⃣ Mais de 3 meses (crônica)",
        "campo": "dor_duracao",
        "tipo": "opcao",
        "opcoes": {
            "1": "aguda",
            "2": "subaguda",
            "3": "cronica"
        }
    },
    {
        "step": 10,
        "bloco": "dor",
        "condicao": "tem_dor",
        "pergunta": "A dor *irradia* (se espalha) para outras regiões?\n\n1️⃣ Não, fica só no local\n2️⃣ Sim, desce para a perna\n3️⃣ Sim, desce para o braço\n4️⃣ Sim, outro local",
        "campo": "dor_irradiacao",
        "tipo": "opcao",
        "opcoes": {
            "1": "nao",
            "2": "perna",
            "3": "braco",
            "4": "outro"
        }
    },
    
    # Step 11: RED FLAGS
    {
        "step": 11,
        "bloco": "red_flags",
        "pergunta": "⚠️ *SINTOMAS IMPORTANTES*\n\nVocê sente algum desses sintomas?\n(marque todos que se aplicam, separado por vírgula, ou 0 se nenhum)\n\n0️⃣ Nenhum\n1️⃣ Fraqueza nas pernas\n2️⃣ Fraqueza nas mãos/braços\n3️⃣ Dificuldade para segurar urina\n4️⃣ Dificuldade para segurar fezes\n5️⃣ Dormência na região genital\n6️⃣ Perda de equilíbrio\n7️⃣ Dor que acorda durante a noite\n8️⃣ Febre associada à dor\n9️⃣ Perda de peso inexplicada",
        "campo": "sintomas_alerta",
        "tipo": "multipla",
        "opcoes": {
            "0": "nenhum",
            "1": "fraqueza_pernas",
            "2": "fraqueza_bracos",
            "3": "dificuldade_urina",
            "4": "dificuldade_fezes",
            "5": "anestesia_sela",
            "6": "perda_equilibrio",
            "7": "dor_noturna",
            "8": "febre",
            "9": "perda_peso"
        }
    },
    
    # Step 12-14: Sono e Estresse
    {
        "step": 12,
        "bloco": "sono",
        "pergunta": "😴 *SONO*\n\nComo você se sente ao acordar?\n\n1️⃣ Descansado e com energia\n2️⃣ Um pouco cansado, mas ok\n3️⃣ Cansado como se não tivesse dormido\n4️⃣ Exausto",
        "campo": "sono_qualidade",
        "tipo": "opcao",
        "opcoes": {
            "1": "descansado",
            "2": "pouco_cansado",
            "3": "cansado",
            "4": "exausto"
        }
    },
    {
        "step": 13,
        "bloco": "sono",
        "pergunta": "Quantas vezes *acorda durante a noite*?\n\n1️⃣ Nenhuma (sono direto)\n2️⃣ 1-2 vezes\n3️⃣ 3-4 vezes\n4️⃣ Mais de 4 vezes",
        "campo": "sono_despertares",
        "tipo": "opcao",
        "opcoes": {
            "1": "nenhuma",
            "2": "1_2",
            "3": "3_4",
            "4": "mais_4"
        }
    },
    {
        "step": 14,
        "bloco": "estresse",
        "pergunta": "😰 *ESTRESSE*\n\nEm uma escala de *0 a 10*, qual seu nível de estresse atual?\n(0 = nenhum, 10 = máximo)",
        "campo": "estresse_nivel",
        "tipo": "numero",
        "min": 0,
        "max": 10
    },
    
    # Step 15-17: Medicamentos
    {
        "step": 15,
        "bloco": "medicamentos",
        "pergunta": "💊 *MEDICAMENTOS*\n\nUsa algum *medicamento* atualmente?\n\n1️⃣ Não\n2️⃣ Sim",
        "campo": "usa_medicamentos",
        "tipo": "opcao",
        "opcoes": {"1": "nao", "2": "sim"}
    },
    {
        "step": 16,
        "bloco": "medicamentos",
        "condicao": "usa_medicamentos",
        "pergunta": "Quais medicamentos você usa?\n(liste todos, um por linha ou separados por vírgula)",
        "campo": "medicamentos_lista",
        "tipo": "texto"
    },
    
    # Step 17: Tratamentos anteriores
    {
        "step": 17,
        "bloco": "tratamentos",
        "pergunta": "🏥 *TRATAMENTOS ANTERIORES*\n\nJá fez algum tratamento para esse problema?\n(marque todos, separado por vírgula, ou 0 se nenhum)\n\n0️⃣ Nenhum\n1️⃣ Medicações\n2️⃣ Fisioterapia\n3️⃣ Acupuntura\n4️⃣ Infiltração/bloqueio\n5️⃣ Cirurgia\n6️⃣ Outro",
        "campo": "tratamentos_anteriores",
        "tipo": "multipla",
        "opcoes": {
            "0": "nenhum",
            "1": "medicacoes",
            "2": "fisioterapia",
            "3": "acupuntura",
            "4": "infiltracao",
            "5": "cirurgia",
            "6": "outro"
        }
    },
    
    # Step 18: Expectativas
    {
        "step": 18,
        "bloco": "expectativas",
        "pergunta": "🎯 *EXPECTATIVAS*\n\nO que você espera desta consulta?\n(resposta livre)",
        "campo": "expectativas",
        "tipo": "texto"
    },
]

# Steps do ODI (aplicado se dor lombar/perna)
ODI_STEPS = [
    {
        "step": "odi_1",
        "pergunta": "📊 *ODI - Avaliação Funcional Lombar*\n\n*Seção 1: Intensidade da dor*\n\n0️⃣ Não sinto dor no momento\n1️⃣ A dor é muito leve\n2️⃣ A dor é moderada\n3️⃣ A dor é razoavelmente intensa\n4️⃣ A dor é muito intensa\n5️⃣ A dor é a pior imaginável",
        "campo": "odi_intensidade_dor",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_2",
        "pergunta": "*Seção 2: Cuidados pessoais (lavar-se, vestir-se)*\n\n0️⃣ Posso cuidar de mim sem dor\n1️⃣ Posso cuidar de mim, mas provoca dor\n2️⃣ É doloroso e sou lento\n3️⃣ Preciso de alguma ajuda\n4️⃣ Preciso de ajuda na maioria dos cuidados\n5️⃣ Não consigo me vestir sozinho",
        "campo": "odi_cuidados_pessoais",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_3",
        "pergunta": "*Seção 3: Levantar objetos*\n\n0️⃣ Posso levantar objetos pesados sem dor\n1️⃣ Posso levantar pesados, mas dói\n2️⃣ Só consigo se bem posicionados\n3️⃣ Só consigo objetos leves/médios\n4️⃣ Só consigo objetos muito leves\n5️⃣ Não consigo levantar nada",
        "campo": "odi_levantar_objetos",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_4",
        "pergunta": "*Seção 4: Caminhar*\n\n0️⃣ Posso caminhar qualquer distância\n1️⃣ Não consigo mais de 1,5 km\n2️⃣ Não consigo mais de 800 metros\n3️⃣ Não consigo mais de 400 metros\n4️⃣ Só com bengala ou muletas\n5️⃣ Fico na cama a maior parte",
        "campo": "odi_caminhar",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_5",
        "pergunta": "*Seção 5: Sentar*\n\n0️⃣ Posso sentar o tempo que quiser\n1️⃣ Posso sentar na minha cadeira favorita\n2️⃣ Não consigo mais de 1 hora\n3️⃣ Não consigo mais de 30 minutos\n4️⃣ Não consigo mais de 10 minutos\n5️⃣ A dor me impede de sentar",
        "campo": "odi_sentar",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_6",
        "pergunta": "*Seção 6: Ficar em pé*\n\n0️⃣ Posso ficar em pé sem dor\n1️⃣ Posso, mas provoca dor\n2️⃣ Não consigo mais de 1 hora\n3️⃣ Não consigo mais de 30 minutos\n4️⃣ Não consigo mais de 10 minutos\n5️⃣ A dor me impede de ficar em pé",
        "campo": "odi_ficar_em_pe",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_7",
        "pergunta": "*Seção 7: Dormir*\n\n0️⃣ Meu sono nunca é perturbado pela dor\n1️⃣ Ocasionalmente perturbado\n2️⃣ Durmo menos de 6 horas pela dor\n3️⃣ Durmo menos de 4 horas\n4️⃣ Durmo menos de 2 horas\n5️⃣ A dor me impede de dormir",
        "campo": "odi_dormir",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_8",
        "pergunta": "*Seção 8: Vida social*\n\n0️⃣ Normal, sem dor\n1️⃣ Normal, mas aumenta a dor\n2️⃣ Pouco afetada, exceto atividades intensas\n3️⃣ Restringida, não saio tanto\n4️⃣ Restrita à minha casa\n5️⃣ Não tenho vida social pela dor",
        "campo": "odi_vida_social",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
    {
        "step": "odi_9",
        "pergunta": "*Seção 9: Viajar*\n\n0️⃣ Posso viajar sem dor\n1️⃣ Posso viajar, mas provoca dor\n2️⃣ Consigo viagens de mais de 2h\n3️⃣ Menos de 1 hora\n4️⃣ Menos de 30 minutos\n5️⃣ A dor me impede de viajar",
        "campo": "odi_viajar",
        "tipo": "opcao",
        "opcoes": {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    },
]

# ============================================================
# GERENCIADOR DO BOT
# ============================================================

class AnamneseBot:
    def __init__(self, telefone: str):
        self.telefone = self._normalizar_telefone(telefone)
        self.paciente = None
        self.anamnese = None
        self._carregar_ou_criar()
    
    def _normalizar_telefone(self, telefone: str) -> str:
        """Remove caracteres não numéricos"""
        return ''.join(filter(str.isdigit, telefone))
    
    def _carregar_ou_criar(self):
        """Carrega paciente existente ou prepara para criar novo"""
        self.paciente = buscar_paciente_por_telefone(self.telefone)
        if self.paciente:
            self.anamnese = buscar_anamnese_em_andamento(self.paciente['id'])
    
    def get_step_atual(self) -> int:
        """Retorna o step atual da anamnese"""
        if not self.anamnese:
            return 1
        return self.anamnese.get('step_atual', 1)
    
    def get_pergunta_atual(self) -> Tuple[str, Dict]:
        """Retorna a pergunta atual e metadados"""
        step = self.get_step_atual()
        dados = self.anamnese.get('dados', {}) if self.anamnese else {}
        
        # Verificar se precisa aplicar ODI
        if step > len(FLUXO_ANAMNESE):
            dor_loc = dados.get('dor_localizacao', [])
            if any(loc in dor_loc for loc in ['lombar', 'gluteo_quadril', 'perna']):
                odi_step = step - len(FLUXO_ANAMNESE) - 1
                if odi_step < len(ODI_STEPS):
                    return ODI_STEPS[odi_step]['pergunta'], ODI_STEPS[odi_step]
            
            # Finalizado
            return self._mensagem_finalizacao(), {"tipo": "fim"}
        
        pergunta_info = FLUXO_ANAMNESE[step - 1]
        
        # Verificar condições
        if pergunta_info.get('condicao') == 'tem_dor':
            dor_loc = dados.get('dor_localizacao', [])
            if 'sem_dor' in dor_loc or not dor_loc:
                # Pular para próximo bloco
                self._avancar_step()
                return self.get_pergunta_atual()
        
        if pergunta_info.get('condicao') == 'usa_medicamentos':
            if dados.get('usa_medicamentos') != 'sim':
                self._avancar_step()
                return self.get_pergunta_atual()
        
        return pergunta_info['pergunta'], pergunta_info
    
    def processar_resposta(self, resposta: str) -> str:
        """Processa resposta e retorna próxima pergunta"""
        step = self.get_step_atual()
        
        if not self.paciente:
            # Criar paciente com nome (step 1)
            self.paciente = criar_paciente(resposta.strip(), self.telefone)
            self.anamnese = criar_anamnese(self.paciente['id'], {'nome': resposta.strip()})
            self._avancar_step()
            proxima, _ = self.get_pergunta_atual()
            return proxima
        
        if not self.anamnese:
            # Paciente existe mas sem anamnese em andamento
            self.anamnese = criar_anamnese(self.paciente['id'], {'nome': self.paciente.get('nome', '')})
            # Continua para processar a resposta normalmente
        
        # Processar resposta baseado no tipo
        if step <= len(FLUXO_ANAMNESE):
            pergunta_info = FLUXO_ANAMNESE[step - 1]
        else:
            odi_step = step - len(FLUXO_ANAMNESE) - 1
            if odi_step < len(ODI_STEPS):
                pergunta_info = ODI_STEPS[odi_step]
            else:
                return self._mensagem_finalizacao()
        
        valor = self._processar_valor(resposta, pergunta_info)
        
        if valor is None:
            return f"❌ Resposta inválida. Por favor, responda novamente:\n\n{pergunta_info['pergunta']}"
        
        # Salvar resposta
        campo = pergunta_info['campo']
        dados = self.anamnese.get('dados', {})
        dados[campo] = valor
        
        # Atualizar paciente se for dado de identificação
        if campo == 'data_nascimento':
            atualizar_paciente(self.paciente['id'], {'data_nascimento': valor})
        elif campo == 'sexo':
            atualizar_paciente(self.paciente['id'], {'sexo': valor})
        elif campo == 'profissao':
            atualizar_paciente(self.paciente['id'], {'profissao': valor})
        
        atualizar_anamnese(self.anamnese['id'], dados=dados)
        self._avancar_step()
        
        # Verificar se finalizou
        proxima, info = self.get_pergunta_atual()
        
        if info.get('tipo') == 'fim':
            self._finalizar()
        
        return proxima
    
    def _processar_valor(self, resposta: str, info: Dict) -> Any:
        """Processa valor baseado no tipo"""
        tipo = info.get('tipo')
        resposta = resposta.strip()
        
        if tipo == 'texto':
            return resposta
        
        elif tipo == 'numero':
            try:
                valor = int(resposta)
                if info.get('min') is not None and valor < info['min']:
                    return None
                if info.get('max') is not None and valor > info['max']:
                    return None
                return valor
            except:
                return None
        
        elif tipo == 'opcao':
            opcoes = info.get('opcoes', {})
            if resposta in opcoes:
                return opcoes[resposta]
            return None
        
        elif tipo == 'multipla':
            opcoes = info.get('opcoes', {})
            valores = []
            for r in resposta.replace(' ', '').split(','):
                if r in opcoes:
                    valores.append(opcoes[r])
            return valores if valores else None
        
        elif tipo == 'data':
            # Aceita DD/MM/AAAA ou AAAA-MM-DD
            try:
                if '/' in resposta:
                    partes = resposta.split('/')
                    return f"{partes[2]}-{partes[1]}-{partes[0]}"
                return resposta
            except:
                return resposta
        
        return resposta
    
    def _avancar_step(self):
        """Avança para próximo step"""
        novo_step = self.get_step_atual() + 1
        atualizar_anamnese(self.anamnese['id'], step=novo_step)
        self.anamnese['step_atual'] = novo_step
    
    def _finalizar(self):
        """Finaliza a anamnese e calcula scores"""
        dados = self.anamnese.get('dados', {})
        
        # Detectar red flags
        sintomas = dados.get('sintomas_alerta', [])
        red_flags = []
        if 'fraqueza_pernas' in sintomas:
            red_flags.append("🚨 Fraqueza nas pernas")
        if 'fraqueza_bracos' in sintomas:
            red_flags.append("🚨 Fraqueza nos braços")
        if 'dificuldade_urina' in sintomas:
            red_flags.append("🚨 URGENTE: Alteração urinária")
        if 'dificuldade_fezes' in sintomas:
            red_flags.append("🚨 URGENTE: Alteração intestinal")
        if 'anestesia_sela' in sintomas:
            red_flags.append("🚨 URGENTE: Anestesia em sela")
        if 'perda_equilibrio' in sintomas:
            red_flags.append("🚨 Perda de equilíbrio")
        if 'febre' in sintomas:
            red_flags.append("🚨 Febre associada")
        if 'perda_peso' in sintomas:
            red_flags.append("🚨 Perda de peso inexplicada")
        
        # Calcular ODI se aplicável
        odi_score = None
        odi_campos = ['odi_intensidade_dor', 'odi_cuidados_pessoais', 'odi_levantar_objetos',
                      'odi_caminhar', 'odi_sentar', 'odi_ficar_em_pe', 'odi_dormir', 
                      'odi_vida_social', 'odi_viajar']
        odi_respostas = {}
        for campo in odi_campos:
            if campo in dados:
                chave = campo.replace('odi_', '')
                odi_respostas[chave] = dados[campo]
        
        if odi_respostas:
            odi_score = calcular_odi(odi_respostas)
        
        finalizar_anamnese(
            self.anamnese['id'],
            odi_score=odi_score,
            red_flags=red_flags if red_flags else None
        )
    
    def _mensagem_finalizacao(self) -> str:
        """Gera mensagem de finalização"""
        dados = self.anamnese.get('dados', {})
        
        msg = ["✅ *ANAMNESE FINALIZADA!*\n"]
        msg.append("Obrigado por completar o questionário.\n")
        
        # Red flags
        sintomas = dados.get('sintomas_alerta', [])
        red_flags = [s for s in sintomas if s not in ['nenhum']]
        if red_flags:
            msg.append("⚠️ *ATENÇÃO:* Identificamos alguns sintomas importantes que serão avaliados na consulta.\n")
        
        # Score ODI se calculado
        odi_campos = [k for k in dados.keys() if k.startswith('odi_')]
        if odi_campos:
            odi_respostas = {}
            for campo in odi_campos:
                chave = campo.replace('odi_', '')
                odi_respostas[chave] = dados[campo]
            score = calcular_odi(odi_respostas)
            msg.append(f"📊 *Índice de Incapacidade (ODI):* {score}%")
            msg.append(f"   _{interpretar_odi(score)}_\n")
        
        msg.append("O Dr. Felipe irá revisar suas respostas antes da consulta.")
        msg.append("\n🗓️ Nos vemos em breve!")
        
        return "\n".join(msg)
    
    def reiniciar(self):
        """Reinicia a anamnese"""
        if self.anamnese:
            atualizar_anamnese(self.anamnese['id'], status='cancelada')
        self.anamnese = criar_anamnese(self.paciente['id'])

# ============================================================
# FUNÇÕES DE INTERFACE
# ============================================================

def processar_mensagem(telefone: str, mensagem: str) -> str:
    """
    Processa mensagem do WhatsApp e retorna resposta
    Ponto de entrada principal para o bot
    """
    bot = AnamneseBot(telefone)
    
    # Comandos especiais
    if mensagem.lower() in ['/reiniciar', '/restart', 'reiniciar']:
        bot.reiniciar()
        return "🔄 Anamnese reiniciada!\n\n" + bot.get_pergunta_atual()[0]
    
    if mensagem.lower() in ['/status', 'status']:
        step = bot.get_step_atual()
        total = len(FLUXO_ANAMNESE) + len(ODI_STEPS)
        return f"📊 Progresso: {step}/{total} ({int(step/total*100)}%)"
    
    if mensagem.lower() in ['/iniciar', '/start', 'iniciar', 'oi', 'olá', 'ola', 'começar', 'comecar']:
        # Iniciar nova anamnese se não tem uma em andamento
        if not bot.anamnese:
            pergunta, _ = bot.get_pergunta_atual()
            return pergunta
        else:
            # Já tem anamnese em andamento
            pergunta, _ = bot.get_pergunta_atual()
            return f"Você já tem uma anamnese em andamento.\n\nContinuando de onde parou:\n\n{pergunta}"
    
    # Processar resposta (cria paciente/anamnese se necessário)
    return bot.processar_resposta(mensagem)

# ============================================================
# CLI para testes
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python anamnese_bot.py <telefone> <mensagem>")
        print("Exemplo: python anamnese_bot.py 11999999999 'João Silva'")
        sys.exit(1)
    
    telefone = sys.argv[1]
    mensagem = ' '.join(sys.argv[2:])
    
    resposta = processar_mensagem(telefone, mensagem)
    print(resposta)

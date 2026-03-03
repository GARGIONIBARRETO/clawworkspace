#!/usr/bin/env python3
"""
API para integração com Supabase - Clínica Dr. Felipe Barreto
Gerencia pacientes e anamneses
"""

import json
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

# Carregar credenciais
SECRETS_PATH = "/root/.secrets/supabase_clinica.json"

def load_credentials():
    with open(SECRETS_PATH) as f:
        return json.load(f)

CREDS = load_credentials()
SUPABASE_URL = CREDS["url"]
SUPABASE_KEY = CREDS["anon_key"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ============================================================
# PACIENTES
# ============================================================

def criar_paciente(nome: str, telefone: str, data_nascimento: str = None, 
                   sexo: str = None, profissao: str = None, email: str = None) -> Dict:
    """Cria um novo paciente"""
    data = {
        "nome": nome,
        "telefone": telefone,
        "data_nascimento": data_nascimento,
        "sexo": sexo,
        "profissao": profissao,
        "email": email
    }
    # Remove campos None
    data = {k: v for k, v in data.items() if v is not None}
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/pacientes",
        headers=HEADERS,
        json=data
    )
    
    if response.status_code == 201:
        return response.json()[0]
    elif response.status_code == 409:  # Conflito - já existe
        return buscar_paciente_por_telefone(telefone)
    else:
        raise Exception(f"Erro ao criar paciente: {response.text}")

def buscar_paciente_por_telefone(telefone: str) -> Optional[Dict]:
    """Busca paciente pelo telefone"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/pacientes?telefone=eq.{telefone}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        results = response.json()
        return results[0] if results else None
    return None

def buscar_paciente_por_nome(nome: str) -> List[Dict]:
    """Busca pacientes pelo nome (busca parcial)"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/pacientes?nome=ilike.*{nome}*",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()
    return []

def buscar_paciente_por_id(paciente_id: str) -> Optional[Dict]:
    """Busca paciente pelo ID"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/pacientes?id=eq.{paciente_id}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        results = response.json()
        return results[0] if results else None
    return None

def listar_pacientes(limit: int = 50) -> List[Dict]:
    """Lista todos os pacientes"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/pacientes?order=nome.asc&limit={limit}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()
    return []

def atualizar_paciente(paciente_id: str, dados: Dict) -> Dict:
    """Atualiza dados do paciente"""
    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/pacientes?id=eq.{paciente_id}",
        headers=HEADERS,
        json=dados
    )
    
    if response.status_code == 200:
        return response.json()[0]
    raise Exception(f"Erro ao atualizar paciente: {response.text}")

# ============================================================
# ANAMNESES
# ============================================================

def criar_anamnese(paciente_id: str, dados_iniciais: Dict = None) -> Dict:
    """Cria uma nova anamnese para o paciente"""
    data = {
        "paciente_id": paciente_id,
        "dados": dados_iniciais or {},
        "status": "em_andamento",
        "step_atual": 1
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/anamneses",
        headers=HEADERS,
        json=data
    )
    
    if response.status_code == 201:
        return response.json()[0]
    raise Exception(f"Erro ao criar anamnese: {response.text}")

def buscar_anamnese_em_andamento(paciente_id: str) -> Optional[Dict]:
    """Busca anamnese em andamento do paciente"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/anamneses?paciente_id=eq.{paciente_id}&status=eq.em_andamento&order=created_at.desc&limit=1",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        results = response.json()
        return results[0] if results else None
    return None

def buscar_anamnese_por_id(anamnese_id: str) -> Optional[Dict]:
    """Busca anamnese pelo ID"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/anamneses?id=eq.{anamnese_id}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        results = response.json()
        return results[0] if results else None
    return None

def atualizar_anamnese(anamnese_id: str, dados: Dict = None, step: int = None, 
                       status: str = None, odi_score: float = None, 
                       ndi_score: float = None, red_flags: List[str] = None) -> Dict:
    """Atualiza anamnese"""
    update_data = {"updated_at": datetime.now().isoformat()}
    
    if dados is not None:
        # Merge com dados existentes
        anamnese = buscar_anamnese_por_id(anamnese_id)
        if anamnese:
            dados_atuais = anamnese.get("dados", {})
            dados_atuais.update(dados)
            update_data["dados"] = dados_atuais
        else:
            update_data["dados"] = dados
    
    if step is not None:
        update_data["step_atual"] = step
    if status is not None:
        update_data["status"] = status
    if odi_score is not None:
        update_data["odi_score"] = odi_score
    if ndi_score is not None:
        update_data["ndi_score"] = ndi_score
    if red_flags is not None:
        update_data["red_flags"] = red_flags
    
    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/anamneses?id=eq.{anamnese_id}",
        headers=HEADERS,
        json=update_data
    )
    
    if response.status_code == 200:
        return response.json()[0]
    raise Exception(f"Erro ao atualizar anamnese: {response.text}")

def finalizar_anamnese(anamnese_id: str, odi_score: float = None, 
                       ndi_score: float = None, red_flags: List[str] = None) -> Dict:
    """Finaliza a anamnese"""
    return atualizar_anamnese(
        anamnese_id, 
        status="finalizada",
        odi_score=odi_score,
        ndi_score=ndi_score,
        red_flags=red_flags
    )

def listar_anamneses_paciente(paciente_id: str) -> List[Dict]:
    """Lista todas as anamneses de um paciente"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/anamneses?paciente_id=eq.{paciente_id}&order=created_at.desc",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()
    return []

def buscar_anamneses_recentes(limit: int = 10) -> List[Dict]:
    """Busca anamneses recentes com dados do paciente"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/anamneses?select=*,pacientes(nome,telefone)&order=created_at.desc&limit={limit}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()
    return []

# ============================================================
# CÁLCULOS DE SCORES
# ============================================================

def calcular_odi(respostas: Dict[str, int]) -> float:
    """
    Calcula o Oswestry Disability Index
    respostas: dict com as seções (1-10) e valores (0-5)
    Retorna porcentagem de incapacidade
    """
    # Seções do ODI
    secoes = ['intensidade_dor', 'cuidados_pessoais', 'levantar_objetos', 
              'caminhar', 'sentar', 'ficar_em_pe', 'dormir', 
              'vida_sexual', 'vida_social', 'viajar']
    
    total = 0
    secoes_respondidas = 0
    
    for secao in secoes:
        if secao in respostas and respostas[secao] is not None:
            total += respostas[secao]
            secoes_respondidas += 1
    
    if secoes_respondidas == 0:
        return 0.0
    
    max_score = secoes_respondidas * 5
    return round((total / max_score) * 100, 1)

def calcular_ndi(respostas: Dict[str, int]) -> float:
    """
    Calcula o Neck Disability Index
    respostas: dict com as seções (1-10) e valores (0-5)
    Retorna porcentagem de incapacidade
    """
    # Seções do NDI
    secoes = ['intensidade_dor', 'cuidados_pessoais', 'levantar_objetos',
              'leitura', 'dor_cabeca', 'concentracao', 'trabalho',
              'dirigir', 'dormir', 'lazer']
    
    total = 0
    secoes_respondidas = 0
    
    for secao in secoes:
        if secao in respostas and respostas[secao] is not None:
            total += respostas[secao]
            secoes_respondidas += 1
    
    if secoes_respondidas == 0:
        return 0.0
    
    max_score = secoes_respondidas * 5
    return round((total / max_score) * 100, 1)

def interpretar_odi(score: float) -> str:
    """Interpreta o score ODI"""
    if score <= 20:
        return "Incapacidade mínima"
    elif score <= 40:
        return "Incapacidade moderada"
    elif score <= 60:
        return "Incapacidade severa"
    elif score <= 80:
        return "Incapacitado"
    else:
        return "Acamado ou exagero dos sintomas"

def interpretar_ndi(score: float) -> str:
    """Interpreta o score NDI"""
    if score <= 8:
        return "Sem incapacidade"
    elif score <= 28:
        return "Incapacidade leve"
    elif score <= 48:
        return "Incapacidade moderada"
    elif score <= 68:
        return "Incapacidade severa"
    else:
        return "Incapacidade completa"

def detectar_red_flags(dados: Dict) -> List[str]:
    """Detecta red flags neurológicos na anamnese"""
    flags = []
    
    sintomas = dados.get("sintomas_alerta", {})
    
    if sintomas.get("fraqueza_pernas"):
        flags.append("🚨 Fraqueza nas pernas")
    if sintomas.get("fraqueza_bracos"):
        flags.append("🚨 Fraqueza nos braços")
    if sintomas.get("dificuldade_urina"):
        flags.append("🚨 URGENTE: Alteração esfincteriana (urina)")
    if sintomas.get("dificuldade_fezes"):
        flags.append("🚨 URGENTE: Alteração esfincteriana (fezes)")
    if sintomas.get("anestesia_sela"):
        flags.append("🚨 URGENTE: Anestesia em sela")
    if sintomas.get("perda_equilibrio"):
        flags.append("🚨 Perda de equilíbrio")
    if sintomas.get("dor_noturna"):
        flags.append("⚠️ Dor que acorda à noite")
    if sintomas.get("febre"):
        flags.append("🚨 Febre associada à dor")
    if sintomas.get("perda_peso"):
        flags.append("🚨 Perda de peso inexplicada")
    
    return flags

# ============================================================
# RESUMO E RELATÓRIO
# ============================================================

def gerar_resumo_anamnese(anamnese_id: str) -> str:
    """Gera resumo formatado da anamnese"""
    anamnese = buscar_anamnese_por_id(anamnese_id)
    if not anamnese:
        return "Anamnese não encontrada"
    
    paciente = buscar_paciente_por_id(anamnese["paciente_id"])
    dados = anamnese.get("dados", {})
    
    resumo = []
    resumo.append("=" * 50)
    resumo.append("RESUMO DA ANAMNESE")
    resumo.append("=" * 50)
    
    # Dados do paciente
    if paciente:
        resumo.append(f"\n📋 PACIENTE: {paciente.get('nome', 'N/A')}")
        resumo.append(f"📱 Telefone: {paciente.get('telefone', 'N/A')}")
        if paciente.get('data_nascimento'):
            resumo.append(f"🎂 Nascimento: {paciente.get('data_nascimento')}")
    
    # Red Flags
    red_flags = anamnese.get("red_flags", [])
    if red_flags:
        resumo.append("\n" + "⚠️ " * 10)
        resumo.append("🚨 RED FLAGS IDENTIFICADOS:")
        for flag in red_flags:
            resumo.append(f"  {flag}")
        resumo.append("⚠️ " * 10)
    
    # Scores
    if anamnese.get("odi_score"):
        score = anamnese["odi_score"]
        resumo.append(f"\n📊 ODI (Lombar): {score}% - {interpretar_odi(score)}")
    
    if anamnese.get("ndi_score"):
        score = anamnese["ndi_score"]
        resumo.append(f"📊 NDI (Cervical): {score}% - {interpretar_ndi(score)}")
    
    # Queixa principal
    if dados.get("queixa_principal"):
        resumo.append(f"\n💬 QUEIXA PRINCIPAL:")
        resumo.append(f"  {dados['queixa_principal']}")
    
    # Dor
    if dados.get("dor"):
        dor = dados["dor"]
        resumo.append(f"\n🎯 DOR:")
        if dor.get("localizacao"):
            resumo.append(f"  Localização: {', '.join(dor['localizacao'])}")
        if dor.get("intensidade_media"):
            resumo.append(f"  Intensidade média: {dor['intensidade_media']}/10")
        if dor.get("duracao"):
            resumo.append(f"  Duração: {dor['duracao']}")
    
    # Sono
    if dados.get("sono"):
        sono = dados["sono"]
        resumo.append(f"\n😴 SONO:")
        if sono.get("qualidade"):
            resumo.append(f"  Qualidade: {sono['qualidade']}")
        if sono.get("horas"):
            resumo.append(f"  Horas: {sono['horas']}")
    
    # Estresse
    if dados.get("estresse"):
        resumo.append(f"\n😰 ESTRESSE: {dados['estresse']}/10")
    
    # Medicamentos
    if dados.get("medicamentos"):
        resumo.append(f"\n💊 MEDICAMENTOS:")
        for med in dados["medicamentos"]:
            resumo.append(f"  - {med}")
    
    resumo.append("\n" + "=" * 50)
    resumo.append(f"Data: {anamnese.get('created_at', 'N/A')[:10]}")
    resumo.append(f"Status: {anamnese.get('status', 'N/A')}")
    resumo.append("=" * 50)
    
    return "\n".join(resumo)

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python clinica_api.py <comando> [args]")
        print("Comandos:")
        print("  listar_pacientes")
        print("  buscar_paciente <nome>")
        print("  criar_paciente <nome> <telefone>")
        print("  anamneses_recentes")
        print("  resumo_anamnese <anamnese_id>")
        sys.exit(1)
    
    comando = sys.argv[1]
    
    if comando == "listar_pacientes":
        pacientes = listar_pacientes()
        for p in pacientes:
            print(f"{p['nome']} - {p['telefone']}")
    
    elif comando == "buscar_paciente":
        nome = sys.argv[2]
        pacientes = buscar_paciente_por_nome(nome)
        for p in pacientes:
            print(json.dumps(p, indent=2, ensure_ascii=False))
    
    elif comando == "criar_paciente":
        nome = sys.argv[2]
        telefone = sys.argv[3]
        paciente = criar_paciente(nome, telefone)
        print(json.dumps(paciente, indent=2, ensure_ascii=False))
    
    elif comando == "anamneses_recentes":
        anamneses = buscar_anamneses_recentes()
        for a in anamneses:
            paciente = a.get("pacientes", {})
            print(f"{paciente.get('nome', 'N/A')} - {a['status']} - {a['created_at'][:10]}")
    
    elif comando == "resumo_anamnese":
        anamnese_id = sys.argv[2]
        print(gerar_resumo_anamnese(anamnese_id))
    
    else:
        print(f"Comando desconhecido: {comando}")

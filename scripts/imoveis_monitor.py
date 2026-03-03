#!/usr/bin/env python3
"""
Monitor de imóveis para encontrar pechinchas
Regiões: Vila Nova Conceição, Moema, Itaim Bibi
Critérios: até 200m², até R$ 3.000.000
"""

import json
import os
from datetime import datetime

SEEN_FILE = "/root/clawd/data/imoveis_vistos.json"
CRITERIA = {
    "max_price": 3000000,
    "max_area": 200,
    "regions": ["Vila Nova Conceição", "Moema", "Itaim Bibi"],
    "min_price_per_m2_deal": 12000,  # Abaixo disso é pechincha nessa região
}

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return json.load(f)
    return {"seen_ids": [], "last_check": None}

def save_seen(data):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_deal(price, area):
    """Verifica se é uma pechincha baseado no preço/m²"""
    if area <= 0:
        return False
    price_per_m2 = price / area
    # Nessa região, abaixo de R$ 15.000/m² já é interessante
    # Abaixo de R$ 12.000/m² é pechincha
    return price_per_m2 < 15000

def get_deal_score(price, area):
    """Retorna um score de 1-5 estrelas para a pechincha"""
    if area <= 0:
        return 0
    price_per_m2 = price / area
    if price_per_m2 < 10000:
        return 5  # Excelente
    elif price_per_m2 < 12000:
        return 4  # Muito bom
    elif price_per_m2 < 14000:
        return 3  # Bom
    elif price_per_m2 < 15000:
        return 2  # Interessante
    else:
        return 1  # Normal

def format_report():
    """Gera relatório de status do monitoramento"""
    data = load_seen()
    return f"""📊 **Monitor de Imóveis Ativo**

🎯 **Critérios:**
- Regiões: Vila Nova Conceição, Moema, Itaim Bibi
- Até R$ 3.000.000
- Até 200m²
- Alvo: < R$ 15.000/m² (pechincha: < R$ 12.000/m²)

📅 Última verificação: {data.get('last_check', 'Nunca')}
🏠 Imóveis já vistos: {len(data.get('seen_ids', []))}

💡 **Links para busca manual:**
- Loft: loft.com.br
- QuintoAndar: quintoandar.com.br
- Zap: zapimoveis.com.br
"""

if __name__ == "__main__":
    print(format_report())

#!/usr/bin/env python3

import os
import subprocess
import json

def extract_docx_full(filepath):
    """Extrai texto completo de DOCX"""
    try:
        # Tenta com unzip primeiro
        result = subprocess.run(
            ['unzip', '-p', filepath, 'word/document.xml'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            xml_content = result.stdout
            # Limpa XML
            import re
            text = xml_content.replace('</w:t>', '\n')
            text = re.sub('<[^>]+>', '', text)
            text = re.sub('\n\s*\n', '\n', text)
            return text.strip()
        
        # Tenta com pandoc como fallback
        result = subprocess.run(
            ['pandoc', '-f', 'docx', '-t', 'plain', filepath],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
            
        return None
        
    except Exception as e:
        return f"Erro: {str(e)}"

# Arquivos de endoscopia
arquivos_endoscopia = [
    '/root/.clawdbot/media/inbound/1f765f32-5fc8-4477-ae11-b08b834015ed.docx',
    '/root/.clawdbot/media/inbound/2f8baeda-8fc5-462e-baf5-6a03edcda6ad.docx',
    '/root/.clawdbot/media/inbound/7da54f28-df7d-47c6-a467-b8f0217ede8d.docx'
]

pedidos_endoscopia = []

for i, arquivo in enumerate(arquivos_endoscopia, 1):
    print(f"\n===== PEDIDO ENDOSCOPIA {i} =====")
    texto = extract_docx_full(arquivo)
    
    if texto and texto != "Erro":
        # Mostra todo o conteúdo (limitado a 2000 chars para visualização)
        print(texto[:2000])
        if len(texto) > 2000:
            print("\n[...continua...]")
        
        # Salva texto completo
        pedidos_endoscopia.append({
            'arquivo': os.path.basename(arquivo),
            'numero': i,
            'texto': texto
        })
        
        # Salva em arquivo
        output_file = f'/root/clawd/exemplos/pedido_endoscopia_{i}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f"\n✅ Texto completo salvo em: {output_file}")
    else:
        print("❌ Não foi possível extrair o conteúdo")

# Salva todos em JSON
if pedidos_endoscopia:
    with open('/root/clawd/exemplos/pedidos_endoscopia_todos.json', 'w', encoding='utf-8') as f:
        json.dump(pedidos_endoscopia, f, ensure_ascii=False, indent=2)
    print(f"\n📁 {len(pedidos_endoscopia)} pedidos salvos em JSON")

print("\n✅ Análise concluída!")
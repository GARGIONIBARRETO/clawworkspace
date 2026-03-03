#!/usr/bin/env python3

import os
import subprocess
import json

def extract_docx_text(filepath):
    """Extrai texto de DOCX usando unzip e parsing básico do XML"""
    try:
        # Extrai document.xml
        result = subprocess.run(
            ['unzip', '-p', filepath, 'word/document.xml'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return None
            
        xml_content = result.stdout
        
        # Remove tags XML de forma simples
        import re
        # Substitui </w:t> por quebra de linha para manter estrutura
        text = xml_content.replace('</w:t>', '\n')
        # Remove todas as outras tags
        text = re.sub('<[^>]+>', '', text)
        # Remove linhas vazias múltiplas
        text = re.sub('\n\s*\n', '\n', text)
        
        return text.strip()
        
    except Exception as e:
        return f"Erro: {str(e)}"

# Arquivos de pedidos de artrodese
arquivos_pedidos = [
    '/root/.clawdbot/media/inbound/159dbd68-8643-42f1-994b-045c4bc18523.docx',
    '/root/.clawdbot/media/inbound/92d8d176-cdb8-401b-9f04-f7552d968b9f.docx',
    '/root/.clawdbot/media/inbound/a68a4818-63a3-443c-a653-c922b6c162ca.docx',
    '/root/.clawdbot/media/inbound/ff3d94bf-b760-4857-a567-73468addbe32.docx'
]

pedidos_extraidos = []

for i, arquivo in enumerate(arquivos_pedidos, 1):
    print(f"\n===== PEDIDO {i} =====")
    texto = extract_docx_text(arquivo)
    
    if texto:
        # Mostra primeiros 1500 caracteres
        print(texto[:1500])
        if len(texto) > 1500:
            print("\n[...continua...]")
        
        # Salva texto completo
        pedidos_extraidos.append({
            'arquivo': os.path.basename(arquivo),
            'numero': i,
            'texto': texto
        })
        
        # Salva em arquivo separado
        output_file = f'/root/clawd/exemplos/pedido_artrodese_{i}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f"\nTexto completo salvo em: {output_file}")

# Salva todos os pedidos em JSON
with open('/root/clawd/exemplos/pedidos_artrodese_todos.json', 'w', encoding='utf-8') as f:
    json.dump(pedidos_extraidos, f, ensure_ascii=False, indent=2)

print("\n✅ Extração concluída!")
print(f"📁 Pedidos salvos em /root/clawd/exemplos/")
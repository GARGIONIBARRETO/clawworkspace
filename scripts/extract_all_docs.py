#!/usr/bin/env python3

import os
import subprocess
import json

def extract_docx_text(filepath):
    """Extrai texto de DOCX usando unzip"""
    try:
        result = subprocess.run(
            ['unzip', '-p', filepath, 'word/document.xml'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return None
            
        xml_content = result.stdout
        
        # Remove tags XML
        import re
        text = xml_content.replace('</w:t>', '\n')
        text = re.sub('<[^>]+>', '', text)
        text = re.sub('\n\s*\n', '\n', text)
        
        return text.strip()
        
    except Exception as e:
        return f"Erro: {str(e)}"

# Lista dos 7 arquivos
arquivos = [
    '/root/.clawdbot/media/inbound/d80ff5b7-395a-4244-bd4d-b2f5d54575c8.docx',
    '/root/.clawdbot/media/inbound/15b64aa9-8401-4abc-b75b-ea61e6e79cce.docx',
    '/root/.clawdbot/media/inbound/03d86a7f-1552-41bc-ad2b-65a837594cda.docx',
    '/root/.clawdbot/media/inbound/b68b2097-060c-4a41-b1d7-c46b42a78e4b.docx',
    '/root/.clawdbot/media/inbound/6f05fe28-67cf-483e-8369-d72bbd01cc6a.docx',
    '/root/.clawdbot/media/inbound/1de4ba4d-a51c-4801-ae1e-cccaa38db429.docx',
    '/root/.clawdbot/media/inbound/b3002e2b-6527-44e4-b228-39e52325d4d7.docx'
]

todos_documentos = []

for i, arquivo in enumerate(arquivos, 1):
    print(f"\n===== DOCUMENTO {i} =====")
    texto = extract_docx_text(arquivo)
    
    if texto:
        # Mostra primeiros 800 caracteres para identificar o tipo
        preview = texto[:800]
        print(preview)
        if len(texto) > 800:
            print("\n[...continua...]")
        
        # Identifica o tipo de documento
        tipo = "desconhecido"
        if "artrodese" in texto.lower():
            tipo = "artrodese"
        elif "endoscop" in texto.lower() or "percutâne" in texto.lower():
            tipo = "endoscopia/percutaneo"
        elif "bloqueio" in texto.lower():
            tipo = "bloqueio"
        elif "rizotomia" in texto.lower():
            tipo = "rizotomia"
        elif "vertebroplastia" in texto.lower():
            tipo = "vertebroplastia"
        elif "microdiscectomia" in texto.lower():
            tipo = "microdiscectomia"
        elif "laminectomia" in texto.lower():
            tipo = "laminectomia"
        
        print(f"\n🏷️ Tipo identificado: {tipo}")
        
        todos_documentos.append({
            'arquivo': os.path.basename(arquivo),
            'numero': i,
            'tipo': tipo,
            'texto': texto
        })
        
        # Salva individual
        output_file = f'/root/clawd/exemplos/doc_{i}_{tipo}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto)

# Salva resumo
with open('/root/clawd/exemplos/documentos_analisados.json', 'w', encoding='utf-8') as f:
    json.dump(todos_documentos, f, ensure_ascii=False, indent=2)

print(f"\n✅ Análise concluída!")
print(f"📁 {len(todos_documentos)} documentos processados")
print("\nResumo por tipo:")
tipos = {}
for doc in todos_documentos:
    tipo = doc['tipo']
    tipos[tipo] = tipos.get(tipo, 0) + 1

for tipo, count in tipos.items():
    print(f"  - {tipo}: {count} documento(s)")
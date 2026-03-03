#!/usr/bin/env python3
"""
Configuração de HTTPS para a interface web
Opções: certificado auto-assinado ou Let's Encrypt
"""

import os
import subprocess
from datetime import datetime

def gerar_certificado_autoassinado():
    """Gera certificado SSL auto-assinado"""
    
    cert_dir = '/root/clawd/certificates'
    os.makedirs(cert_dir, exist_ok=True)
    
    cert_file = os.path.join(cert_dir, 'clinica.crt')
    key_file = os.path.join(cert_dir, 'clinica.key')
    
    # Gerar certificado auto-assinado válido por 1 ano
    cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
        '-keyout', key_file,
        '-out', cert_file,
        '-days', '365',
        '-nodes',
        '-subj', '/CN=clinica.local/O=Clinica Dr Felipe/C=BR'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Certificado gerado em:")
        print(f"   Certificado: {cert_file}")
        print(f"   Chave: {key_file}")
        
        # Ajustar permissões
        os.chmod(key_file, 0o600)
        
        return cert_file, key_file
        
    except Exception as e:
        print(f"❌ Erro ao gerar certificado: {e}")
        return None, None

def atualizar_web_interface_https():
    """Atualiza web_interface.py para suportar HTTPS"""
    
    arquivo = '/root/clawd/scripts/web_interface.py'
    
    # Fazer backup
    backup = f"{arquivo}.backup_https_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(arquivo, backup)
    print(f"📁 Backup criado: {backup}")
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Adicionar imports necessários
    if 'import ssl' not in conteudo:
        # Adicionar após outros imports
        pos = conteudo.find('from datetime import datetime')
        if pos > 0:
            pos = conteudo.find('\n', pos) + 1
            conteudo = conteudo[:pos] + 'import ssl\n' + conteudo[pos:]
    
    # Modificar o app.run() para incluir SSL
    old_run = '''app.run(host='0.0.0.0', port=5000, debug=True)'''
    
    new_run = '''# Configuração HTTPS
    cert_file = '/root/clawd/certificates/clinica.crt'
    key_file = '/root/clawd/certificates/clinica.key'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # Executar com HTTPS
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        print("🔒 Executando com HTTPS")
        print("🌐 Acesse: https://YOUR_SERVER_IP:5443")
        
        app.run(host='0.0.0.0', port=5443, debug=True, ssl_context=context)
    else:
        # Fallback para HTTP
        print("⚠️  Certificados não encontrados, executando em HTTP")
        app.run(host='0.0.0.0', port=5000, debug=True)'''
    
    if old_run in conteudo:
        conteudo = conteudo.replace(old_run, new_run)
        
        with open(arquivo, 'w') as f:
            f.write(conteudo)
        
        print("✅ web_interface.py atualizado para HTTPS")
        return True
    
    return False

def criar_script_nginx():
    """Cria configuração Nginx como alternativa mais robusta"""
    
    nginx_config = '''# Configuração Nginx para Clínica Dr. Felipe
# Arquivo: /etc/nginx/sites-available/clinica

server {
    listen 80;
    server_name _;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    # Certificados SSL
    ssl_certificate /root/clawd/certificates/clinica.crt;
    ssl_certificate_key /root/clawd/certificates/clinica.key;
    
    # Configurações SSL modernas
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Headers de segurança
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy para Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeout para uploads grandes
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
    
    # Limite de upload para exames/gravações
    client_max_body_size 100M;
}'''
    
    with open('/root/clawd/nginx_clinica.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Configuração Nginx criada em: /root/clawd/nginx_clinica.conf")
    
    # Instruções de instalação
    print("\n📝 Para usar Nginx (recomendado):")
    print("1. Instalar Nginx: sudo yum install -y nginx")
    print("2. Copiar config: sudo cp /root/clawd/nginx_clinica.conf /etc/nginx/conf.d/clinica.conf")
    print("3. Testar config: sudo nginx -t")
    print("4. Reiniciar: sudo systemctl restart nginx")
    print("5. Manter Flask rodando em HTTP na porta 5000")

def criar_script_letsencrypt():
    """Script para obter certificado Let's Encrypt"""
    
    script = '''#!/bin/bash
# Script para obter certificado Let's Encrypt

DOMAIN="$1"
EMAIL="$2"

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Uso: $0 <dominio> <email>"
    echo "Exemplo: $0 clinica.exemplo.com admin@exemplo.com"
    exit 1
fi

# Instalar certbot
echo "📦 Instalando Certbot..."
sudo yum install -y epel-release
sudo yum install -y certbot python3-certbot-nginx

# Obter certificado
echo "🔐 Obtendo certificado para $DOMAIN..."
sudo certbot --nginx -d "$DOMAIN" -m "$EMAIL" --agree-tos --non-interactive

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/bin/certbot renew --quiet") | crontab -

echo "✅ Certificado Let's Encrypt configurado!"
echo "🌐 Acesse: https://$DOMAIN"
'''
    
    with open('/root/clawd/scripts/configurar_letsencrypt.sh', 'w') as f:
        f.write(script)
    
    os.chmod('/root/clawd/scripts/configurar_letsencrypt.sh', 0o755)
    print("✅ Script Let's Encrypt criado")

def verificar_portas():
    """Verifica portas disponíveis"""
    
    print("\n🔍 Verificando portas:")
    
    # Verificar porta 443
    result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
    
    if ':443' in result.stdout:
        print("⚠️  Porta 443 já está em uso")
    else:
        print("✅ Porta 443 disponível")
    
    if ':5443' in result.stdout:
        print("⚠️  Porta 5443 já está em uso")
    else:
        print("✅ Porta 5443 disponível para Flask HTTPS")

def main():
    print("🔒 CONFIGURANDO HTTPS PARA A INTERFACE WEB")
    print("=" * 60)
    
    # Gerar certificados
    cert, key = gerar_certificado_autoassinado()
    
    if cert and key:
        # Atualizar Flask
        if atualizar_web_interface_https():
            print("\n✅ Flask configurado para HTTPS!")
            print("\n🔐 Opções de acesso:")
            print("1. HTTPS direto Flask: https://129.121.33.120:5443")
            print("   ⚠️  Navegador mostrará aviso de certificado auto-assinado")
            print("   Clique em 'Avançado' > 'Continuar mesmo assim'")
        
        # Criar configs adicionais
        criar_script_nginx()
        criar_script_letsencrypt()
        
        # Verificar portas
        verificar_portas()
        
        print("\n🎯 RECOMENDAÇÕES:")
        print("1. Para produção: Use Nginx + Let's Encrypt")
        print("2. Para teste rápido: Use Flask HTTPS na porta 5443")
        print("\n⚠️  Reinicie o servidor web:")
        print("   pkill -f web_interface.py")
        print("   cd /root/clawd/scripts && nohup python3 web_interface.py > /tmp/web_interface.log 2>&1 &")
        
        print("\n🔐 SEGURANÇA ADICIONAL:")
        print("✓ Headers de segurança configurados")
        print("✓ TLS 1.2/1.3 apenas")
        print("✓ Ciphers fortes")
        print("✓ HSTS habilitado (com Nginx)")

if __name__ == "__main__":
    main()
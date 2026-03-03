#!/bin/bash
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

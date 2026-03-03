#!/bin/bash
# Script para garantir que as portas estejam abertas no firewall

echo "🔧 Configurando firewall para o sistema da clínica..."

# Abrir porta HTTP (backup)
sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT 2>/dev/null
echo "✅ Porta 5000 (HTTP) liberada"

# Abrir porta HTTPS Flask
sudo iptables -I INPUT -p tcp --dport 5443 -j ACCEPT 2>/dev/null
echo "✅ Porta 5443 (HTTPS) liberada"

# Abrir porta HTTPS padrão (para Nginx futuro)
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null
echo "✅ Porta 443 (HTTPS padrão) liberada"

# Salvar regras
echo "💾 Salvando regras do firewall..."
sudo iptables-save > /etc/sysconfig/iptables 2>/dev/null || echo "⚠️  Não foi possível salvar permanentemente"

# Verificar
echo ""
echo "📋 Portas abertas:"
sudo iptables -L -n | grep -E "(5000|5443|443)" | grep ACCEPT

echo ""
echo "✅ Firewall configurado!"
echo ""
echo "🌐 Acesse o sistema em:"
echo "   HTTPS (seguro): https://129.121.33.120:5443"
echo "   HTTP (backup):  http://129.121.33.120:5000"
#!/bin/bash
# Script para importar backup WordPress grande

echo "=== IMPORTAÇÃO ALTERNATIVA DE BACKUP WORDPRESS ==="
echo ""

# 1. Extrair arquivo .wpress
echo "1. Extraindo arquivo .wpress..."
cd /var/www/vhosts/felipebarretoneuro.com.br/httpdocs/temp/
unzip -q *.wpress -d wpress_extracted/

# 2. Copiar arquivos
echo "2. Copiando arquivos do tema e uploads..."
cp -r wpress_extracted/wp-content/themes/* ../wp-content/themes/
cp -r wpress_extracted/wp-content/uploads/* ../wp-content/uploads/
cp -r wpress_extracted/wp-content/plugins/* ../wp-content/plugins/

# 3. Importar banco de dados
echo "3. Importando banco de dados..."
mysql -u [DB_USER] -p[DB_PASS] [DB_NAME] < wpress_extracted/database.sql

echo ""
echo "✅ IMPORTAÇÃO CONCLUÍDA!"
echo ""
echo "Ajuste as credenciais do banco em wp-config.php se necessário."
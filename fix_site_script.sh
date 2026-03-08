#!/bin/bash
# Script para corrigir o site do Dr. Felipe Barreto

echo "🔧 SCRIPT DE CORREÇÃO DO SITE - Dr. Felipe Barreto"
echo "================================================="
echo ""

# Diretório do site (ajustar se necessário)
SITE_DIR="/var/www/vhosts/felipebarretoneuro.com.br/httpdocs"

echo "📁 Verificando diretório do site..."
if [ ! -d "$SITE_DIR" ]; then
    echo "❌ Diretório não encontrado. Ajuste o caminho no script."
    exit 1
fi

echo "✅ Diretório encontrado: $SITE_DIR"
echo ""

# Fazer backup
echo "💾 Criando backup dos arquivos atuais..."
BACKUP_DIR="$SITE_DIR/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$SITE_DIR"/*.html "$SITE_DIR"/*.css "$SITE_DIR"/*.js "$SITE_DIR"/css "$SITE_DIR"/js "$BACKUP_DIR" 2>/dev/null

echo "✅ Backup criado em: $BACKUP_DIR"
echo ""

# Criar diretório anamnese
echo "📂 Criando diretório /anamnese..."
mkdir -p "$SITE_DIR/anamnese"

# Mover arquivos da anamnese
echo "🚚 Movendo arquivos da anamnese..."
mv "$SITE_DIR"/*.html "$SITE_DIR"/*.css "$SITE_DIR"/*.js "$SITE_DIR"/css "$SITE_DIR"/js "$SITE_DIR/anamnese/" 2>/dev/null

# Criar novo index.html
echo "📄 Criando novo index.html..."
cat > "$SITE_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dr. Felipe Barreto - Neurocirurgia de Coluna</title>
    <meta http-equiv="refresh" content="0; url=https://doctoralia.com.br/felipe-barreto">
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
        }
        .container {
            padding: 40px;
        }
        h1 {
            margin-bottom: 20px;
        }
        a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Dr. Felipe Barreto</h1>
        <p>Redirecionando para o sistema de agendamento...</p>
        <p>Se não for redirecionado automaticamente, <a href="https://doctoralia.com.br/felipe-barreto">clique aqui</a>.</p>
    </div>
</body>
</html>
EOF

# Criar .htaccess
echo "⚙️ Criando arquivo .htaccess..."
cat > "$SITE_DIR/.htaccess" << 'EOF'
RewriteEngine On

# Redirecionar /anamnese para a pasta anamnese
RewriteRule ^anamnese/?$ /anamnese/index.html [L]

# Página principal
DirectoryIndex index.html
EOF

# Ajustar permissões
echo "🔐 Ajustando permissões..."
chown -R $(stat -c '%U:%G' "$SITE_DIR") "$SITE_DIR"/*
chmod 644 "$SITE_DIR"/*.html "$SITE_DIR"/.htaccess 2>/dev/null

echo ""
echo "✅ CORREÇÃO CONCLUÍDA!"
echo ""
echo "📊 RESUMO:"
echo "- Site principal: Redirecionando para Doctoralia"
echo "- Anamnese: Disponível em /anamnese"
echo "- Backup: Salvo em $BACKUP_DIR"
echo ""
echo "🌐 URLs funcionando:"
echo "- felipebarretoneuro.com.br → Doctoralia"
echo "- felipebarretoneuro.com.br/anamnese → Formulário"
echo ""
echo "💡 Para restaurar o backup:"
echo "cp -r $BACKUP_DIR/* $SITE_DIR/"
echo ""
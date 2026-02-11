#!/bin/bash
# Backup Script - Sincroniza workspace com GitHub
# Uso: ./scripts/backup_github.sh [mensagem do commit]

set -e

WORKSPACE="/root/clawd"
cd "$WORKSPACE"

# Mensagem padrão com timestamp
MSG="${1:-Backup automático $(date '+%Y-%m-%d %H:%M')}"

# Arquivos/pastas a ignorar (secrets, cache, etc)
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Secrets
.secrets/
*.credentials.json
*_credentials.json

# Cache e temporários
__pycache__/
*.pyc
.cache/
test-results/
node_modules/

# Logs
*.log

# Arquivos grandes de mídia (opcional)
# *.mp4
# *.wav

# Sistema
.DS_Store
Thumbs.db
EOF
    echo "✓ .gitignore criado"
fi

# Adiciona todos os arquivos
git add -A

# Verifica se há mudanças
if git diff --cached --quiet; then
    echo "✓ Nenhuma mudança para commitar"
    exit 0
fi

# Commit
git commit -m "$MSG"
echo "✓ Commit: $MSG"

# Push (se remote configurado)
if git remote | grep -q origin; then
    git push origin master
    echo "✓ Push realizado com sucesso!"
else
    echo "⚠ Remote 'origin' não configurado. Execute:"
    echo "  git remote add origin git@github.com:SEU_USUARIO/SEU_REPO.git"
    echo "  git push -u origin master"
fi

echo ""
echo "Backup concluído em $(date '+%Y-%m-%d %H:%M:%S')"

#!/bin/bash

echo "🐘 Instalando PostgreSQL localmente..."
echo "================================="

# Instalar PostgreSQL
dnf install -y postgresql postgresql-server postgresql-contrib

# Inicializar banco
postgresql-setup --initdb

# Iniciar serviço
systemctl enable postgresql
systemctl start postgresql

# Verificar status
systemctl status postgresql --no-pager -l

echo ""
echo "✅ PostgreSQL instalado! Configurando usuário..."

# Configurar usuário para a clínica
sudo -u postgres psql << 'EOF'
CREATE USER clinica_admin WITH PASSWORD 'clinica2026!';
CREATE DATABASE clinica_dr_felipe OWNER clinica_admin;
GRANT ALL PRIVILEGES ON DATABASE clinica_dr_felipe TO clinica_admin;
\q
EOF

echo ""
echo "🔧 Configurando acesso local..."

# Permitir acesso local
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /var/lib/pgsql/data/postgresql.conf

# Configurar autenticação
cat > /var/lib/pgsql/data/pg_hba.conf << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

# Reiniciar PostgreSQL
systemctl restart postgresql

echo ""
echo "✅ PostgreSQL configurado!"
echo "🔗 Detalhes da conexão:"
echo "   Host: localhost"
echo "   Port: 5432" 
echo "   Database: clinica_dr_felipe"
echo "   User: clinica_admin"
echo "   Password: clinica2026!"
echo ""
echo "🧪 Testando conexão..."

# Testar conexão
PGPASSWORD='clinica2026!' psql -h localhost -U clinica_admin -d clinica_dr_felipe -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "✅ Conexão funcionando!"
else
    echo "❌ Erro na conexão"
fi
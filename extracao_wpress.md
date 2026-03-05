# COMO EXTRAIR ARQUIVO .WPRESS

## NO SEU COMPUTADOR:

1. Baixe o arquivo .wpress do Plesk
2. Renomeie para .zip (mude a extensão)
3. Extraia com WinRAR/7zip
4. Dentro você vai encontrar:
   - database.sql (banco de dados)
   - plugins/ (todos os plugins)
   - themes/ (seu tema)
   - uploads/ (todas as imagens)

## UPLOAD MANUAL:

1. **Banco de dados:**
   - Plesk → Bancos de dados → phpMyAdmin
   - Importe o database.sql

2. **Arquivos:**
   - /wp-content/themes/ → suba o tema
   - /wp-content/uploads/ → suba as imagens
   - /wp-content/plugins/ → suba os plugins

3. **Ajustar wp-config.php:**
   - Atualize com os dados do banco novo
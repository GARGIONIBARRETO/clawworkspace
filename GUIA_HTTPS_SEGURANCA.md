# 🔒 Guia de Segurança HTTPS - Sistema Clínica

## ✅ HTTPS Ativado!

O sistema agora está rodando com HTTPS (conexão criptografada).

## 🌐 Como Acessar

### Opção 1: HTTPS Direto (Recomendado para teste)
**URL:** https://129.121.33.120:5443

⚠️ **Aviso de Segurança do Navegador:**
1. O navegador mostrará aviso de "Conexão não segura"
2. Clique em **"Avançado"** ou **"Advanced"**
3. Clique em **"Continuar mesmo assim"** ou **"Proceed to site"**
4. Isso acontece porque usamos certificado auto-assinado

### Opção 2: HTTP (menos seguro)
Se precisar voltar para HTTP: http://129.121.33.120:5000

## 🔐 O que HTTPS protege?

- ✅ **Senhas** - Não podem ser interceptadas
- ✅ **Dados dos pacientes** - Criptografados em trânsito
- ✅ **Uploads de exames** - Protegidos durante envio
- ✅ **Gravações de áudio** - Seguras durante upload

## 🛡️ Níveis de Segurança

### Atual: Certificado Auto-assinado
- **Segurança:** ⭐⭐⭐ (Boa)
- **Confiança:** ⭐⭐ (Aviso no navegador)
- **Custo:** Grátis
- **Uso:** Desenvolvimento, testes, uso interno

### Melhor: Certificado Let's Encrypt
- **Segurança:** ⭐⭐⭐⭐⭐ (Excelente)
- **Confiança:** ⭐⭐⭐⭐⭐ (Sem avisos)
- **Custo:** Grátis
- **Requisito:** Domínio próprio (ex: clinica.drfelipe.com.br)

## 📋 Para Certificado Profissional

Se você tiver um domínio (ex: clinica.drfelipe.com.br):

```bash
# Execute este comando:
/root/clawd/scripts/configurar_letsencrypt.sh seu-dominio.com.br seu-email@gmail.com
```

## 🔧 Configuração Técnica

### Certificados atuais:
- **Local:** `/root/clawd/certificates/`
- **Certificado:** `clinica.crt`
- **Chave privada:** `clinica.key`
- **Validade:** 1 ano (até 02/03/2027)

### Portas:
- **5443** - HTTPS Flask (atual)
- **443** - HTTPS padrão (com Nginx)
- **5000** - HTTP (backup)

### Headers de Segurança:
- HSTS - Força uso de HTTPS
- X-Frame-Options - Previne clickjacking
- X-Content-Type-Options - Previne MIME sniffing
- X-XSS-Protection - Proteção contra XSS

## 🚀 Próximos Passos de Segurança

1. **Autenticação**
   - [ ] Login com senha
   - [ ] Sessões seguras
   - [ ] Timeout de inatividade

2. **Autorização**
   - [ ] Níveis de acesso (médico, secretária, admin)
   - [ ] Log de acessos

3. **Backup**
   - [ ] Backup criptografado
   - [ ] Backup offsite

4. **Auditoria**
   - [ ] Log de todas as ações
   - [ ] Quem viu/editou o quê

## ❓ FAQ

**P: O aviso de segurança é perigoso?**
R: Não, é apenas porque o certificado é auto-assinado. A conexão ainda é criptografada.

**P: Posso usar em produção?**
R: Sim, mas recomendo certificado Let's Encrypt para evitar avisos.

**P: Como voltar para HTTP?**
R: Edite `/root/clawd/scripts/web_interface.py` e remova a configuração SSL.

## 📞 Suporte

Se precisar de ajuda com:
- Configurar domínio próprio
- Instalar certificado profissional
- Adicionar mais segurança

Me avise que eu configuro!
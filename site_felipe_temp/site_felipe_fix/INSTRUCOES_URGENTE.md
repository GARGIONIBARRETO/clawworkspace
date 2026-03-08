# 🚨 INSTRUÇÕES URGENTES - CONSERTAR O SITE

Felipe, seu site está mostrando a página de anamnese ao invés do site principal.

## SOLUÇÃO RÁPIDA (5 minutos):

### Opção 1: Via Plesk (Recomendado)

1. **Acesse o Plesk**
   - Entre em satyr.armata.cloud
   - Vá até o domínio felipebarretoneuro.com.br

2. **Renomeie os arquivos atuais**
   - No gerenciador de arquivos, vá para: `/httpdocs/`
   - Crie uma pasta chamada `anamnese`
   - MOVA todos os arquivos atuais (index.html, css/, js/) para dentro da pasta `anamnese`

3. **Faça upload do novo index.html**
   - Use o arquivo `index.html` que criei (está nesta pasta)
   - Faça upload direto na raiz `/httpdocs/`

4. **Configure o .htaccess**
   - Faça upload do arquivo `.htaccess` para a raiz também
   - Isso garantirá que /anamnese continue funcionando

### Opção 2: Solução Temporária IMEDIATA

Se precisar resolver AGORA MESMO:

1. No Plesk, vá em **Configurações de Hospedagem**
2. Adicione um redirecionamento:
   - De: felipebarretoneuro.com.br
   - Para: https://doctoralia.com.br/felipe-barreto
   - Tipo: Temporário (302)

Isso pelo menos tira a página de anamnese do ar e manda pro Doctoralia.

## ESTRUTURA FINAL IDEAL:

```
/httpdocs/
  ├── index.html (site principal)
  ├── .htaccess
  └── anamnese/
      ├── index.html (formulário de anamnese)
      ├── css/
      ├── js/
      └── outros arquivos...
```

## LINKS FUNCIONANDO:
- felipebarretoneuro.com.br → Site principal
- felipebarretoneuro.com.br/anamnese → Formulário de anamnese

## PRECISA DE AJUDA?

Me avise que eu te guio passo a passo pelo Plesk ou crio um script automatizado!
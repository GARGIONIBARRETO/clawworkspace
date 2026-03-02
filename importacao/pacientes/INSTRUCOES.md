# 👥 IMPORTAÇÃO DE PACIENTES

## Formato do CSV

Seu arquivo CSV deve ter essas colunas (obrigatórias em **negrito**):

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| **nome** | Nome completo do paciente | João Silva Santos |
| **cpf** | CPF (com ou sem formatação) | 123.456.789-00 ou 12345678900 |
| rg | RG do paciente | 12.345.678-9 |
| telefone | Telefone de contato | (11) 99999-9999 |
| email | E-mail do paciente | joao@email.com |
| endereco | Endereço completo | Rua das Flores, 123 - São Paulo/SP |
| data_nascimento | Data no formato YYYY-MM-DD | 1980-05-15 |
| convenio | Convênio médico | Unimed, SulAmérica, Particular |

## Exemplo de Arquivo

```csv
nome,cpf,rg,telefone,email,endereco,data_nascimento,convenio
João Silva Santos,123.456.789-00,12.345.678-9,(11) 99999-9999,joao@email.com,Rua das Flores 123 - São Paulo/SP,1980-05-15,Unimed
Maria Oliveira,987.654.321-00,98.765.432-1,(11) 88888-8888,maria@email.com,Av. Paulista 456 - São Paulo/SP,1975-12-20,SulAmérica
```

## Como Usar

1. **Salve seus dados** em formato CSV nesta pasta
2. **Execute:** `python3 /root/clawd/scripts/importador_completo.py pacientes`
3. **Ou importação completa:** `python3 /root/clawd/scripts/importador_completo.py`

⚠️ **IMPORTANTE:** CPF será usado como chave única. Pacientes duplicados serão ignorados.
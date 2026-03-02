# 📋 INSTRUÇÕES DE IMPORTAÇÃO - DR. FELIPE

## 🌐 Opção 1: INTERFACE WEB (Mais Fácil!)

1. Acesse: **http://129.121.33.120:5000**
2. Login: **drfelipe** / Senha: **clinica2026**
3. Use o menu para adicionar pacientes e consultas manualmente

## 💻 Opção 2: IMPORTAÇÃO EM MASSA

### Passo 1: Prepare seus dados em CSV

Já criei 2 templates para você:

#### 📁 `template_consultas_felipe.csv`
Para suas consultas recentes:
- nome_paciente
- data_consulta (formato: AAAA-MM-DD)
- queixa_principal
- historia_doenca
- exame_fisico
- hipotese_diagnostica
- conduta
- retorno
- observacoes

#### 📁 `template_historico_felipe.csv`
Para histórico médico completo:
- nome_paciente
- diagnosticos_previos
- cirurgias_anteriores
- medicacoes_cronicas
- alergias
- exames_importantes
- observacoes_gerais

### Passo 2: Execute o importador

```bash
# Para importar tudo de uma vez:
python3 /root/clawd/importar_consultas_felipe.py

# Ou direto com arquivo:
python3 /root/clawd/importar_consultas_felipe.py template_consultas_felipe.csv
python3 /root/clawd/importar_consultas_felipe.py template_historico_felipe.csv
```

## 💡 DICAS IMPORTANTES

1. **Nome do paciente**: O sistema busca por nome parcial! 
   - "João Silva" encontra "João Silva Santos"
   - "Maria" encontra "Maria Santos"

2. **Datas**: Use formato AAAA-MM-DD (ex: 2024-03-15)

3. **Campos vazios**: Sem problema! Deixe em branco o que não tiver

4. **Excel para CSV**: 
   - Salve como "CSV UTF-8" no Excel
   - Ou me mande o Excel que eu converto!

## 🚀 EXEMPLO RÁPIDO

Se você tem uma lista simples tipo:

```
João Silva - 15/06/2024
Dor lombar há 6 meses, piora ao sentar
Lasègue negativo, contratura L4-L5
Lombalgia mecânica
Fisioterapia + Meloxicam
Retorno em 30 dias
```

É só colocar no CSV e rodar o importador!

## ⚠️ PRECISA DE AJUDA?

- Me manda o arquivo (Excel, Word, PDF, foto) que eu formato pra você!
- O sistema aceita qualquer formato de nome
- Histórico antigo pode ser texto corrido

---

**Servidor Web**: http://129.121.33.120:5000 (drfelipe/clinica2026)
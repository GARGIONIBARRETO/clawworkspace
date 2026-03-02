# 🩺 IMPORTAÇÃO DE CONSULTAS

## Formato do CSV

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| **cpf_paciente** | CPF do paciente (deve existir no sistema) | 123.456.789-00 |
| **data_consulta** | Data da consulta (YYYY-MM-DD) | 2023-01-15 |
| medico | Nome do médico | Dr. Felipe |
| motivo | Motivo da consulta | Dor na coluna lombar |
| observacoes | Observações da consulta | Paciente relata dor há 2 semanas... |

## Exemplo

```csv
cpf_paciente,data_consulta,medico,motivo,observacoes
123.456.789-00,2023-01-15,Dr. Felipe,Dor lombar,Paciente com dor há 2 semanas
987.654.321-00,2023-01-20,Dr. Felipe,Retorno,Melhora significativa após tratamento
```

⚠️ **ATENÇÃO:** Os pacientes devem ser importados ANTES das consultas!
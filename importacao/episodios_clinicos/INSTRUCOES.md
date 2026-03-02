# 🏥 IMPORTAÇÃO DE EPISÓDIOS CLÍNICOS

## Formato do CSV

Para casos clínicos mais complexos que consultas simples:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| **cpf_paciente** | CPF do paciente | 123.456.789-00 |
| data_episodio | Data do episódio (YYYY-MM-DD) | 2023-01-15 |
| tipo_episodio | Tipo do episódio | Cirurgia, Internação, Emergência |
| descricao | Descrição detalhada | Paciente apresentou quadro de... |
| diagnostico | Diagnóstico médico | Hérnia de disco L4-L5 |
| tratamento | Tratamento realizado | Discectomia percutânea |

## Exemplo

```csv
cpf_paciente,data_episodio,tipo_episodio,descricao,diagnostico,tratamento
123.456.789-00,2023-01-15,Cirurgia,Cirurgia de hérnia discal,Hérnia L4-L5,Discectomia
987.654.321-00,2023-02-10,Emergência,Dor intensa súbita,Crise lombar,Bloqueio anestésico
```

📋 **INFO:** Episódios serão salvos como consultas detalhadas no sistema.
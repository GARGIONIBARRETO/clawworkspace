# Sistema Clínica Dr. Felipe Barreto

## Estrutura

```
clinica/
├── pacientes/          # Cadastro de pacientes (JSON)
├── consultas/          # Histórico de consultas
├── exames/             # Resultados de exames (PDFs + análises)
├── receitas/           # Receitas e prescrições geradas
├── templates/          # Templates de mensagens WhatsApp
└── config.json         # Configurações do sistema
```

## Funcionalidades

### Prontuário Eletrônico
- Cadastro completo de pacientes
- Histórico de consultas com anamnese
- Registro de exames com comparativos
- Prescrições e receitas

### Integração WhatsApp
- Confirmação de consultas (automático)
- Envio de receitas e pedidos de exames
- Recebimento de exames dos pacientes
- Lembretes de retorno

### Integração Google Calendar
- Sync com agenda da clínica
- Detecção de novos agendamentos
- Trigger automático de confirmações

## Fluxo de Confirmação

1. Paciente agenda consulta (Doctoralia/Calendar)
2. Sistema detecta novo agendamento
3. 24h antes: envia WhatsApp de confirmação
4. Paciente confirma ou reagenda
5. Atualiza status no sistema


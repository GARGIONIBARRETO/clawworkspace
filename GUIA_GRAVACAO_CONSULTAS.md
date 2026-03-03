# 🎤 Guia de Gravação de Consultas

## Como Gravar uma Consulta

### Opção 1: Gravar Direto no Navegador
1. Entre na página do paciente
2. Clique no botão **"Gravar Consulta"** (amarelo) 🎤
3. Clique no botão vermelho grande para iniciar
4. Converse normalmente com o paciente
5. Clique novamente para parar
6. Revise o áudio e clique em "Salvar e Transcrever"

### Opção 2: Upload de Áudio (Celular/Gravador)
1. Grave no seu celular ou gravador digital
2. Na página do paciente → "Gravar Consulta"
3. Use a seção "Upload de Áudio"
4. Selecione o arquivo (MP3, M4A, WAV)
5. Clique em "Enviar e Transcrever"

## O que o Sistema Faz Automaticamente

### 1. Transcrição com Whisper
- Converte áudio em texto usando IA da OpenAI
- Reconhece português brasileiro
- Alta precisão mesmo com termos médicos

### 2. Processamento Inteligente
O sistema analisa a transcrição e extrai:
- **Queixa Principal** - "Paciente refere dor lombar..."
- **História da Doença** - Início, evolução, fatores
- **Exame Físico** - Achados mencionados
- **Hipóteses** - Diagnósticos considerados
- **Condutas** - Medicações, exames, orientações

### 3. Criação do Episódio Clínico
- Preenche automaticamente o prontuário
- Você pode revisar e ajustar
- Salva tudo organizado no sistema

## Exemplo Prático

**Você grava:**
> "Paciente de 45 anos vem hoje com queixa de dor lombar há 3 meses. 
> Começou após carregar peso no trabalho. Piora ao sentar, melhora deitado.
> Ao exame: Lasègue negativo, força preservada, reflexos normais.
> Vou prescrever anti-inflamatório e fisioterapia. 
> Solicitar ressonância da coluna lombar."

**Sistema organiza em:**
- **QP:** Dor lombar há 3 meses
- **HDA:** Início após esforço físico, piora sentado, melhora deitado
- **Exame:** Lasègue negativo, força e reflexos normais
- **Conduta:** Anti-inflamatório, fisioterapia, RNM lombar

## Dicas para Melhor Resultado

1. **Fale claramente** - Mencione números e doses
2. **Seja estruturado** - "Ao exame físico...", "Vou prescrever..."
3. **Dite pontuação** - "vírgula", "ponto", "dois pontos"
4. **Ambiente silencioso** - Reduz erros de transcrição

## Privacidade e Segurança

- Áudios ficam salvos localmente no servidor
- Transcrição via API segura da OpenAI
- Dados não são compartilhados
- Você pode deletar gravações após transcrever

## Comandos Úteis

### Transcrever manualmente:
```bash
cd /root/clawd/scripts
./transcrever_audio.py /path/to/audio.mp3
```

### Ver transcrições:
```bash
ls /root/clawd/gravacoes/paciente_*/
```

## Próximas Melhorias

- [ ] Reconhecimento de múltiplas vozes (médico vs paciente)
- [ ] Templates por especialidade
- [ ] Integração com comandos de voz
- [ ] App mobile para gravação
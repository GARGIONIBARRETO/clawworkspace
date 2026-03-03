# Documentação - Anamnese e Pedidos Cirúrgicos

## 📋 Módulo de Questionários de Anamnese

### Funcionalidades

1. **Importação de Questionários**
   - Formato JSON padronizado
   - Integração com formulários web (TypeForm, Google Forms)
   - Processamento automático de respostas

2. **Integração ao Prontuário**
   - Converte anamnese em entrada estruturada
   - Cria registro na tabela de consultas
   - Mantém histórico completo

3. **Gestão de Anamneses**
   - Lista anamneses pendentes
   - Controle de status (pendente/revisado/integrado)
   - Exportação para PDF (futura implementação)

### Como Usar

#### 1. Criar tabela de anamnese (primeira vez)
```bash
python3 /root/clawd/scripts/clinica_manager.py
# Menu: 6 → 5 (Criar tabela de anamnese)
```

#### 2. Importar questionário JSON
```bash
# Exemplo de arquivo em: /root/clawd/exemplos/anamnese_exemplo.json
python3 /root/clawd/scripts/clinica_manager.py
# Menu: 6 → 1 (Importar questionário JSON)
```

#### 3. Integração Web

Para TypeForm/Google Forms, veja o exemplo em:
`/root/clawd/exemplos/integracao_web_exemplo.py`

Fluxo:
1. Paciente preenche formulário online
2. Webhook envia dados para seu servidor
3. Sistema processa e armazena anamnese
4. Médico revisa e integra ao prontuário

### Estrutura JSON de Anamnese

```json
{
  "queixa_principal": "texto",
  "historia_doenca_atual": "texto detalhado",
  "tempo_sintomas": "duração",
  "sintomas": {
    "gerais": "febre, peso...",
    "neurologicos": "parestesias...",
    "cardiovasculares": "dispneia...",
    "respiratorios": "tosse...",
    "gastrointestinais": "náuseas...",
    "genitourinarios": "disúria...",
    "musculoesqueleticos": "dores..."
  },
  "antecedentes": {
    "pessoais": "HAS, DM...",
    "familiares": "CA, cardiopatias...",
    "cirurgicos": "cirurgias prévias..."
  },
  "medicacoes": ["med1", "med2"],
  "alergias": "medicamentosas/alimentares",
  "habitos": {
    "tabagismo": "status",
    "etilismo": "status",
    "atividade_fisica": "frequência",
    "sono_qualidade": "bom/ruim"
  }
}
```

## 🏥 Módulo de Pedidos Cirúrgicos

### Funcionalidades

1. **Templates de Cirurgia**
   - Templates pré-configurados para cirurgias comuns
   - Códigos TUSS/AMB inclusos
   - Personalizável por paciente

2. **Geração de Pedidos**
   - Pedidos completos com justificativa
   - Códigos de procedimentos e materiais
   - Exportação HTML/PDF

3. **Gestão de Códigos**
   - Busca de códigos TUSS
   - Tabela de procedimentos
   - OPME detalhado

### Como Usar

#### 1. Criar tabelas (primeira vez)
```bash
python3 /root/clawd/scripts/clinica_manager.py
# Menu: 7 → 7 (Criar tabelas)
```

#### 2. Criar templates padrão
```bash
python3 /root/clawd/scripts/clinica_manager.py
# Menu: 7 → 6 (Criar templates padrão)
```

Templates disponíveis:
- Hérnia Discal Lombar - Microdiscectomia
- Estenose de Canal - Laminectomia

#### 3. Gerar pedido com template
```bash
python3 /root/clawd/scripts/clinica_manager.py
# Menu: 7 → 2 (Usar template)
```

#### 4. Gerar pedido customizado
```bash
# Para casos específicos
python3 /root/clawd/scripts/clinica_manager.py
# Menu: 7 → 1 (Gerar novo pedido)
```

### Estrutura do Pedido Cirúrgico

O pedido inclui:
- **Identificação**: Paciente, convênio, matrícula
- **Diagnóstico**: CIDs, descrição clínica
- **Procedimento**: Principal e adicionais
- **Justificativa**: Completa e fundamentada
- **Materiais**: OPME detalhado
- **Códigos**: TUSS/AMB para autorização
- **Equipe**: Cirurgião, auxiliares, anestesia
- **Logística**: Tempo, internação, UTI

### Exemplo de Pedido

Veja exemplo completo em:
`/root/clawd/exemplos/pedido_cirurgico_exemplo.json`

### Códigos TUSS Comuns - Neurocirurgia Coluna

#### Procedimentos
- **31403047**: Hérnia discal lombar via posterior
- **31403055**: Descompressão radicular
- **31403039**: Laminectomia descompressiva
- **31401066**: Microcirurgia (microscópio)
- **31403136**: Descompressão medular/radicular

#### Materiais
- **07020902**: Sistema afastamento MIS
- **07010478**: Agente hemostático
- **07021470**: Substituto dural

## 📊 Integração com Sistema Existente

Ambos os módulos se integram com:
- Tabela de pacientes
- Tabela de consultas
- Sistema de relatórios
- Exportação de dados

## 🔄 Workflow Recomendado

### Para Anamnese
1. Paciente agenda consulta
2. Recebe link do questionário
3. Preenche online (TypeForm/Google)
4. Sistema importa automaticamente
5. Médico revisa na consulta
6. Integra ao prontuário

### Para Pedidos Cirúrgicos
1. Consulta e indicação cirúrgica
2. Gera pedido (template ou custom)
3. Exporta HTML/PDF
4. Envia para convênio
5. Acompanha autorização
6. Atualiza status

## 🚀 Próximas Melhorias

- [ ] Exportação PDF nativa
- [ ] Assinatura digital
- [ ] Envio automático para convênios
- [ ] App mobile para preenchimento
- [ ] Dashboard de autorizações
- [ ] Integração com WhatsApp
- [ ] Lembretes automáticos

## 📞 Suporte

Para dúvidas ou sugestões:
- Documentação: `/root/clawd/docs/`
- Exemplos: `/root/clawd/exemplos/`
- Scripts: `/root/clawd/scripts/`
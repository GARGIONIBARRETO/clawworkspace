# Templates de Artrodese Lombar - Documentação

## 🏥 Templates Disponíveis

### 1. Artrodese Posterior com Instrumentação
- **Indicação**: Espondilolistese, instabilidade segmentar
- **Procedimento**: Fixação pedicular com barras e parafusos
- **Materiais principais**: 
  - 6 parafusos pediculares
  - 4 barras de titânio
  - Enxerto ósseo
- **Tempo cirúrgico**: 4 horas
- **UTI**: Sim
- **Internação**: 3 dias

### 2. Artrodese Anterior (ALIF)
- **Indicação**: Discopatia degenerativa severa
- **Procedimento**: Acesso anterior com cage intersomático
- **Materiais principais**:
  - Cage ALIF
  - Placa anterior + parafusos
  - Substituto ósseo
- **Tempo cirúrgico**: 3 horas
- **UTI**: Não (geralmente)
- **Internação**: 2 dias
- **Observação**: Necessita cirurgião vascular

### 3. Artrodese 360° (Combinada)
- **Indicação**: Instabilidade severa, pseudoartrose
- **Procedimento**: ALIF + fixação posterior
- **Materiais**: Combinação anterior + posterior
- **Tempo cirúrgico**: 6-8 horas
- **UTI**: Sim
- **Internação**: 4 dias
- **Observação**: Pode ser em 1 ou 2 tempos

### 4. Artrodese com Extensão ao Ilíaco
- **Indicação**: Falha L5-S1, construções longas
- **Procedimento**: Fixação lombo-pélvica
- **Materiais principais**:
  - Parafusos pediculares + ilíacos
  - Conectores offset
  - Cross-links
- **Tempo cirúrgico**: 5-6 horas
- **UTI**: Sim
- **Internação**: 4 dias
- **Observação**: Monitorização obrigatória

## 📋 Códigos TUSS Principais

### Procedimentos Base
- **30712114**: Espondilolistese - tratamento cirúrgico
- **30715016**: Artrodese com instrumentação/segmento
- **30714024**: Artrodese via anterior/póstero-lateral
- **30715091**: Descompressão medular/cauda equina
- **30732026**: Enxerto ósseo

### Materiais OPME
- **07020902**: Parafuso pedicular
- **07020910**: Barra de conexão
- **07020929**: Bloqueador
- **07020937**: Cage intersomático
- **07020945**: Placa anterior
- **07020961**: Parafuso ilíaco
- **07020970**: Conector/Offset
- **07020988**: Cross-link

## 🔧 Customização dos Pedidos

Cada template pode ser customizado com:
- Dados específicos do paciente
- Ajuste de quantidades de material
- Observações particulares
- Códigos adicionais conforme necessidade

## 📝 Elementos Essenciais do Pedido

1. **História clínica detalhada**
   - Tempo de evolução
   - Tratamentos prévios
   - Falha do conservador

2. **Justificativa técnica**
   - Achados de imagem
   - Déficits neurológicos
   - Scores funcionais (Oswestry, VAS)

3. **Materiais com justificativa**
   - Quantidade exata
   - Marcas sugeridas
   - Fornecedores

4. **Cuidados especiais**
   - Monitorização
   - Hemoderivados
   - Radioscopia
   - UTI

## 🚀 Como Usar

1. No sistema principal:
   ```
   python3 /root/clawd/scripts/clinica_manager.py
   Menu → 7 → 2 (Usar template)
   ```

2. Escolha o template apropriado

3. Customize conforme necessário:
   - Convênio e matrícula
   - Detalhes específicos
   - Observações adicionais

4. Exporte para HTML/PDF

## ⚠️ Observações Importantes

- **Monitorização neurofisiológica**: Obrigatória em casos complexos
- **Hemoderivados**: Reservar conforme complexidade
- **Radioscopia**: Sempre disponível
- **Cell saver**: Recomendado em cirurgias longas
- **Equipe vascular**: Para acessos anteriores

## 📊 Referência Rápida

| Template | Tempo | UTI | Internação | Complexidade |
|----------|-------|-----|------------|--------------|
| Posterior | 4h | Sim | 3 dias | Média-Alta |
| ALIF | 3h | Não | 2 dias | Média |
| 360° | 6-8h | Sim | 4 dias | Alta |
| Ilíaco | 5-6h | Sim | 4 dias | Alta |

---

*Baseado em protocolos atualizados e códigos TUSS 2024/2025*
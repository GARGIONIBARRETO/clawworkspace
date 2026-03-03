# 🏥 Sistema de Validação de Cirurgia de Coluna

## 📋 Visão Geral

Sistema completo para geração, validação e armazenamento de pedidos de cirurgia de coluna, baseado no Manual de Codificação SBC/SBOT/SBN.

## 🚀 Componentes do Sistema

### 1. **Validador de Códigos** (`validador_codigos_coluna.py`)
- Base de dados com todos os códigos CBHPM de coluna
- Validação automática de pedidos
- Verificação de incompatibilidades
- Sugestões de códigos complementares

### 2. **Gerador de Pedidos** (`gerador_pedido_cirurgia.py`)
- Templates pré-configurados para cirurgias comuns
- Cálculo automático de quantidades
- Estimativa de tempo cirúrgico
- Formatação para impressão

### 3. **Integração com BD** (`integracao_pedidos_cirurgia_db.py`)
- Armazenamento de pedidos
- Histórico de validações
- Templates customizados
- Relatórios estatísticos

## 💻 Como Usar

### Instalação

```bash
# Criar tabelas no banco
python3 scripts/integracao_pedidos_cirurgia_db.py
```

### Exemplo 1: Validar Pedido Manual

```python
from validador_codigos_coluna import ValidadorCodigosColuna

validador = ValidadorCodigosColuna()

# Criar pedido manual
pedido = {
    "procedimentos": [
        {"codigo": "3.07.15.18-0", "quantidade": 2, "descricao": "Hérnia disco lombar"},
        {"codigo": "3.07.15.09-1", "quantidade": 2, "descricao": "Descompressão"},
        {"codigo": "4.08.11.02-6", "quantidade": 1, "descricao": "Radioscopia"}
    ],
    "niveis": "L4-L5-S1"
}

# Validar
resultado = validador.validar_pedido(pedido)
print(validador.gerar_relatorio(resultado))
```

### Exemplo 2: Gerar Pedido com Template

```python
from gerador_pedido_cirurgia import GeradorPedidoCirurgia

gerador = GeradorPedidoCirurgia()

# Usar template
pedido = gerador.gerar_pedido("hernia_lombar_simples", {
    "niveis": "L4-L5-S1",  # 2 segmentos
    "condicoes": ["estenose_associada", "laminectomia_necessaria"],
    "observacoes": "Paciente com déficit motor"
})

# Imprimir formatado
print(gerador.formatar_pedido_texto(pedido))
```

### Exemplo 3: Integração Completa

```python
from integracao_pedidos_cirurgia_db import IntegracaoPedidosCirurgiaDB
from gerador_pedido_cirurgia import GeradorPedidoCirurgia

# Inicializar
integracao = IntegracaoPedidosCirurgiaDB()
gerador = GeradorPedidoCirurgia()

# Gerar pedido
pedido = gerador.gerar_pedido("artrodese_lombar", {
    "niveis": "L3-L4-L5",
    "condicoes": ["monitorizacao_indicada"]
})

# Salvar no banco
pedido_id = integracao.salvar_pedido(
    paciente_id=123,
    pedido_dict=pedido,
    medico_solicitante="Dr. Felipe Barreto",
    data_prevista="2026-03-15"
)
```

## 📝 Templates Disponíveis

### 1. **hernia_lombar_simples**
- Hérnia de disco lombar básica
- Inclui: discectomia, descompressão, radioscopia
- Opcionais: estenose, laminectomia, monitorização

### 2. **artrodese_lombar**
- Artrodese posterior com instrumentação
- Inclui: artrodese, descompressão, enxerto, radioscopia
- Opcionais: hérnia associada, monitorização

### 3. **artrodese_360**
- Artrodese anterior + posterior
- Aplica regra especial de cobrança 360°
- Inclui ambos os acessos

### 4. **estenose_canal**
- Descompressão de estenose
- Inclui: tratamento microcirúrgico, laminectomia

### 5. **hernia_cervical**
- Hérnia cervical anterior
- Inclui: discectomia cervical, artrodese
- Opcional: monitorização para mielopatia

## 🔍 Buscar Códigos

```python
# Buscar por termo
resultados = gerador.buscar_codigo("infiltração")
for r in resultados:
    print(f"{r['codigo']} - {r['descricao']} ({r['porte']})")
```

## 📊 Relatórios

```python
# Gerar relatório de uso
relatorio = integracao.gerar_relatorio_pedidos(
    data_inicio="2026-01-01",
    data_fim="2026-03-31"
)

# Códigos mais utilizados
for codigo in relatorio['codigos_mais_utilizados']:
    print(f"{codigo['codigo']}: usado {codigo['frequencia']} vezes")
```

## ⚠️ Validações Automáticas

O sistema verifica automaticamente:

1. **Código existe** na base CBHPM
2. **Descrição compatível** com o oficial
3. **Quantidade correta** para tipo de cobrança
4. **Radioscopia presente** (aviso se não)
5. **Incompatibilidades** (ex: endoscopia vs acesso aberto)
6. **Sugestões** de códigos complementares

## 🎯 Regras Importantes

### Multiplicação de Códigos
- **Por segmento**: L4-L5-S1 = 2 segmentos
- **Por vértebra**: L4, L5, S1 = 3 vértebras
- **Por estrutura**: Bilateral = 2x
- **Uma vez**: Independente da extensão

### Cirurgia 360°
- **1º tempo**: 100% código principal + 50% secundários
- **2º tempo**: 75% de todos os códigos

### Monitorização Neurofisiológica
- Código exclusivo da equipe de monitorização
- Não repassar para equipe cirúrgica

## 📋 Checklist Pré-Validação

Antes de enviar o pedido, verifique:

- [ ] Níveis especificados corretamente
- [ ] Radioscopia incluída (se aplicável)
- [ ] Descompressão se há compressão neural
- [ ] Laminectomia se remove lâmina
- [ ] Enxerto se faz artrodese
- [ ] Quantidade correta por tipo de cobrança
- [ ] Descrições compatíveis com CBHPM
- [ ] Considerar códigos sugeridos

## 🆘 Suporte

Em caso de dúvidas:
1. Consulte o manual completo em `/referencias/`
2. Use a busca de códigos do sistema
3. Verifique os exemplos nos scripts

---

💡 **Dica:** Execute os scripts com exemplos para entender melhor o funcionamento!
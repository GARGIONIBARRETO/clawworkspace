# Análise das Consultas Importadas - 02/03/2026

## Resumo do Problema
Das 1480 consultas importadas, 689 (46.6%) estão sem evolução/observações.

## Origem dos Dados

### 1. Doctoralia (maioria dos registros)
- **611 consultas** de vários locais
- **Problema:** Sistema Doctoralia exporta apenas dados básicos (data, local, tipo)
- **Sem evolução:** 577 consultas (94%)

Locais identificados:
- CLINIDA DIA: 319 consultas (313 sem observações - 98%)
- Consultório Dr. Felipe Barreto: 292 consultas (222 sem observações - 76%)
- Personal Ortopedia: 29 consultas (27 sem observações - 93%)
- Telemedicina: 88 consultas (58 sem observações - 66%)

### 2. CLINICA CUORE
- **35 consultas** (todas de 02/03/2026)
- **Todas com observações completas** ✓
- Incluem: idade, profissão, queixa principal

### 3. Episódios Clínicos
- **Diversos registros** importados individualmente
- Alguns com descrições, outros sem

## Análise Detalhada

### Consultas SEM Observações (exemplos recentes):
```
19/02 - SANDRA CERBONCINI LUCAS - Consulta neurocirurgia
11/02 - Edson Carvalho Machado - Retorno
11/02 - LORENZO DOS SANTOS - Retorno  
05/02 - Álvaro André Detogne - Consulta
29/01 - ELIZABETE FERREIRA - Consulta
```

### Consultas COM Observações (exemplos):
```
02/03 - Rafaella Rodrigues - "12 anos, Dor lombar há 1 ano"
02/03 - Nilson Vieira - "52 anos, gerente RH, Parestesia"
02/03 - Patricia Verdi - "52 anos, comunicação visual, travamento..."
```

## Causa Raiz
O Doctoralia exporta apenas a estrutura básica das consultas (agenda), não o conteúdo clínico (prontuário). Por isso temos:
- ✓ Data da consulta
- ✓ Local/Tipo
- ✗ História clínica
- ✗ Exame físico
- ✗ Conduta

## Soluções Possíveis

### 1. Recuperação Manual
- Acessar prontuários no Doctoralia um por um
- Extrair texto das evoluções
- Atualizar no banco local

### 2. Importação Complementar
- Se houver backup ou export completo do Doctoralia
- Importar arquivo de episódios clínicos

### 3. Priorização
- Focar nas consultas mais recentes
- Pacientes em acompanhamento ativo
- Casos complexos/cirúrgicos

## Próximos Passos
1. Verificar se existe export completo do Doctoralia com prontuários
2. Identificar pacientes prioritários para recuperação manual
3. Configurar sistema novo para capturar evolução obrigatoriamente
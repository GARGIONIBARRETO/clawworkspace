# 🎉 Novos Templates de Procedimentos Endoscópicos/Percutâneos!

Baseado nos pedidos que você enviou, criei **5 novos templates** para procedimentos minimamente invasivos:

## 🔬 Templates Implementados

### 1️⃣ **Endoscopia Percutânea**
- Discectomia endoscópica para hérnia focal
- Preserva anatomia, recuperação rápida
- 2h cirurgia | Day hospital possível

### 2️⃣ **Rizotomia por Radiofrequência**
- Para síndrome facetária confirmada
- Alívio duradouro (6-24 meses)
- 1-2h | Ambulatorial

### 3️⃣ **Nucleoplastia**
- Descompressão discal por coblation
- Hérnia contida < 6mm
- 1h | Day hospital

### 4️⃣ **Bloqueio Epidural**
- Interlaminar ou transforaminal
- Alívio rápido da radiculopatia
- 30min | Ambulatorial

### 5️⃣ **Vertebroplastia**
- Fratura osteoporótica dolorosa
- Cimento PMMA
- 1-2h | 1 dia internação

## 🚀 Como Usar

```bash
python3 /root/clawd/scripts/clinica_manager.py
```
**Menu 7** → **Opção 2** → Escolha entre opções 7-11

## ✅ Vantagens dos Procedimentos Percutâneos

- 💉 **Anestesia local** + sedação leve
- 🏃 **Recuperação rápida** (dias vs semanas)
- 🏥 **Day hospital** na maioria dos casos
- 📍 **Preservação anatômica**
- 💰 **Menor custo** vs cirurgia aberta

## 📊 Quando Indicar Cada Um?

| Problema | 1ª Linha | 2ª Linha |
|----------|----------|----------|
| Hérnia focal | Endoscopia | Microdiscectomia |
| Dor facetária | Rizotomia | Artrodese |
| Hérnia contida | Nucleoplastia | Endoscopia |
| Radiculopatia aguda | Bloqueio | Cirurgia |
| Fratura vertebral | Vertebroplastia | Cifoplastia |

## 📋 Códigos TUSS Inclusos

- `31403063` - Discectomia percutânea
- `31401058` - Rizotomia RF
- `31401074` - Bloqueio nervoso
- `31403071` - Vertebroplastia
- `40811026` - Radioscopia

## 💡 Fluxo Sugerido

1. **Falha conservador** → Avaliação
2. **Imagem adequada** → Selecionar procedimento
3. **Gerar pedido** com template
4. **Personalizar** dados do paciente
5. **Exportar** HTML/PDF

## 📚 Documentação Completa

- `/root/clawd/docs/TEMPLATES_ENDOSCOPIA_PERCUTANEA.md` - Guia detalhado
- Seleção de pacientes
- Complicações e manejo
- Algoritmo de tratamento

---

🎯 **Total de templates disponíveis agora: 11**
- 6 cirurgias abertas
- 5 procedimentos percutâneos

Cobrindo todo espectro de tratamento da coluna! 🏥
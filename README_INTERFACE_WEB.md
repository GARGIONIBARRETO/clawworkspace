# 🌐 Interface Web - Sistema Clínica Dr. Felipe

## 🚀 Acesso Rápido
**Link:** http://129.121.33.120:5000

---

## ✨ NOVAS FUNCIONALIDADES ADICIONADAS

### 📋 **1. Importação Completa**

**Tipos de dados suportados:**
- ✅ **Pacientes** (CSV) - dados básicos
- ✅ **Consultas** (CSV) - histórico médico
- ✅ **Episódios Clínicos** (CSV) - casos complexos
- ✅ **Bioimpedância** (CSV) - peso, IMC, gordura, músculo
- ✅ **Exames de Sangue** (CSV) - hemograma, glicemia, etc
- ✅ **Anexos** (JPG, PNG, PDF) - imagens de exames

### 👤 **2. Detalhes do Paciente com Abas**

**Acesse:** http://129.121.33.120:5000/pacientes → Clique em "Ver Detalhes"

**Abas disponíveis:**
- 🩺 **Consultas** - histórico médico completo
- ⚖️ **Bioimpedância** - evolução corporal em tabela
- 🔬 **Exames** - resultados laboratoriais organizados  
- 📎 **Anexos** - imagens de ressonâncias, raios-X, etc

---

## 📥 COMO IMPORTAR SEUS DADOS

### **1. Pacientes (Primeiro passo)**
```
Formato: CPF, Nome, Telefone, Convênio, etc
Template: http://129.121.33.120:5000/templates/pacientes_template.csv
```

### **2. Bioimpedância**
```
Formato: CPF_Paciente, Data, Peso, Altura, IMC, Gordura%, Músculo, Água%
Template: http://129.121.33.120:5000/templates/bioimpedancia_template_cpf.csv
```

### **3. Exames de Sangue**
```
Formato: CPF_Paciente, Data, Tipo_Exame, Laboratório, Parâmetros_JSON
Template: http://129.121.33.120:5000/templates/exames_laboratoriais_template.csv
```

### **4. Anexos (Imagens de Exames)**
```
Formato do nome: CPF_tipo_exame.extensao
Exemplos:
- 12345678900_ressonancia_lombar.jpg
- 98765432100_raio_x_coluna.pdf
- 11111111111_hemograma.jpg
```

---

## 🎯 FLUXO RECOMENDADO

### **Passo 1: Organize seus arquivos**
1. **Extraia dados** do seu sistema antigo
2. **Organize em CSVs** usando os templates
3. **Renomeie anexos** no formato CPF_tipo_exame.extensao

### **Passo 2: Importação**
1. **Pacientes primeiro** → http://129.121.33.120:5000/importar
2. **Depois consultas/episódios** 
3. **Em seguida bioimpedância e exames**
4. **Por último os anexos** (imagens)

### **Passo 3: Verificar**
1. **Dashboard** → ver estatísticas gerais
2. **Pacientes** → verificar se todos foram importados
3. **Detalhes** → confirmar dados nas abas

---

## 💡 DICAS IMPORTANTES

### **📂 Para Anexos:**
- **Nome correto:** `12345678900_ressonancia.jpg`
- **Formatos:** JPG, PNG, PDF
- **Organização:** Automática por paciente
- **Visualização:** Direto na aba "Anexos" do paciente

### **🔬 Para Exames JSON:**
```json
{
  "hemoglobina": 14.2,
  "leucocitos": 7200,
  "glicose": 95
}
```

### **⚖️ Para Bioimpedância:**
- Facilita acompanhamento de evolução
- Gráficos automáticos da progressão
- Controle de peso e composição corporal

---

## 🔧 COMANDOS ÚTEIS

### **Verificar Status:**
```bash
python3 /root/clawd/scripts/verificar_importacao.py
```

### **Reiniciar Interface:**
```bash
# Parar (Ctrl+C no terminal)
# Iniciar novamente
cd /root/clawd/scripts && python3 web_interface.py
```

### **Backup Manual:**
```bash
python3 /root/clawd/scripts/db_local_adapter.py
```

---

## 📊 DASHBOARD

**Métricas em tempo real:**
- 👥 **Total de pacientes**
- 🩺 **Consultas registradas** 
- 🔬 **Exames laboratoriais**
- ⚖️ **Medições bioimpedância**
- 📋 **Consultas recentes**

---

## 🎉 RESULTADO FINAL

Após importação completa, você terá:

✅ **Sistema 100% local e privado**  
✅ **Interface web moderna e responsiva**  
✅ **Histórico completo por paciente**  
✅ **Anexos organizados automaticamente**  
✅ **Dados facilmente acessíveis**  
✅ **Backup automático PostgreSQL**  

**🚀 Seu consultório digital está pronto!**
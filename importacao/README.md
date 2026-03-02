# 📥 IMPORTAÇÃO DE DADOS - Sistema Clínica Dr. Felipe

## Estrutura de Pastas

### 📁 `/pacientes/`
**Dados básicos dos pacientes**
- Formato: CSV com colunas: nome, cpf, rg, telefone, email, endereco, data_nascimento, convenio
- Template disponível em: `/root/clawd/templates/pacientes_template.csv`
- Comando: `python3 /root/clawd/scripts/import_dados.py pacientes`

### 📁 `/consultas/`
**Histórico de consultas**
- Formato: CSV com colunas: cpf_paciente, data_consulta, medico, motivo, observacoes
- Deve referenciar pacientes já existentes pelo CPF
- Comando: `python3 /root/clawd/scripts/import_dados.py consultas`

### 📁 `/episodios_clinicos/`
**Episódios clínicos detalhados**
- Formato: CSV com colunas: cpf_paciente, data_episodio, tipo_episodio, descricao, diagnostico, tratamento
- Para casos mais complexos que consultas simples
- Comando: `python3 /root/clawd/scripts/import_dados.py episodios`

### 📁 `/anexos/`
**Arquivos e imagens**

#### `/anexos/exames_imagem/`
- Ressonâncias, tomografias, raios-X
- Organizados por CPF do paciente: `123456789/ressonancia_2023-01-15.jpg`

#### `/anexos/fotos_exames/`
- Fotos de exames físicos, laudos, etc.
- Organizados por CPF do paciente: `123456789/foto_exame_2023-01-15.jpg`

## Como Usar

1. **Copie seus arquivos** para as pastas correspondentes
2. **Para CSVs:** use os templates como referência
3. **Para anexos:** organize por CPF do paciente (criar subpasta com CPF)
4. **Execute a importação:** `python3 /root/clawd/scripts/importador_completo.py`

## Ordem Recomendada

1. Primeiro importe **pacientes**
2. Depois **consultas** e **episódios clínicos**
3. Por último, **anexos** (serão associados automaticamente aos pacientes)

---
**📞 Dúvidas:** Chame o Max!
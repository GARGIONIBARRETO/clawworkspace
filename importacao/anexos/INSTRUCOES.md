# 📎 IMPORTAÇÃO DE ANEXOS

## Organização por CPF

Organize seus arquivos em **subpastas** usando o **CPF do paciente** como nome:

```
anexos/
├── exames_imagem/
│   ├── 12345678900/          ← CPF do paciente
│   │   ├── ressonancia_2023-01-15.jpg
│   │   ├── tomografia_2023-02-10.pdf
│   │   └── raio_x_coluna.png
│   └── 98765432100/
│       └── ressonancia_lombar.jpg
└── fotos_exames/
    ├── 12345678900/
    │   ├── foto_exame_fisico.jpg
    │   └── laudo_manuscrito.pdf
    └── 98765432100/
        └── postura_paciente.jpg
```

## Tipos de Anexos

### 📸 `/exames_imagem/`
- Ressonâncias magnéticas
- Tomografias
- Raios-X
- Ultrassons
- Outros exames de imagem

### 📷 `/fotos_exames/`
- Fotos de exames físicos
- Laudos fotografados
- Posturas do paciente
- Anotações manuscritas

## Formatos Aceitos
- **Imagens:** JPG, PNG, GIF, WEBP
- **Documentos:** PDF
- **Outros:** qualquer formato será preservado

## Como Usar

1. **Organize** seus arquivos em pastas com CPF do paciente
2. **Coloque** cada pasta de CPF dentro do tipo correto (exames_imagem ou fotos_exames)
3. **Execute:** `python3 /root/clawd/scripts/importador_completo.py anexos`

📁 **RESULTADO:** Arquivos serão copiados para `/root/clawd/anexos_pacientes/paciente_ID_CPF/`

⚠️ **IMPORTANTE:** Pacientes devem estar importados no sistema antes dos anexos!
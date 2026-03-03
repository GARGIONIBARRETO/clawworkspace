#!/usr/bin/env python3
"""
Validador de Códigos CBHPM para Cirurgia de Coluna
Baseado no Manual SBC/SBOT/SBN
"""

# Base de dados de códigos CBHPM para cirurgia de coluna
CODIGOS_COLUNA = {
    # PROCEDIMENTOS COBRADOS POR SEGMENTO
    "3.07.15.01-6": {
        "descricao": "Artrodese da coluna com instrumentação por segmento",
        "porte": "12C",
        "cobranca": "por_segmento",
        "categoria": "artrodese"
    },
    "3.07.15.02-4": {
        "descricao": "Artrodese de coluna via anterior ou póstero-lateral",
        "porte": "12C",
        "cobranca": "por_segmento",
        "categoria": "artrodese"
    },
    "3.07.15.11-3": {
        "descricao": "Espondilolistese - tratamento cirúrgico",
        "porte": "10A",
        "cobranca": "por_segmento",
        "categoria": "deformidade"
    },
    "3.07.15.09-1": {
        "descricao": "Descompressão medular e/ou cauda equina",
        "porte": "9C",
        "cobranca": "por_nivel",
        "categoria": "descompressao"
    },
    "3.07.15.36-9": {
        "descricao": "Trat. microcirúrgico do canal vertebral estreito por segmento",
        "porte": "10B",
        "cobranca": "por_segmento",
        "categoria": "descompressao"
    },
    "3.07.15.39-3": {
        "descricao": "Hérnia de disco cervical - tratamento cirúrgico",
        "porte": "12B",
        "cobranca": "por_disco",
        "categoria": "hernia_disco"
    },
    "3.07.15.18-0": {
        "descricao": "Hérnia de disco tóraco-lombar - tratamento cirúrgico",
        "porte": "10A",
        "cobranca": "por_disco",
        "categoria": "hernia_disco"
    },
    "3.07.15.59-8": {
        "descricao": "Artroplastia discal de coluna vertebral",
        "porte": "12C",
        "cobranca": "por_segmento",
        "categoria": "artroplastia"
    },
    "3.14.03.33-6": {
        "descricao": "Rizotomia percutâneo por segmento - qualquer método",
        "porte": "10C",
        "cobranca": "por_segmento",
        "categoria": "dor"
    },
    "3.14.03.03-4": {
        "descricao": "Denervação percutânea de faceta articular - por segmento",
        "porte": "9C",
        "cobranca": "por_segmento",
        "categoria": "dor"
    },
    
    # PROCEDIMENTOS COBRADOS POR VÉRTEBRA
    "3.07.15.03-2": {
        "descricao": "Biópsia da coluna",
        "porte": "7C",
        "cobranca": "por_vertebra",
        "categoria": "diagnostico"
    },
    "3.07.15.19-9": {
        "descricao": "Laminectomia ou laminotomia",
        "porte": "9C",
        "cobranca": "por_vertebra",
        "categoria": "descompressao"
    },
    "3.07.15.22-9": {
        "descricao": "Osteotomia de coluna vertebral - tratamento cirúrgico",
        "porte": "8C",
        "cobranca": "por_vertebra",
        "categoria": "deformidade"
    },
    "3.07.15.28-8": {
        "descricao": "Substituição de corpo vertebral",
        "porte": "10B",
        "cobranca": "por_vertebra",
        "categoria": "tumor"
    },
    "3.07.15.38-5": {
        "descricao": "Tumor ósseo vertebral - tratamento cirúrgico",
        "porte": "13C",
        "cobranca": "por_vertebra",
        "categoria": "tumor"
    },
    "3.07.15.17-2": {
        "descricao": "Hemivertebra - ressecção via anterior ou posterior",
        "porte": "11C",
        "cobranca": "por_vertebra",
        "categoria": "malformacao"
    },
    "4.08.14.09-2": {
        "descricao": "Osteoplastia ou discectomia percutânea (vertebroplastia)",
        "porte": "8C",
        "cobranca": "por_vertebra",
        "categoria": "percutaneo"
    },
    
    # PROCEDIMENTOS COBRADOS POR ESTRUTURA
    "4.08.13.36-3": {
        "descricao": "Coluna vertebral: infiltração foraminal ou facetária ou articular",
        "porte": "5A",
        "cobranca": "por_estrutura",
        "categoria": "infiltracao"
    },
    "3.06.01.02-9": {
        "descricao": "Costectomia",
        "porte": "8B",
        "cobranca": "por_costela",
        "categoria": "acesso"
    },
    "2.01.03.30-1": {
        "descricao": "Infiltração de ponto-gatilho (por região muscular)",
        "porte": "3A",
        "cobranca": "por_musculo",
        "categoria": "infiltracao"
    },
    
    # PROCEDIMENTOS COBRADOS UMA VEZ
    "3.07.15.05-9": {
        "descricao": "Cirurgia de coluna por via endoscópica",
        "porte": "11A",
        "cobranca": "uma_vez",
        "categoria": "endoscopia"
    },
    "3.07.15.12-1": {
        "descricao": "Fratura de coluna - tratamento conservador",
        "porte": "2C",
        "cobranca": "uma_vez",
        "categoria": "trauma"
    },
    "3.07.15.16-4": {
        "descricao": "Fraturas ou fratura-luxação de coluna - tratamento cirúrgico",
        "porte": "12B",
        "cobranca": "uma_vez",
        "categoria": "trauma"
    },
    "3.07.15.21-0": {
        "descricao": "Osteomielite de coluna - tratamento cirúrgico",
        "porte": "8B",
        "cobranca": "uma_vez",
        "categoria": "infeccao"
    },
    "3.07.15.24-5": {
        "descricao": "Pseudartrose de coluna - tratamento cirúrgico",
        "porte": "9C",
        "cobranca": "uma_vez",
        "categoria": "complicacao"
    },
    "3.07.15.26-1": {
        "descricao": "Retirada de corpo estranho - tratamento cirúrgico",
        "porte": "8B",
        "cobranca": "uma_vez",
        "categoria": "retirada"
    },
    "3.07.15.27-0": {
        "descricao": "Retirada de material de síntese - tratamento cirúrgico",
        "porte": "8A",
        "cobranca": "uma_vez",
        "categoria": "retirada"
    },
    "3.07.15.31-8": {
        "descricao": "Tratamento cirúrgico da lesão traumática raquimedular",
        "porte": "14B",
        "cobranca": "uma_vez",
        "categoria": "trauma"
    },
    "3.07.32.02-6": {
        "descricao": "Enxerto ósseo",
        "porte": "9B",
        "cobranca": "uma_vez",
        "categoria": "complementar"
    },
    "3.07.15.10-5": {
        "descricao": "Dorso curvo/escoliose/giba costal - tratamento cirúrgico",
        "porte": "14B",
        "cobranca": "uma_vez",
        "categoria": "deformidade"
    },
    "3.16.02.16-9": {
        "descricao": "Bloqueio peridural ou subaracnóideo com corticoide",
        "porte": "3C",
        "cobranca": "uma_vez",
        "categoria": "bloqueio"
    },
    "3.14.01.10-4": {
        "descricao": "Implante de eletrodo para neuroestimulação",
        "porte": "13C",
        "cobranca": "uma_vez",
        "categoria": "neuroestimulacao"
    },
    "3.14.03.14-0": {
        "descricao": "Implante de gerador para neuroestimulação",
        "porte": "10C",
        "cobranca": "uma_vez",
        "categoria": "neuroestimulacao"
    },
    "3.14.01.26-0": {
        "descricao": "Tratamento cirúrgico da fístula liquórica",
        "porte": "10C",
        "cobranca": "uma_vez",
        "categoria": "complicacao"
    },
    "4.08.11.02-6": {
        "descricao": "Radioscopia para acompanhamento de procedimento cirúrgico",
        "porte": "2B",
        "cobranca": "por_hora",
        "categoria": "imagem"
    },
    "2.02.02.09-1": {
        "descricao": "Monitorização neurofisiológica intra-operatória",
        "porte": "11B",
        "cobranca": "uma_vez",
        "categoria": "monitorizacao"
    },
    "3.09.10.13-7": {
        "descricao": "Lesões vasculares intra-abdominais",
        "porte": "12A",
        "cobranca": "uma_vez",
        "categoria": "complicacao"
    },
    "3.06.01.19-3": {
        "descricao": "Toracotomia para procedimentos ortopédicos sobre a coluna",
        "porte": "9C",
        "cobranca": "uma_vez",
        "categoria": "acesso"
    }
}

# Códigos que geralmente devem estar presentes
CODIGOS_COMPLEMENTARES_COMUNS = {
    "radioscopia": "4.08.11.02-6",
    "enxerto": "3.07.32.02-6",
    "monitorizacao": "2.02.02.09-1"
}

# Incompatibilidades entre códigos
INCOMPATIBILIDADES = [
    # Via endoscópica exclui alguns acessos abertos
    ("3.07.15.05-9", ["3.06.01.19-3", "3.06.01.02-9"]),
]

# Códigos que sugerem outros códigos
SUGESTOES_COMPLEMENTARES = {
    # Artrodese geralmente precisa de enxerto
    "3.07.15.01-6": ["3.07.32.02-6"],
    "3.07.15.02-4": ["3.07.32.02-6"],
    
    # Hérnia de disco pode precisar de descompressão
    "3.07.15.18-0": ["3.07.15.09-1", "3.07.15.36-9"],
    "3.07.15.39-3": ["3.07.15.09-1"],
    
    # Estenose geralmente precisa de laminectomia
    "3.07.15.36-9": ["3.07.15.19-9"],
}

class ValidadorCodigosColuna:
    def __init__(self):
        self.codigos_db = CODIGOS_COLUNA
        
    def validar_pedido(self, pedido_cirurgia):
        """
        Valida um pedido de cirurgia
        
        Args:
            pedido_cirurgia: dict com formato:
                {
                    "procedimentos": [
                        {"codigo": "3.07.15.01-6", "quantidade": 2, "descricao": "..."},
                        ...
                    ],
                    "via_acesso": "posterior",  # anterior, lateral, endoscopica
                    "niveis": "L4-S1",
                    "tempo_estimado_horas": 3
                }
        
        Returns:
            dict com erros, avisos e sugestões
        """
        resultado = {
            "valido": True,
            "erros": [],
            "avisos": [],
            "sugestoes": []
        }
        
        codigos_presentes = [p["codigo"] for p in pedido_cirurgia["procedimentos"]]
        
        # Validar cada procedimento
        for proc in pedido_cirurgia["procedimentos"]:
            self._validar_procedimento(proc, resultado)
        
        # Verificar radioscopia
        if "4.08.11.02-6" not in codigos_presentes:
            resultado["avisos"].append("⚠️ Radioscopia não incluída - confirmar se não é necessária")
        
        # Verificar incompatibilidades
        self._verificar_incompatibilidades(codigos_presentes, resultado)
        
        # Sugerir códigos complementares
        self._sugerir_complementares(codigos_presentes, resultado)
        
        # Validar cirurgia 360 graus
        if self._eh_cirurgia_360(codigos_presentes):
            resultado["avisos"].append("📐 Cirurgia 360° detectada - aplicar regra: 1º tempo (100%+50%), 2º tempo (75%)")
        
        if resultado["erros"]:
            resultado["valido"] = False
            
        return resultado
    
    def _validar_procedimento(self, proc, resultado):
        codigo = proc["codigo"]
        quantidade = proc.get("quantidade", 1)
        descricao = proc.get("descricao", "")
        
        # Verificar se código existe
        if codigo not in self.codigos_db:
            resultado["erros"].append(f"❌ Código {codigo} não encontrado na base")
            return
        
        info_codigo = self.codigos_db[codigo]
        
        # Verificar descrição
        if descricao and not self._descricao_compativel(descricao, info_codigo["descricao"]):
            resultado["avisos"].append(
                f"⚠️ Descrição divergente para {codigo}: "
                f"esperado '{info_codigo['descricao']}'"
            )
        
        # Verificar quantidade vs tipo de cobrança
        if info_codigo["cobranca"] == "uma_vez" and quantidade > 1:
            resultado["erros"].append(
                f"❌ Código {codigo} deve ser cobrado apenas uma vez (quantidade: {quantidade})"
            )
        elif info_codigo["cobranca"] in ["por_segmento", "por_vertebra", "por_nivel", "por_disco"]:
            if quantidade < 1:
                resultado["erros"].append(f"❌ Quantidade inválida para {codigo}: {quantidade}")
            elif quantidade > 10:
                resultado["avisos"].append(
                    f"⚠️ Quantidade alta para {codigo}: {quantidade} - confirmar se está correto"
                )
    
    def _descricao_compativel(self, desc_fornecida, desc_esperada):
        # Remove acentos e converte para minúsculas para comparação
        import unicodedata
        
        def normalizar(texto):
            texto = unicodedata.normalize('NFKD', texto.lower())
            return ''.join(c for c in texto if not unicodedata.combining(c))
        
        desc_fornecida = normalizar(desc_fornecida)
        desc_esperada = normalizar(desc_esperada)
        
        # Verifica se as palavras principais estão presentes
        palavras_principais = desc_esperada.split()[:3]
        return all(palavra in desc_fornecida for palavra in palavras_principais)
    
    def _verificar_incompatibilidades(self, codigos_presentes, resultado):
        for codigo_principal, codigos_incompativeis in INCOMPATIBILIDADES:
            if codigo_principal in codigos_presentes:
                for incompativel in codigos_incompativeis:
                    if incompativel in codigos_presentes:
                        resultado["erros"].append(
                            f"❌ Incompatibilidade: {codigo_principal} não pode ser usado com {incompativel}"
                        )
    
    def _sugerir_complementares(self, codigos_presentes, resultado):
        codigos_sugeridos = set()
        
        for codigo in codigos_presentes:
            if codigo in SUGESTOES_COMPLEMENTARES:
                for sugestao in SUGESTOES_COMPLEMENTARES[codigo]:
                    if sugestao not in codigos_presentes:
                        codigos_sugeridos.add(sugestao)
        
        for sugestao in codigos_sugeridos:
            info = self.codigos_db.get(sugestao, {})
            resultado["sugestoes"].append(
                f"💡 Considerar adicionar: {sugestao} - {info.get('descricao', '')}"
            )
    
    def _eh_cirurgia_360(self, codigos_presentes):
        # Verifica se tem artrodese anterior E posterior
        tem_anterior = any(c in codigos_presentes for c in ["3.07.15.02-4"])
        tem_posterior = any(c in codigos_presentes for c in ["3.07.15.01-6"])
        return tem_anterior and tem_posterior
    
    def gerar_relatorio(self, resultado_validacao):
        """Gera relatório formatado da validação"""
        relatorio = []
        
        if resultado_validacao["valido"]:
            relatorio.append("✅ PEDIDO VÁLIDO")
        else:
            relatorio.append("❌ PEDIDO COM PROBLEMAS")
        
        if resultado_validacao["erros"]:
            relatorio.append("\n🚨 ERROS ENCONTRADOS:")
            for erro in resultado_validacao["erros"]:
                relatorio.append(f"  {erro}")
        
        if resultado_validacao["avisos"]:
            relatorio.append("\n⚠️  AVISOS:")
            for aviso in resultado_validacao["avisos"]:
                relatorio.append(f"  {aviso}")
        
        if resultado_validacao["sugestoes"]:
            relatorio.append("\n💡 SUGESTÕES:")
            for sugestao in resultado_validacao["sugestoes"]:
                relatorio.append(f"  {sugestao}")
        
        return "\n".join(relatorio)


# Exemplo de uso
if __name__ == "__main__":
    validador = ValidadorCodigosColuna()
    
    # Exemplo de pedido de cirurgia
    pedido_exemplo = {
        "procedimentos": [
            {"codigo": "3.07.15.01-6", "quantidade": 2, "descricao": "Artrodese com instrumentação"},
            {"codigo": "3.07.15.18-0", "quantidade": 2, "descricao": "Hérnia de disco lombar"},
            {"codigo": "3.07.15.09-1", "quantidade": 2, "descricao": "Descompressão"},
            {"codigo": "3.07.15.19-9", "quantidade": 2, "descricao": "Laminectomia"},
        ],
        "via_acesso": "posterior",
        "niveis": "L4-S1",
        "tempo_estimado_horas": 3
    }
    
    resultado = validador.validar_pedido(pedido_exemplo)
    print(validador.gerar_relatorio(resultado))
#!/usr/bin/env python3
"""
Gerador Automático de Pedidos de Cirurgia de Coluna
Integração com sistema de prontuário eletrônico
"""

from validador_codigos_coluna import ValidadorCodigosColuna, CODIGOS_COLUNA
from datetime import datetime
import json

class GeradorPedidoCirurgia:
    def __init__(self):
        self.validador = ValidadorCodigosColuna()
        self.templates = self._carregar_templates()
        
    def _carregar_templates(self):
        """Templates de cirurgias comuns"""
        return {
            "hernia_lombar_simples": {
                "nome": "Hérnia de Disco Lombar Simples",
                "codigos_base": [
                    {"codigo": "3.07.15.18-0", "multiplicador": "por_disco"},
                    {"codigo": "3.07.15.09-1", "multiplicador": "por_nivel"},
                    {"codigo": "4.08.11.02-6", "quantidade_fixa": 1}
                ],
                "codigos_opcionais": [
                    {"codigo": "3.07.15.36-9", "condicao": "estenose_associada"},
                    {"codigo": "3.07.15.19-9", "condicao": "laminectomia_necessaria"},
                    {"codigo": "2.02.02.09-1", "condicao": "deficit_neurologico"}
                ]
            },
            "artrodese_lombar": {
                "nome": "Artrodese Lombar Posterior",
                "codigos_base": [
                    {"codigo": "3.07.15.01-6", "multiplicador": "por_segmento"},
                    {"codigo": "3.07.15.09-1", "multiplicador": "por_nivel"},
                    {"codigo": "3.07.32.02-6", "quantidade_fixa": 1},
                    {"codigo": "4.08.11.02-6", "quantidade_fixa": 1}
                ],
                "codigos_opcionais": [
                    {"codigo": "3.07.15.18-0", "condicao": "hernia_associada"},
                    {"codigo": "3.07.15.19-9", "condicao": "laminectomia_necessaria"},
                    {"codigo": "2.02.02.09-1", "condicao": "monitorizacao_indicada"}
                ]
            },
            "artrodese_360": {
                "nome": "Artrodese 360° (Anterior + Posterior)",
                "codigos_base": [
                    {"codigo": "3.07.15.01-6", "multiplicador": "por_segmento"},
                    {"codigo": "3.07.15.02-4", "multiplicador": "por_segmento"},
                    {"codigo": "3.07.32.02-6", "quantidade_fixa": 1},
                    {"codigo": "4.08.11.02-6", "quantidade_fixa": 2}  # 2 tempos
                ],
                "nota_especial": "Aplicar regra 360°: 1º tempo (100%+50%), 2º tempo (75%)"
            },
            "estenose_canal": {
                "nome": "Estenose de Canal",
                "codigos_base": [
                    {"codigo": "3.07.15.36-9", "multiplicador": "por_segmento"},
                    {"codigo": "3.07.15.09-1", "multiplicador": "por_nivel"},
                    {"codigo": "3.07.15.19-9", "multiplicador": "por_vertebra"},
                    {"codigo": "4.08.11.02-6", "quantidade_fixa": 1}
                ]
            },
            "hernia_cervical": {
                "nome": "Hérnia Cervical Anterior",
                "codigos_base": [
                    {"codigo": "3.07.15.39-3", "multiplicador": "por_disco"},
                    {"codigo": "3.07.15.01-6", "multiplicador": "por_segmento"},
                    {"codigo": "4.08.11.02-6", "quantidade_fixa": 1}
                ],
                "codigos_opcionais": [
                    {"codigo": "2.02.02.09-1", "condicao": "mielopatia"}
                ]
            }
        }
    
    def gerar_pedido(self, template_nome, parametros):
        """
        Gera pedido de cirurgia baseado em template
        
        Args:
            template_nome: nome do template
            parametros: dict com:
                - niveis: str (ex: "L4-L5-S1")
                - condicoes: list de condições presentes
                - observacoes: str
                
        Returns:
            dict com pedido formatado
        """
        if template_nome not in self.templates:
            raise ValueError(f"Template '{template_nome}' não encontrado")
        
        template = self.templates[template_nome]
        niveis = self._processar_niveis(parametros.get("niveis", ""))
        condicoes = parametros.get("condicoes", [])
        
        procedimentos = []
        
        # Adicionar códigos base
        for codigo_info in template["codigos_base"]:
            quantidade = self._calcular_quantidade(codigo_info, niveis)
            procedimentos.append({
                "codigo": codigo_info["codigo"],
                "quantidade": quantidade,
                "descricao": CODIGOS_COLUNA[codigo_info["codigo"]]["descricao"]
            })
        
        # Adicionar códigos opcionais baseado em condições
        if "codigos_opcionais" in template:
            for codigo_info in template["codigos_opcionais"]:
                if codigo_info["condicao"] in condicoes:
                    quantidade = self._calcular_quantidade(codigo_info, niveis)
                    procedimentos.append({
                        "codigo": codigo_info["codigo"],
                        "quantidade": quantidade,
                        "descricao": CODIGOS_COLUNA[codigo_info["codigo"]]["descricao"]
                    })
        
        pedido = {
            "data": datetime.now().isoformat(),
            "template_usado": template_nome,
            "nome_procedimento": template["nome"],
            "niveis": parametros.get("niveis", ""),
            "procedimentos": procedimentos,
            "observacoes": parametros.get("observacoes", ""),
            "tempo_estimado_horas": self._estimar_tempo(procedimentos)
        }
        
        if "nota_especial" in template:
            pedido["nota_especial"] = template["nota_especial"]
        
        # Validar pedido
        resultado_validacao = self.validador.validar_pedido(pedido)
        pedido["validacao"] = resultado_validacao
        
        return pedido
    
    def _processar_niveis(self, niveis_str):
        """Processa string de níveis em estrutura de dados"""
        if not niveis_str:
            return {"segmentos": 1, "vertebras": 2, "discos": 1}
        
        # Exemplo: "L4-L5-S1" = 2 segmentos, 3 vértebras, 2 discos
        vertebras = niveis_str.split("-")
        num_vertebras = len(vertebras)
        num_segmentos = num_vertebras - 1 if num_vertebras > 1 else 1
        num_discos = num_segmentos
        
        return {
            "segmentos": num_segmentos,
            "vertebras": num_vertebras,
            "discos": num_discos,
            "niveis": num_segmentos  # sinônimo
        }
    
    def _calcular_quantidade(self, codigo_info, niveis):
        """Calcula quantidade baseado no tipo de multiplicador"""
        if "quantidade_fixa" in codigo_info:
            return codigo_info["quantidade_fixa"]
        
        if "multiplicador" not in codigo_info:
            return 1
        
        multiplicador = codigo_info["multiplicador"]
        
        if multiplicador == "por_segmento":
            return niveis["segmentos"]
        elif multiplicador == "por_vertebra":
            return niveis["vertebras"]
        elif multiplicador == "por_disco":
            return niveis["discos"]
        elif multiplicador == "por_nivel":
            return niveis["niveis"]
        else:
            return 1
    
    def _estimar_tempo(self, procedimentos):
        """Estima tempo cirúrgico baseado nos procedimentos"""
        # Simplificado: baseado no maior porte
        portes_tempo = {
            "2C": 0.5, "3A": 0.5, "3C": 0.5,
            "5A": 1, "7C": 1.5, "8A": 2, "8B": 2, "8C": 2,
            "9B": 2.5, "9C": 2.5, "10A": 3, "10B": 3, "10C": 3,
            "11A": 3.5, "11B": 3.5, "11C": 3.5,
            "12A": 4, "12B": 4, "12C": 4,
            "13C": 4.5, "14B": 5
        }
        
        tempo_max = 1  # mínimo 1 hora
        for proc in procedimentos:
            codigo = proc["codigo"]
            if codigo in CODIGOS_COLUNA:
                porte = CODIGOS_COLUNA[codigo]["porte"]
                tempo = portes_tempo.get(porte, 2)
                tempo_max = max(tempo_max, tempo)
        
        return tempo_max
    
    def formatar_pedido_texto(self, pedido):
        """Formata pedido em texto para impressão/visualização"""
        linhas = []
        linhas.append(f"PEDIDO DE CIRURGIA - {pedido['nome_procedimento']}")
        linhas.append(f"Data: {pedido['data'][:10]}")
        linhas.append(f"Níveis: {pedido['niveis']}")
        linhas.append(f"Tempo estimado: {pedido['tempo_estimado_horas']}h")
        linhas.append("\nPROCEDIMENTOS:")
        
        total = 0
        for proc in pedido["procedimentos"]:
            qtd = proc["quantidade"]
            codigo = proc["codigo"]
            desc = proc["descricao"]
            porte = CODIGOS_COLUNA[codigo]["porte"]
            
            if qtd > 1:
                linhas.append(f"{codigo} x{qtd} - {desc} ({porte})")
            else:
                linhas.append(f"{codigo} - {desc} ({porte})")
        
        if "nota_especial" in pedido:
            linhas.append(f"\nNOTA: {pedido['nota_especial']}")
        
        if pedido.get("observacoes"):
            linhas.append(f"\nOBSERVAÇÕES: {pedido['observacoes']}")
        
        # Adicionar resultado da validação
        validacao = pedido.get("validacao", {})
        if validacao:
            linhas.append("\n" + self.validador.gerar_relatorio(validacao))
        
        return "\n".join(linhas)
    
    def exportar_para_json(self, pedido, arquivo):
        """Exporta pedido para arquivo JSON"""
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(pedido, f, ensure_ascii=False, indent=2)
    
    def buscar_codigo(self, termo):
        """Busca código por termo na descrição"""
        resultados = []
        termo_lower = termo.lower()
        
        for codigo, info in CODIGOS_COLUNA.items():
            if termo_lower in info["descricao"].lower():
                resultados.append({
                    "codigo": codigo,
                    "descricao": info["descricao"],
                    "porte": info["porte"],
                    "cobranca": info["cobranca"]
                })
        
        return resultados


# Exemplo de uso
if __name__ == "__main__":
    gerador = GeradorPedidoCirurgia()
    
    # Exemplo 1: Hérnia lombar L4-L5 e L5-S1 com estenose
    pedido1 = gerador.gerar_pedido("hernia_lombar_simples", {
        "niveis": "L4-L5-S1",
        "condicoes": ["estenose_associada", "laminectomia_necessaria"],
        "observacoes": "Paciente com déficit motor leve"
    })
    
    print("=== PEDIDO 1 ===")
    print(gerador.formatar_pedido_texto(pedido1))
    
    # Exemplo 2: Artrodese L4-S1
    pedido2 = gerador.gerar_pedido("artrodese_lombar", {
        "niveis": "L4-L5-S1",
        "condicoes": ["hernia_associada", "monitorizacao_indicada"],
        "observacoes": "Espondilolistese grau II"
    })
    
    print("\n\n=== PEDIDO 2 ===")
    print(gerador.formatar_pedido_texto(pedido2))
    
    # Buscar códigos
    print("\n\n=== BUSCA: 'infiltração' ===")
    resultados = gerador.buscar_codigo("infiltração")
    for r in resultados:
        print(f"{r['codigo']} - {r['descricao']} ({r['porte']}) - Cobrança: {r['cobranca']}")
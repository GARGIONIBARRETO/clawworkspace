#!/usr/bin/env python3
"""
Exemplo prático do Sistema de Validação de Cirurgia de Coluna
Demonstra uso completo do validador e gerador
"""

from gerador_pedido_cirurgia import GeradorPedidoCirurgia
from validador_codigos_coluna import ValidadorCodigosColuna

def exemplo_1_hernia_simples():
    """Exemplo: Hérnia de disco lombar simples"""
    print("="*60)
    print("EXEMPLO 1: Hérnia de Disco Lombar L4-L5")
    print("="*60)
    
    gerador = GeradorPedidoCirurgia()
    
    # Gerar pedido
    pedido = gerador.gerar_pedido("hernia_lombar_simples", {
        "niveis": "L4-L5",
        "condicoes": [],  # Sem condições especiais
        "observacoes": "Hérnia posterolateral direita"
    })
    
    # Mostrar pedido formatado
    print(gerador.formatar_pedido_texto(pedido))
    print("\n")

def exemplo_2_hernia_complexa():
    """Exemplo: Hérnia com estenose e necessidade de laminectomia"""
    print("="*60)
    print("EXEMPLO 2: Hérnia L4-L5-S1 com Estenose")
    print("="*60)
    
    gerador = GeradorPedidoCirurgia()
    
    pedido = gerador.gerar_pedido("hernia_lombar_simples", {
        "niveis": "L4-L5-S1",  # 2 segmentos
        "condicoes": ["estenose_associada", "laminectomia_necessaria"],
        "observacoes": "Estenose severa + déficit motor grau 4/5"
    })
    
    print(gerador.formatar_pedido_texto(pedido))
    print("\n")

def exemplo_3_artrodese():
    """Exemplo: Artrodese lombar"""
    print("="*60)
    print("EXEMPLO 3: Artrodese L4-S1")
    print("="*60)
    
    gerador = GeradorPedidoCirurgia()
    
    pedido = gerador.gerar_pedido("artrodese_lombar", {
        "niveis": "L4-L5-S1",
        "condicoes": ["hernia_associada", "monitorizacao_indicada"],
        "observacoes": "Espondilolistese L5-S1 grau II + instabilidade"
    })
    
    print(gerador.formatar_pedido_texto(pedido))
    print("\n")

def exemplo_4_validacao_manual():
    """Exemplo: Validação de pedido criado manualmente"""
    print("="*60)
    print("EXEMPLO 4: Validação Manual - Pedido com Erro")
    print("="*60)
    
    validador = ValidadorCodigosColuna()
    
    # Criar pedido com erros propositais
    pedido_com_erros = {
        "procedimentos": [
            # Via endoscópica (cobra 1x) mas com quantidade 2 - ERRO!
            {"codigo": "3.07.15.05-9", "quantidade": 2, "descricao": "Via endoscópica"},
            # Hérnia lombar - OK
            {"codigo": "3.07.15.18-0", "quantidade": 1, "descricao": "Hérnia lombar"},
            # Código inexistente - ERRO!
            {"codigo": "3.07.15.99-9", "quantidade": 1, "descricao": "Procedimento inventado"},
            # Faltou radioscopia - AVISO!
        ],
        "niveis": "L5-S1"
    }
    
    resultado = validador.validar_pedido(pedido_com_erros)
    print(validador.gerar_relatorio(resultado))
    print("\n")

def exemplo_5_cirurgia_360():
    """Exemplo: Artrodese 360 graus"""
    print("="*60)
    print("EXEMPLO 5: Artrodese 360° (Anterior + Posterior)")
    print("="*60)
    
    gerador = GeradorPedidoCirurgia()
    
    pedido = gerador.gerar_pedido("artrodese_360", {
        "niveis": "L4-L5",
        "observacoes": "Discopatia degenerativa severa com colapso do espaço"
    })
    
    print(gerador.formatar_pedido_texto(pedido))
    print("\n")

def exemplo_6_busca_codigos():
    """Exemplo: Buscar códigos por termo"""
    print("="*60)
    print("EXEMPLO 6: Busca de Códigos")
    print("="*60)
    
    gerador = GeradorPedidoCirurgia()
    
    # Buscar infiltrações
    print("Buscando por 'infiltração':")
    resultados = gerador.buscar_codigo("infiltração")
    for r in resultados[:5]:
        print(f"  {r['codigo']} - {r['descricao']} (Porte: {r['porte']}) - Cobrança: {r['cobranca']}")
    
    print("\nBuscando por 'artrodese':")
    resultados = gerador.buscar_codigo("artrodese")
    for r in resultados[:5]:
        print(f"  {r['codigo']} - {r['descricao']} (Porte: {r['porte']}) - Cobrança: {r['cobranca']}")
    print("\n")

def exemplo_7_comparacao_pedidos():
    """Exemplo: Comparação de custos entre abordagens"""
    print("="*60)
    print("EXEMPLO 7: Comparação de Abordagens")
    print("="*60)
    
    gerador = GeradorPedidoCirurgia()
    
    print("Opção 1: Discectomia Simples")
    pedido1 = gerador.gerar_pedido("hernia_lombar_simples", {
        "niveis": "L4-L5",
        "condicoes": []
    })
    print(f"Tempo estimado: {pedido1['tempo_estimado_horas']}h")
    print(f"Procedimentos: {len(pedido1['procedimentos'])}")
    
    print("\nOpção 2: Artrodese")
    pedido2 = gerador.gerar_pedido("artrodese_lombar", {
        "niveis": "L4-L5",
        "condicoes": []
    })
    print(f"Tempo estimado: {pedido2['tempo_estimado_horas']}h")
    print(f"Procedimentos: {len(pedido2['procedimentos'])}")
    
    # Mostrar diferença de complexidade
    print("\nDiferença de códigos:")
    codigos1 = {p['codigo'] for p in pedido1['procedimentos']}
    codigos2 = {p['codigo'] for p in pedido2['procedimentos']}
    extras = codigos2 - codigos1
    
    for codigo in extras:
        info = ValidadorCodigosColuna().codigos_db[codigo]
        print(f"  + {codigo} - {info['descricao']} (Porte: {info['porte']})")
    print("\n")

# Menu principal
if __name__ == "__main__":
    print("\n🏥 SISTEMA DE VALIDAÇÃO DE CIRURGIA DE COLUNA")
    print("Demonstração de Funcionalidades\n")
    
    while True:
        print("\nEscolha um exemplo:")
        print("1. Hérnia de disco simples")
        print("2. Hérnia com estenose")
        print("3. Artrodese lombar")
        print("4. Validação com erros")
        print("5. Artrodese 360°")
        print("6. Buscar códigos")
        print("7. Comparar abordagens")
        print("8. Executar todos")
        print("0. Sair")
        
        escolha = input("\nOpção: ")
        
        if escolha == "1":
            exemplo_1_hernia_simples()
        elif escolha == "2":
            exemplo_2_hernia_complexa()
        elif escolha == "3":
            exemplo_3_artrodese()
        elif escolha == "4":
            exemplo_4_validacao_manual()
        elif escolha == "5":
            exemplo_5_cirurgia_360()
        elif escolha == "6":
            exemplo_6_busca_codigos()
        elif escolha == "7":
            exemplo_7_comparacao_pedidos()
        elif escolha == "8":
            exemplo_1_hernia_simples()
            exemplo_2_hernia_complexa()
            exemplo_3_artrodese()
            exemplo_4_validacao_manual()
            exemplo_5_cirurgia_360()
            exemplo_6_busca_codigos()
            exemplo_7_comparacao_pedidos()
        elif escolha == "0":
            print("\nEncerrando sistema...")
            break
        else:
            print("\nOpção inválida!")
        
        input("\nPressione ENTER para continuar...")
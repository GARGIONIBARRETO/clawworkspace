#!/usr/bin/env python3
"""
Script para corrigir os botões que não foram adicionados
"""

import os

def corrigir_template_detalhes():
    """Adiciona os botões que faltam no template de detalhes"""
    
    arquivo = '/root/clawd/templates/paciente_detalhes.html'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Encontrar onde adicionar os botões (após o título "Consultas")
    # Procurar pela linha do tab de consultas
    if '<i class="fas fa-stethoscope"></i> Consultas' in conteudo:
        # Adicionar botões na seção de consultas
        # Encontrar o card de consultas
        pos_card = conteudo.find('<div class="tab-pane fade show active" id="consultas"')
        if pos_card > 0:
            # Encontrar onde começa o card-body dentro da tab de consultas
            pos_body = conteudo.find('<div class="card-body">', pos_card)
            if pos_body > 0:
                # Inserir os botões logo após o card-body
                botoes = '''
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3>Histórico de Consultas</h3>
                            <div>
                                <a href="/paciente/{{ paciente[0] }}/novo_episodio" class="btn btn-success btn-sm">
                                    <i class="fas fa-file-medical"></i> Novo Episódio Clínico
                                </a>
                                <a href="/paciente/{{ paciente[0] }}/gravar" class="btn btn-warning btn-sm">
                                    <i class="fas fa-microphone"></i> Gravar Consulta
                                </a>
                            </div>
                        </div>'''
                
                # Inserir após o card-body
                pos_insert = pos_body + len('<div class="card-body">')
                conteudo = conteudo[:pos_insert] + botoes + conteudo[pos_insert:]
                
                with open(arquivo, 'w') as f:
                    f.write(conteudo)
                
                print("✅ Botões adicionados ao template paciente_detalhes.html")
                return True
    
    print("❌ Não foi possível adicionar os botões")
    return False

def corrigir_botao_editar():
    """Adiciona botão de editar que também está faltando"""
    
    arquivo = '/root/clawd/templates/paciente_detalhes.html'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Verificar se já tem botão editar
    if 'editar' not in conteudo.lower():
        # Adicionar botão editar ao lado do título
        if '<h1><i class="fas fa-user"></i> {{ paciente[1] }}</h1>' in conteudo:
            conteudo = conteudo.replace(
                '<h1><i class="fas fa-user"></i> {{ paciente[1] }}</h1>',
                '''<h1><i class="fas fa-user"></i> {{ paciente[1] }}</h1>
            </div>
            <div>
                <a href="/paciente/{{ paciente[0] }}/editar" class="btn btn-warning btn-sm">
                    <i class="fas fa-edit"></i> Editar
                </a>'''
            )
            
            with open(arquivo, 'w') as f:
                f.write(conteudo)
            
            print("✅ Botão editar adicionado")

def verificar_rotas():
    """Verifica se as rotas existem no web_interface.py"""
    
    arquivo = '/root/clawd/scripts/web_interface.py'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    rotas_necessarias = [
        ('novo_episodio', '@app.route(\'/paciente/<int:paciente_id>/novo_episodio\')'),
        ('gravar_consulta', '@app.route(\'/paciente/<int:paciente_id>/gravar\')'),
        ('editar_paciente', '@app.route(\'/paciente/<int:paciente_id>/editar\')')
    ]
    
    print("\n📋 Verificando rotas:")
    todas_ok = True
    
    for nome, rota in rotas_necessarias:
        if rota in conteudo:
            print(f"✅ Rota {nome} encontrada")
        else:
            print(f"❌ Rota {nome} NÃO encontrada")
            todas_ok = False
    
    return todas_ok

def main():
    print("🔧 CORRIGINDO BOTÕES NA INTERFACE")
    print("=" * 50)
    
    # Corrigir template
    corrigir_template_detalhes()
    corrigir_botao_editar()
    
    # Verificar rotas
    if verificar_rotas():
        print("\n✅ Todas as rotas estão configuradas!")
        print("\n⚠️  Reinicie o servidor web para aplicar as mudanças:")
        print("   pkill -f web_interface.py")
        print("   cd /root/clawd/scripts && nohup python3 web_interface.py > /tmp/web_interface.log 2>&1 &")
    else:
        print("\n❌ Algumas rotas estão faltando!")
        print("   Execute os scripts de implementação novamente")

if __name__ == "__main__":
    main()
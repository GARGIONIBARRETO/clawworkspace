#!/usr/bin/env python3
"""
Script para adicionar funcionalidades de busca e nova consulta na interface web
"""

import os
import shutil
from datetime import datetime

def backup_arquivo(arquivo):
    """Faz backup do arquivo antes de modificar"""
    if os.path.exists(arquivo):
        backup_name = f"{arquivo}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(arquivo, backup_name)
        print(f"📁 Backup criado: {backup_name}")

def adicionar_rotas_web_interface():
    """Adiciona rotas de busca e nova consulta no web_interface.py"""
    arquivo = '/root/clawd/scripts/web_interface.py'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Adicionar rota de busca após a rota /pacientes
    busca_route = '''
@app.route('/buscar')
def buscar():
    """Busca pacientes"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('pacientes'))
    
    try:
        db = clinica_app.get_db()
        db.cursor.execute("""
        SELECT id, nome, cpf, telefone, convenio 
        FROM pacientes 
        WHERE LOWER(nome) LIKE LOWER(%s) 
        OR cpf LIKE %s
        OR telefone LIKE %s
        ORDER BY nome
        LIMIT 50
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        pacientes = db.cursor.fetchall()
        
        return render_template('pacientes.html', 
                             pacientes=pacientes,
                             busca=query,
                             total_encontrados=len(pacientes))
    except Exception as e:
        flash(f'Erro na busca: {str(e)}')
        return redirect(url_for('pacientes'))

@app.route('/paciente/<int:paciente_id>/nova_consulta')
def nova_consulta(paciente_id):
    """Formulário para nova consulta"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("""
        SELECT id, nome, cpf FROM pacientes WHERE id = %s
        """, (paciente_id,))
        paciente = db.cursor.fetchone()
        
        if not paciente:
            flash('Paciente não encontrado!')
            return redirect(url_for('pacientes'))
        
        return render_template('nova_consulta.html', paciente=paciente)
    except Exception as e:
        flash(f'Erro: {str(e)}')
        return redirect(url_for('pacientes'))

@app.route('/paciente/<int:paciente_id>/salvar_consulta', methods=['POST'])
def salvar_consulta(paciente_id):
    """Salva nova consulta"""
    try:
        db = clinica_app.get_db()
        
        # Coletar dados do formulário
        data_consulta = request.form.get('data_consulta')
        motivo = request.form.get('motivo')
        observacoes = request.form.get('observacoes')
        medico = request.form.get('medico', 'Dr. Felipe')
        
        # Inserir consulta
        db.cursor.execute("""
        INSERT INTO consultas (paciente_id, data_consulta, medico, motivo, observacoes)
        VALUES (%s, %s, %s, %s, %s)
        """, (paciente_id, data_consulta, medico, motivo, observacoes))
        
        db.connection.commit()
        
        flash('Consulta adicionada com sucesso!', 'success')
        return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
    except Exception as e:
        db.connection.rollback()
        flash(f'Erro ao salvar consulta: {str(e)}', 'danger')
        return redirect(url_for('nova_consulta', paciente_id=paciente_id))
'''
    
    # Encontrar posição para inserir (após a rota de pacientes)
    pos = conteudo.find('@app.route(\'/paciente/<int:paciente_id>\')')
    if pos > 0:
        # Inserir antes da rota de detalhes
        conteudo = conteudo[:pos] + busca_route + '\n' + conteudo[pos:]
        
        with open(arquivo, 'w') as f:
            f.write(conteudo)
        
        print("✅ Rotas de busca e nova consulta adicionadas")

def criar_template_busca():
    """Atualiza template de pacientes para incluir busca"""
    arquivo = '/root/clawd/templates/pacientes.html'
    backup_arquivo(arquivo)
    
    novo_template = '''{% extends "base.html" %}

{% block title %}Pacientes - Clínica Dr. Felipe{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h1><i class="fas fa-users"></i> Pacientes</h1>
            <a href="/importar" class="btn btn-success">
                <i class="fas fa-plus"></i> Importar Pacientes
            </a>
        </div>
    </div>
</div>

<!-- Barra de Busca -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <form action="/buscar" method="get" class="d-flex">
                    <div class="input-group">
                        <span class="input-group-text"><i class="fas fa-search"></i></span>
                        <input type="text" 
                               name="q" 
                               class="form-control form-control-lg" 
                               placeholder="Buscar por nome, CPF ou telefone..." 
                               value="{{ busca or '' }}"
                               autofocus>
                        <button type="submit" class="btn btn-primary">Buscar</button>
                        {% if busca %}
                        <a href="/pacientes" class="btn btn-secondary">Limpar</a>
                        {% endif %}
                    </div>
                </form>
                
                {% if busca %}
                <div class="mt-2">
                    <span class="text-muted">
                        <i class="fas fa-info-circle"></i> 
                        {{ total_encontrados or 0 }} resultado(s) para "{{ busca }}"
                    </span>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                {% if pacientes %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Nome</th>
                                <th>CPF</th>
                                <th>Telefone</th>
                                <th>Convênio</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for paciente in pacientes %}
                            <tr>
                                <td>
                                    <strong>{{ paciente[1] }}</strong>
                                </td>
                                <td>
                                    <span class="font-monospace">{{ paciente[2] or '-' }}</span>
                                </td>
                                <td>{{ paciente[3] or '-' }}</td>
                                <td>
                                    <span class="badge bg-secondary">{{ paciente[4] or 'Particular' }}</span>
                                </td>
                                <td>
                                    <a href="/paciente/{{ paciente[0] }}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-eye"></i> Ver Detalhes
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-3">
                    <p class="text-muted">
                        <i class="fas fa-info-circle"></i> 
                        Total: {{ pacientes|length }} paciente(s) cadastrado(s)
                    </p>
                </div>
                
                {% else %}
                <div class="text-center py-5">
                    {% if busca %}
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4>Nenhum resultado encontrado</h4>
                    <p class="text-muted">Tente buscar com outros termos.</p>
                    <a href="/pacientes" class="btn btn-primary">
                        <i class="fas fa-users"></i> Ver Todos
                    </a>
                    {% else %}
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h4>Nenhum paciente cadastrado</h4>
                    <p class="text-muted">Importe seus dados de pacientes para começar.</p>
                    <a href="/importar" class="btn btn-success">
                        <i class="fas fa-upload"></i> Importar Pacientes
                    </a>
                    {% endif %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(arquivo, 'w') as f:
        f.write(novo_template)
    
    print("✅ Template de pacientes atualizado com busca")

def criar_template_nova_consulta():
    """Cria template para nova consulta"""
    template = '''{% extends "base.html" %}

{% block title %}Nova Consulta - {{ paciente[1] }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/pacientes">Pacientes</a></li>
                <li class="breadcrumb-item"><a href="/paciente/{{ paciente[0] }}">{{ paciente[1] }}</a></li>
                <li class="breadcrumb-item active">Nova Consulta</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-file-medical"></i> Nova Consulta</h1>
        <p class="text-muted">Paciente: <strong>{{ paciente[1] }}</strong> {% if paciente[2] %}(CPF: {{ paciente[2] }}){% endif %}</p>
    </div>
</div>

<div class="row mt-3">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <form action="/paciente/{{ paciente[0] }}/salvar_consulta" method="post">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="data_consulta" class="form-label">Data da Consulta *</label>
                                <input type="date" 
                                       class="form-control" 
                                       id="data_consulta" 
                                       name="data_consulta" 
                                       value="{{ today }}"
                                       required>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="medico" class="form-label">Médico</label>
                                <input type="text" 
                                       class="form-control" 
                                       id="medico" 
                                       name="medico" 
                                       value="Dr. Felipe"
                                       readonly>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="tipo" class="form-label">Tipo</label>
                                <select class="form-select" id="tipo" name="tipo">
                                    <option value="Primeira Consulta">Primeira Consulta</option>
                                    <option value="Retorno">Retorno</option>
                                    <option value="Teleconsulta">Teleconsulta</option>
                                    <option value="Emergência">Emergência</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="motivo" class="form-label">Motivo da Consulta / Queixa Principal *</label>
                        <textarea class="form-control" 
                                  id="motivo" 
                                  name="motivo" 
                                  rows="2" 
                                  placeholder="Descreva o motivo principal da consulta..."
                                  required></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="observacoes" class="form-label">Evolução / Observações</label>
                        <textarea class="form-control" 
                                  id="observacoes" 
                                  name="observacoes" 
                                  rows="10" 
                                  placeholder="História da doença atual, exame físico, hipóteses diagnósticas, conduta..."></textarea>
                    </div>
                    
                    <div class="d-flex justify-content-between">
                        <a href="/paciente/{{ paciente[0] }}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Voltar
                        </a>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Salvar Consulta
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
// Define data de hoje como padrão
document.getElementById('data_consulta').valueAsDate = new Date();
</script>
{% endblock %}'''
    
    with open('/root/clawd/templates/nova_consulta.html', 'w') as f:
        f.write(template)
    
    print("✅ Template de nova consulta criado")

def atualizar_template_detalhes():
    """Adiciona botão de nova consulta na página de detalhes"""
    arquivo = '/root/clawd/templates/paciente_detalhes.html'
    
    if os.path.exists(arquivo):
        backup_arquivo(arquivo)
        
        with open(arquivo, 'r') as f:
            conteudo = f.read()
        
        # Adicionar botão após o título de Consultas
        if '<h3>Consultas</h3>' in conteudo:
            conteudo = conteudo.replace(
                '<h3>Consultas</h3>',
                '''<div class="d-flex justify-content-between align-items-center">
                    <h3>Consultas</h3>
                    <a href="/paciente/{{ paciente[0] }}/nova_consulta" class="btn btn-success btn-sm">
                        <i class="fas fa-plus"></i> Nova Consulta
                    </a>
                </div>'''
            )
            
            with open(arquivo, 'w') as f:
                f.write(conteudo)
            
            print("✅ Template de detalhes atualizado com botão de nova consulta")

def main():
    print("🔧 ADICIONANDO FUNCIONALIDADES DE BUSCA E NOVA CONSULTA")
    print("=" * 60)
    
    # Backup do arquivo principal
    backup_arquivo('/root/clawd/scripts/web_interface.py')
    
    # Adicionar rotas
    adicionar_rotas_web_interface()
    
    # Criar/atualizar templates
    criar_template_busca()
    criar_template_nova_consulta()
    atualizar_template_detalhes()
    
    print("\n✅ CONCLUÍDO!")
    print("\n📝 Funcionalidades adicionadas:")
    print("1. Busca por nome, CPF ou telefone")
    print("2. Botão 'Nova Consulta' na página de detalhes do paciente")
    print("3. Formulário completo para adicionar consultas")
    print("\n⚠️  Reinicie o servidor web para aplicar as mudanças:")
    print("   pkill -f web_interface.py")
    print("   cd /root/clawd/scripts && nohup python3 web_interface.py > /tmp/web_interface.log 2>&1 &")

if __name__ == "__main__":
    main()
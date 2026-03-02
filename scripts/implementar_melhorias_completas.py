#!/usr/bin/env python3
"""
Script para implementar todas as melhorias na interface web:
- Adicionar novo paciente
- Editar dados do paciente
- Upload de exames/documentos
- Agenda de consultas
"""

import os
from datetime import datetime

def adicionar_rotas_melhoradas():
    """Adiciona todas as novas rotas ao web_interface.py"""
    
    novas_rotas = '''
@app.route('/paciente/novo')
def novo_paciente():
    """Formulário para novo paciente"""
    return render_template('novo_paciente.html')

@app.route('/paciente/salvar', methods=['POST'])
def salvar_paciente():
    """Salva novo paciente"""
    try:
        db = clinica_app.get_db()
        
        # Coletar dados do formulário
        nome = request.form.get('nome')
        cpf = request.form.get('cpf', '').replace('.', '').replace('-', '')
        data_nascimento = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        convenio = request.form.get('convenio')
        observacoes = request.form.get('observacoes')
        
        # Inserir paciente
        db.cursor.execute("""
        INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, email, endereco, convenio, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (nome, cpf or None, data_nascimento or None, telefone, email, endereco, convenio, observacoes))
        
        paciente_id = db.cursor.fetchone()[0]
        db.connection.commit()
        
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
    except Exception as e:
        db.connection.rollback()
        flash(f'Erro ao salvar paciente: {str(e)}', 'danger')
        return redirect(url_for('novo_paciente'))

@app.route('/paciente/<int:paciente_id>/editar')
def editar_paciente(paciente_id):
    """Formulário para editar paciente"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("""
        SELECT id, nome, cpf, data_nascimento, telefone, email, endereco, convenio, observacoes
        FROM pacientes WHERE id = %s
        """, (paciente_id,))
        paciente = db.cursor.fetchone()
        
        if not paciente:
            flash('Paciente não encontrado!')
            return redirect(url_for('pacientes'))
        
        return render_template('editar_paciente.html', paciente=paciente)
    except Exception as e:
        flash(f'Erro: {str(e)}')
        return redirect(url_for('pacientes'))

@app.route('/paciente/<int:paciente_id>/atualizar', methods=['POST'])
def atualizar_paciente(paciente_id):
    """Atualiza dados do paciente"""
    try:
        db = clinica_app.get_db()
        
        # Coletar dados do formulário
        nome = request.form.get('nome')
        cpf = request.form.get('cpf', '').replace('.', '').replace('-', '')
        data_nascimento = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        convenio = request.form.get('convenio')
        observacoes = request.form.get('observacoes')
        
        # Atualizar paciente
        db.cursor.execute("""
        UPDATE pacientes 
        SET nome = %s, cpf = %s, data_nascimento = %s, telefone = %s, 
            email = %s, endereco = %s, convenio = %s, observacoes = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """, (nome, cpf or None, data_nascimento or None, telefone, email, 
              endereco, convenio, observacoes, paciente_id))
        
        db.connection.commit()
        
        flash('Paciente atualizado com sucesso!', 'success')
        return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
    except Exception as e:
        db.connection.rollback()
        flash(f'Erro ao atualizar paciente: {str(e)}', 'danger')
        return redirect(url_for('editar_paciente', paciente_id=paciente_id))

@app.route('/paciente/<int:paciente_id>/upload_exame', methods=['POST'])
def upload_exame(paciente_id):
    """Upload de exames/documentos"""
    try:
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
        arquivo = request.files['arquivo']
        tipo_exame = request.form.get('tipo_exame', 'Exame')
        data_exame = request.form.get('data_exame')
        descricao = request.form.get('descricao')
        
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
        # Criar pasta para o paciente
        db = clinica_app.get_db()
        db.cursor.execute("SELECT cpf FROM pacientes WHERE id = %s", (paciente_id,))
        cpf = db.cursor.fetchone()[0]
        
        pasta_paciente = f'/root/clawd/anexos_pacientes/paciente_{paciente_id}_{cpf}'
        os.makedirs(pasta_paciente, exist_ok=True)
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(arquivo.filename)[1]
        nome_arquivo = f'{tipo_exame}_{timestamp}{ext}'
        caminho_arquivo = os.path.join(pasta_paciente, nome_arquivo)
        
        arquivo.save(caminho_arquivo)
        
        # Registrar no banco
        db.cursor.execute("""
        INSERT INTO exames_laboratoriais (paciente_id, data_exame, tipo_exame, arquivo_pdf, observacoes)
        VALUES (%s, %s, %s, %s, %s)
        """, (paciente_id, data_exame or datetime.now(), tipo_exame, nome_arquivo, descricao))
        
        db.connection.commit()
        
        flash('Exame/documento enviado com sucesso!', 'success')
        return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
    except Exception as e:
        flash(f'Erro no upload: {str(e)}', 'danger')
        return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))

@app.route('/agenda')
def agenda():
    """Página de agenda de consultas"""
    try:
        db = clinica_app.get_db()
        
        # Buscar consultas futuras
        db.cursor.execute("""
        SELECT c.id, p.nome, c.data_consulta, c.motivo, p.telefone, p.id as paciente_id
        FROM consultas c
        JOIN pacientes p ON c.paciente_id = p.id
        WHERE c.data_consulta >= CURRENT_DATE
        ORDER BY c.data_consulta, p.nome
        """)
        
        consultas_futuras = db.cursor.fetchall()
        
        # Buscar consultas de hoje
        db.cursor.execute("""
        SELECT c.id, p.nome, c.data_consulta, c.motivo, p.telefone, p.id as paciente_id
        FROM consultas c
        JOIN pacientes p ON c.paciente_id = p.id
        WHERE DATE(c.data_consulta) = CURRENT_DATE
        ORDER BY p.nome
        """)
        
        consultas_hoje = db.cursor.fetchall()
        
        return render_template('agenda.html', 
                             consultas_futuras=consultas_futuras,
                             consultas_hoje=consultas_hoje)
    except Exception as e:
        flash(f'Erro ao carregar agenda: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/<int:paciente_id>/<arquivo>')
def download_anexo(paciente_id, arquivo):
    """Download de anexos do paciente"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("SELECT cpf FROM pacientes WHERE id = %s", (paciente_id,))
        cpf = db.cursor.fetchone()[0]
        
        pasta = f'/root/clawd/anexos_pacientes/paciente_{paciente_id}_{cpf}'
        caminho = os.path.join(pasta, arquivo)
        
        if os.path.exists(caminho):
            return send_file(caminho, as_attachment=True)
        else:
            abort(404)
    except Exception as e:
        abort(404)
'''
    
    # Adicionar ao arquivo
    arquivo = '/root/clawd/scripts/web_interface.py'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Encontrar onde inserir (antes do if __name__)
    pos = conteudo.find('if __name__ == "__main__":')
    if pos > 0:
        conteudo = conteudo[:pos] + novas_rotas + '\n\n' + conteudo[pos:]
        
        with open(arquivo, 'w') as f:
            f.write(conteudo)
        
        print("✅ Novas rotas adicionadas ao web_interface.py")

def atualizar_template_base():
    """Adiciona link para agenda no menu"""
    arquivo = '/root/clawd/templates/base.html'
    
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            conteudo = f.read()
        
        # Adicionar link da agenda após Pacientes
        if '<a class="nav-link" href="/pacientes">Pacientes</a>' in conteudo:
            conteudo = conteudo.replace(
                '<a class="nav-link" href="/pacientes">Pacientes</a>',
                '''<a class="nav-link" href="/pacientes">Pacientes</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/agenda">
                                <i class="fas fa-calendar-alt"></i> Agenda
                            </a>'''
            )
        
        with open(arquivo, 'w') as f:
            f.write(conteudo)
        
        print("✅ Menu atualizado com link para Agenda")

def criar_template_novo_paciente():
    """Cria template para adicionar novo paciente"""
    template = '''{% extends "base.html" %}

{% block title %}Novo Paciente - Clínica Dr. Felipe{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/pacientes">Pacientes</a></li>
                <li class="breadcrumb-item active">Novo Paciente</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-user-plus"></i> Cadastrar Novo Paciente</h1>
    </div>
</div>

<div class="row mt-3">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <form action="/paciente/salvar" method="post">
                    <h4 class="mb-3">Dados Pessoais</h4>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="nome" class="form-label">Nome Completo *</label>
                                <input type="text" class="form-control" id="nome" name="nome" required>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="cpf" class="form-label">CPF</label>
                                <input type="text" class="form-control" id="cpf" name="cpf" 
                                       placeholder="000.000.000-00">
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="data_nascimento" class="form-label">Data de Nascimento</label>
                                <input type="date" class="form-control" id="data_nascimento" name="data_nascimento">
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="telefone" class="form-label">Telefone</label>
                                <input type="text" class="form-control" id="telefone" name="telefone"
                                       placeholder="(00) 00000-0000">
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="email" class="form-label">E-mail</label>
                                <input type="email" class="form-control" id="email" name="email">
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="endereco" class="form-label">Endereço</label>
                        <textarea class="form-control" id="endereco" name="endereco" rows="2"></textarea>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="convenio" class="form-label">Convênio</label>
                                <select class="form-select" id="convenio" name="convenio">
                                    <option value="">Particular</option>
                                    <option value="Unimed">Unimed</option>
                                    <option value="Bradesco Saúde">Bradesco Saúde</option>
                                    <option value="SulAmérica">SulAmérica</option>
                                    <option value="Amil">Amil</option>
                                    <option value="Outro">Outro</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="observacoes" class="form-label">Observações</label>
                        <textarea class="form-control" id="observacoes" name="observacoes" rows="3"></textarea>
                    </div>
                    
                    <div class="d-flex justify-content-between">
                        <a href="/pacientes" class="btn btn-secondary">
                            <i class="fas fa-times"></i> Cancelar
                        </a>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Cadastrar Paciente
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
// Máscara para CPF
document.getElementById('cpf').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\\d{3})(\\d{3})(\\d{3})(\\d{2})/, '$1.$2.$3-$4');
        e.target.value = value;
    }
});

// Máscara para telefone
document.getElementById('telefone').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\\d{2})(\\d{5})(\\d{4})/, '($1) $2-$3');
        e.target.value = value;
    }
});
</script>
{% endblock %}'''
    
    with open('/root/clawd/templates/novo_paciente.html', 'w') as f:
        f.write(template)
    print("✅ Template novo_paciente.html criado")

def criar_template_editar_paciente():
    """Cria template para editar paciente"""
    template = '''{% extends "base.html" %}

{% block title %}Editar - {{ paciente[1] }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/pacientes">Pacientes</a></li>
                <li class="breadcrumb-item"><a href="/paciente/{{ paciente[0] }}">{{ paciente[1] }}</a></li>
                <li class="breadcrumb-item active">Editar</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-user-edit"></i> Editar Paciente</h1>
    </div>
</div>

<div class="row mt-3">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <form action="/paciente/{{ paciente[0] }}/atualizar" method="post">
                    <h4 class="mb-3">Dados Pessoais</h4>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label for="nome" class="form-label">Nome Completo *</label>
                                <input type="text" class="form-control" id="nome" name="nome" 
                                       value="{{ paciente[1] }}" required>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="cpf" class="form-label">CPF</label>
                                <input type="text" class="form-control" id="cpf" name="cpf" 
                                       value="{{ paciente[2] or '' }}" placeholder="000.000.000-00">
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="data_nascimento" class="form-label">Data de Nascimento</label>
                                <input type="date" class="form-control" id="data_nascimento" name="data_nascimento"
                                       value="{{ paciente[3] }}">
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="telefone" class="form-label">Telefone</label>
                                <input type="text" class="form-control" id="telefone" name="telefone"
                                       value="{{ paciente[4] or '' }}" placeholder="(00) 00000-0000">
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="email" class="form-label">E-mail</label>
                                <input type="email" class="form-control" id="email" name="email"
                                       value="{{ paciente[5] or '' }}">
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="endereco" class="form-label">Endereço</label>
                        <textarea class="form-control" id="endereco" name="endereco" rows="2">{{ paciente[6] or '' }}</textarea>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="convenio" class="form-label">Convênio</label>
                                <select class="form-select" id="convenio" name="convenio">
                                    <option value="" {% if not paciente[7] %}selected{% endif %}>Particular</option>
                                    <option value="Unimed" {% if paciente[7] == 'Unimed' %}selected{% endif %}>Unimed</option>
                                    <option value="Bradesco Saúde" {% if paciente[7] == 'Bradesco Saúde' %}selected{% endif %}>Bradesco Saúde</option>
                                    <option value="SulAmérica" {% if paciente[7] == 'SulAmérica' %}selected{% endif %}>SulAmérica</option>
                                    <option value="Amil" {% if paciente[7] == 'Amil' %}selected{% endif %}>Amil</option>
                                    <option value="Outro" {% if paciente[7] and paciente[7] not in ['Unimed', 'Bradesco Saúde', 'SulAmérica', 'Amil'] %}selected{% endif %}>Outro</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="observacoes" class="form-label">Observações</label>
                        <textarea class="form-control" id="observacoes" name="observacoes" rows="3">{{ paciente[8] or '' }}</textarea>
                    </div>
                    
                    <div class="d-flex justify-content-between">
                        <a href="/paciente/{{ paciente[0] }}" class="btn btn-secondary">
                            <i class="fas fa-times"></i> Cancelar
                        </a>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Salvar Alterações
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
// Máscaras (mesmas do novo paciente)
document.getElementById('cpf').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\\d{3})(\\d{3})(\\d{3})(\\d{2})/, '$1.$2.$3-$4');
        e.target.value = value;
    }
});

document.getElementById('telefone').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\\d{2})(\\d{5})(\\d{4})/, '($1) $2-$3');
        e.target.value = value;
    }
});
</script>
{% endblock %}'''
    
    with open('/root/clawd/templates/editar_paciente.html', 'w') as f:
        f.write(template)
    print("✅ Template editar_paciente.html criado")

def criar_template_agenda():
    """Cria template para agenda de consultas"""
    template = '''{% extends "base.html" %}

{% block title %}Agenda - Clínica Dr. Felipe{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-calendar-alt"></i> Agenda de Consultas</h1>
    </div>
</div>

<!-- Consultas de Hoje -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card border-primary">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="fas fa-calendar-day"></i> Consultas de Hoje</h4>
            </div>
            <div class="card-body">
                {% if consultas_hoje %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Horário</th>
                                <th>Paciente</th>
                                <th>Telefone</th>
                                <th>Motivo</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for consulta in consultas_hoje %}
                            <tr>
                                <td>
                                    <i class="fas fa-clock"></i> 
                                    {{ consulta[2].strftime('%H:%M') if consulta[2] else '-' }}
                                </td>
                                <td><strong>{{ consulta[1] }}</strong></td>
                                <td>{{ consulta[4] or '-' }}</td>
                                <td>{{ consulta[3] or 'Consulta' }}</td>
                                <td>
                                    <a href="/paciente/{{ consulta[5] }}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-user"></i> Ver Paciente
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted text-center py-3">
                    <i class="fas fa-calendar-times"></i> Nenhuma consulta agendada para hoje
                </p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Próximas Consultas -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0"><i class="fas fa-calendar-week"></i> Próximas Consultas</h4>
            </div>
            <div class="card-body">
                {% if consultas_futuras %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Paciente</th>
                                <th>Telefone</th>
                                <th>Motivo</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for consulta in consultas_futuras %}
                            <tr>
                                <td>
                                    <i class="fas fa-calendar"></i> 
                                    {{ consulta[2].strftime('%d/%m/%Y %H:%M') if consulta[2] else '-' }}
                                </td>
                                <td><strong>{{ consulta[1] }}</strong></td>
                                <td>{{ consulta[4] or '-' }}</td>
                                <td>{{ consulta[3] or 'Consulta' }}</td>
                                <td>
                                    <a href="/paciente/{{ consulta[5] }}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-user"></i> Ver Paciente
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted text-center py-3">
                    <i class="fas fa-calendar-times"></i> Nenhuma consulta futura agendada
                </p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open('/root/clawd/templates/agenda.html', 'w') as f:
        f.write(template)
    print("✅ Template agenda.html criado")

def atualizar_pacientes_template():
    """Atualiza template de pacientes com botão de novo paciente"""
    arquivo = '/root/clawd/templates/pacientes.html'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Adicionar botão de novo paciente
    conteudo = conteudo.replace(
        '<a href="/importar" class="btn btn-success">',
        '''<div>
                <a href="/paciente/novo" class="btn btn-primary me-2">
                    <i class="fas fa-user-plus"></i> Novo Paciente
                </a>
                <a href="/importar" class="btn btn-success">'''
    )
    conteudo = conteudo.replace(
        '</a>',
        '</a>\n            </div>',
        1  # Substituir apenas a primeira ocorrência
    )
    
    with open(arquivo, 'w') as f:
        f.write(conteudo)
    print("✅ Template pacientes.html atualizado")

def atualizar_paciente_detalhes():
    """Atualiza template de detalhes com upload e editar"""
    arquivo = '/root/clawd/templates/paciente_detalhes.html'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Adicionar botão editar após o nome
    if '<h1>{{ paciente[1] }}</h1>' in conteudo:
        conteudo = conteudo.replace(
            '<h1>{{ paciente[1] }}</h1>',
            '''<div class="d-flex justify-content-between align-items-center">
            <h1>{{ paciente[1] }}</h1>
            <a href="/paciente/{{ paciente[0] }}/editar" class="btn btn-warning">
                <i class="fas fa-edit"></i> Editar Dados
            </a>
        </div>'''
        )
    
    # Adicionar seção de upload de exames
    upload_section = '''
                <!-- Upload de Exames -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h4><i class="fas fa-file-medical"></i> Upload de Exames/Documentos</h4>
                    </div>
                    <div class="card-body">
                        <form action="/paciente/{{ paciente[0] }}/upload_exame" method="post" enctype="multipart/form-data">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="arquivo" class="form-label">Arquivo</label>
                                        <input type="file" class="form-control" id="arquivo" name="arquivo" 
                                               accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" required>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-3">
                                        <label for="tipo_exame" class="form-label">Tipo</label>
                                        <select class="form-select" id="tipo_exame" name="tipo_exame">
                                            <option value="Exame_Sangue">Exame de Sangue</option>
                                            <option value="RX">Raio-X</option>
                                            <option value="RNM">Ressonância</option>
                                            <option value="TC">Tomografia</option>
                                            <option value="USG">Ultrassom</option>
                                            <option value="Outro">Outro</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-3">
                                        <label for="data_exame" class="form-label">Data</label>
                                        <input type="date" class="form-control" id="data_exame" name="data_exame">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="descricao" class="form-label">Descrição</label>
                                <input type="text" class="form-control" id="descricao" name="descricao" 
                                       placeholder="Descrição opcional do exame">
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-upload"></i> Enviar Arquivo
                            </button>
                        </form>
                    </div>
                </div>
                
                <!-- Arquivos Anexados -->
                {% if anexos %}
                <div class="card mt-4">
                    <div class="card-header">
                        <h4><i class="fas fa-paperclip"></i> Arquivos Anexados</h4>
                    </div>
                    <div class="card-body">
                        <div class="list-group">
                            {% for anexo in anexos %}
                            <a href="/download/{{ paciente[0] }}/{{ anexo }}" class="list-group-item list-group-item-action">
                                <i class="fas fa-file"></i> {{ anexo }}
                            </a>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                {% endif %}'''
    
    # Inserir antes do fechamento da div principal
    pos = conteudo.rfind('{% endblock %}')
    if pos > 0:
        conteudo = conteudo[:pos] + upload_section + '\n' + conteudo[pos:]
    
    with open(arquivo, 'w') as f:
        f.write(conteudo)
    print("✅ Template paciente_detalhes.html atualizado")

def main():
    print("🚀 IMPLEMENTANDO TODAS AS MELHORIAS")
    print("=" * 60)
    
    # Adicionar rotas ao web_interface.py
    adicionar_rotas_melhoradas()
    
    # Criar novos templates
    criar_template_novo_paciente()
    criar_template_editar_paciente()
    criar_template_agenda()
    
    # Atualizar templates existentes
    atualizar_template_base()
    atualizar_pacientes_template()
    atualizar_paciente_detalhes()
    
    # Criar pasta para anexos
    os.makedirs('/root/clawd/anexos_pacientes', exist_ok=True)
    
    print("\n✅ TODAS AS MELHORIAS IMPLEMENTADAS!")
    print("\n📝 Funcionalidades adicionadas:")
    print("1. ➕ Adicionar novo paciente (sem importar)")
    print("2. ✏️ Editar dados do paciente")
    print("3. 📎 Upload de exames/documentos")
    print("4. 📅 Agenda de consultas")
    print("\n🔄 Reiniciando o servidor...")

if __name__ == "__main__":
    main()
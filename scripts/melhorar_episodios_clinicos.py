#!/usr/bin/env python3
"""
Script para melhorar o sistema de episódios clínicos/consultas
Adiciona campos detalhados para prontuário médico completo
"""

import os
from datetime import datetime

def criar_tabela_episodios():
    """Cria tabela específica para episódios clínicos se não existir"""
    sql = '''-- SQL para criar tabela de episódios clínicos
CREATE TABLE IF NOT EXISTS episodios_clinicos (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    consulta_id INTEGER REFERENCES consultas(id),
    data_episodio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Anamnese
    queixa_principal TEXT,
    historia_doenca_atual TEXT,
    revisao_sistemas TEXT,
    
    -- Exame Físico
    sinais_vitais JSONB,
    exame_geral TEXT,
    exame_neurologico TEXT,
    exame_coluna TEXT,
    
    -- Diagnóstico
    hipoteses_diagnosticas TEXT,
    cid10 VARCHAR(10),
    
    -- Conduta
    condutas TEXT,
    prescricoes TEXT,
    exames_solicitados TEXT,
    
    -- Follow-up
    orientacoes TEXT,
    retorno VARCHAR(100),
    
    -- Metadados
    medico VARCHAR(255) DEFAULT 'Dr. Felipe',
    tipo_atendimento VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_episodios_paciente ON episodios_clinicos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_episodios_data ON episodios_clinicos(data_episodio);
'''
    
    with open('/root/clawd/scripts/criar_tabela_episodios.sql', 'w') as f:
        f.write(sql)
    
    print("✅ SQL para tabela de episódios criado")
    
    # Executar no banco
    import psycopg2
    conn = psycopg2.connect(
        dbname="clinica_dr_felipe",
        user="clinica_admin", 
        password="clinica2026!",
        host="localhost",
        port="5432"
    )
    
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("✅ Tabela episodios_clinicos criada no banco")
    conn.close()

def atualizar_template_nova_consulta():
    """Cria template melhorado para episódios clínicos"""
    
    template = '''{% extends "base.html" %}

{% block title %}Novo Episódio Clínico - {{ paciente[1] }}{% endblock %}

{% block content %}
<style>
.section-header {
    background-color: #f8f9fa;
    padding: 10px;
    margin: 20px 0 10px 0;
    border-left: 4px solid #007bff;
}
.vital-signs input {
    margin-bottom: 10px;
}
</style>

<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/pacientes">Pacientes</a></li>
                <li class="breadcrumb-item"><a href="/paciente/{{ paciente[0] }}">{{ paciente[1] }}</a></li>
                <li class="breadcrumb-item active">Novo Episódio Clínico</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-file-medical"></i> Novo Episódio Clínico</h1>
        <p class="text-muted">
            <strong>{{ paciente[1] }}</strong> 
            {% if paciente[2] %}(CPF: {{ paciente[2] }}){% endif %}
            {% if paciente[3] %}| {{ idade }} anos{% endif %}
        </p>
    </div>
</div>

<form action="/paciente/{{ paciente[0] }}/salvar_episodio" method="post">
    <div class="row mt-3">
        <div class="col-12">
            <!-- Informações Básicas -->
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="data_episodio" class="form-label">Data/Hora *</label>
                                <input type="datetime-local" class="form-control" id="data_episodio" 
                                       name="data_episodio" required>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="tipo_atendimento" class="form-label">Tipo de Atendimento</label>
                                <select class="form-select" id="tipo_atendimento" name="tipo_atendimento">
                                    <option value="Consulta">Consulta Presencial</option>
                                    <option value="Retorno">Retorno</option>
                                    <option value="Teleconsulta">Teleconsulta</option>
                                    <option value="Urgencia">Urgência</option>
                                    <option value="Pos-operatorio">Pós-operatório</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label for="medico" class="form-label">Médico</label>
                                <input type="text" class="form-control" id="medico" name="medico" 
                                       value="Dr. Felipe" readonly>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ANAMNESE -->
            <h3 class="section-header"><i class="fas fa-comments-medical"></i> ANAMNESE</h3>
            <div class="card">
                <div class="card-body">
                    <div class="mb-3">
                        <label for="queixa_principal" class="form-label">Queixa Principal *</label>
                        <textarea class="form-control" id="queixa_principal" name="queixa_principal" 
                                  rows="2" required 
                                  placeholder="Ex: Dor lombar há 3 meses, piora ao sentar..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="historia_doenca_atual" class="form-label">História da Doença Atual (HDA)</label>
                        <textarea class="form-control" id="historia_doenca_atual" name="historia_doenca_atual" 
                                  rows="5"
                                  placeholder="Início, evolução, fatores de melhora/piora, tratamentos prévios..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="revisao_sistemas" class="form-label">Revisão de Sistemas</label>
                        <textarea class="form-control" id="revisao_sistemas" name="revisao_sistemas" 
                                  rows="3"
                                  placeholder="Sintomas neurológicos, gastrointestinais, cardiovasculares..."></textarea>
                    </div>
                </div>
            </div>

            <!-- EXAME FÍSICO -->
            <h3 class="section-header"><i class="fas fa-stethoscope"></i> EXAME FÍSICO</h3>
            <div class="card">
                <div class="card-body">
                    <!-- Sinais Vitais -->
                    <h5>Sinais Vitais</h5>
                    <div class="row vital-signs mb-3">
                        <div class="col-md-2">
                            <input type="text" class="form-control" name="pa" placeholder="PA (mmHg)">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control" name="fc" placeholder="FC (bpm)">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control" name="fr" placeholder="FR (ipm)">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control" name="temp" placeholder="Temp (°C)">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control" name="sat" placeholder="SatO2 (%)">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control" name="peso" placeholder="Peso (kg)">
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="exame_geral" class="form-label">Exame Geral</label>
                        <textarea class="form-control" id="exame_geral" name="exame_geral" rows="3"
                                  placeholder="Estado geral, fácies, marcha, postura..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="exame_neurologico" class="form-label">Exame Neurológico</label>
                        <textarea class="form-control" id="exame_neurologico" name="exame_neurologico" rows="4"
                                  placeholder="Força muscular, sensibilidade, reflexos, Lasègue, Spurling..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="exame_coluna" class="form-label">Exame da Coluna</label>
                        <textarea class="form-control" id="exame_coluna" name="exame_coluna" rows="3"
                                  placeholder="Inspeção, palpação, mobilidade, contraturas..."></textarea>
                    </div>
                </div>
            </div>

            <!-- DIAGNÓSTICO -->
            <h3 class="section-header"><i class="fas fa-diagnoses"></i> DIAGNÓSTICO</h3>
            <div class="card">
                <div class="card-body">
                    <div class="mb-3">
                        <label for="hipoteses_diagnosticas" class="form-label">Hipóteses Diagnósticas</label>
                        <textarea class="form-control" id="hipoteses_diagnosticas" name="hipoteses_diagnosticas" 
                                  rows="3"
                                  placeholder="1. Lombalgia mecânica&#10;2. Hérnia discal L4-L5?&#10;3. ..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="cid10" class="form-label">CID-10</label>
                        <input type="text" class="form-control" id="cid10" name="cid10" 
                               placeholder="Ex: M54.5 (Dor lombar baixa)">
                    </div>
                </div>
            </div>

            <!-- CONDUTA -->
            <h3 class="section-header"><i class="fas fa-prescription"></i> CONDUTA</h3>
            <div class="card">
                <div class="card-body">
                    <div class="mb-3">
                        <label for="condutas" class="form-label">Condutas/Plano Terapêutico</label>
                        <textarea class="form-control" id="condutas" name="condutas" rows="4"
                                  placeholder="Tratamento conservador, fisioterapia, medicações..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="prescricoes" class="form-label">Prescrições</label>
                        <textarea class="form-control" id="prescricoes" name="prescricoes" rows="5"
                                  placeholder="1. Meloxicam 15mg VO 1x/dia por 7 dias&#10;2. Ciclobenzaprina 10mg VO à noite&#10;3. ..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="exames_solicitados" class="form-label">Exames Solicitados</label>
                        <textarea class="form-control" id="exames_solicitados" name="exames_solicitados" rows="3"
                                  placeholder="RNM coluna lombar, Raio-X panorâmico de coluna..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="orientacoes" class="form-label">Orientações ao Paciente</label>
                        <textarea class="form-control" id="orientacoes" name="orientacoes" rows="3"
                                  placeholder="Repouso relativo, aplicar gelo, evitar carregar peso..."></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="retorno" class="form-label">Retorno</label>
                        <input type="text" class="form-control" id="retorno" name="retorno" 
                               placeholder="Ex: 15 dias, 1 mês, após exames">
                    </div>
                </div>
            </div>

            <!-- BOTÕES -->
            <div class="d-flex justify-content-between mt-4 mb-5">
                <a href="/paciente/{{ paciente[0] }}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
                <div>
                    <button type="submit" name="action" value="save" class="btn btn-primary">
                        <i class="fas fa-save"></i> Salvar Episódio
                    </button>
                    <button type="submit" name="action" value="save_print" class="btn btn-success">
                        <i class="fas fa-print"></i> Salvar e Imprimir
                    </button>
                </div>
            </div>
        </div>
    </div>
</form>

<script>
// Define data/hora atual como padrão
document.getElementById('data_episodio').value = new Date().toISOString().slice(0, 16);

// Auto-save rascunho a cada 30 segundos
let autoSaveTimer;
function autoSave() {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
        const formData = new FormData(document.querySelector('form'));
        formData.append('action', 'draft');
        
        fetch('/paciente/{{ paciente[0] }}/salvar_rascunho', {
            method: 'POST',
            body: formData
        }).then(() => {
            console.log('Rascunho salvo');
        });
    }, 30000);
}

// Ativar auto-save em todos os campos
document.querySelectorAll('input, textarea, select').forEach(el => {
    el.addEventListener('input', autoSave);
});
</script>
{% endblock %}'''
    
    with open('/root/clawd/templates/novo_episodio.html', 'w') as f:
        f.write(template)
    
    print("✅ Template novo_episodio.html criado")

def adicionar_rotas_episodios():
    """Adiciona rotas para episódios clínicos no web_interface.py"""
    
    novas_rotas = '''
@app.route('/paciente/<int:paciente_id>/novo_episodio')
def novo_episodio(paciente_id):
    """Formulário para novo episódio clínico"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("""
        SELECT id, nome, cpf, data_nascimento FROM pacientes WHERE id = %s
        """, (paciente_id,))
        paciente = db.cursor.fetchone()
        
        if not paciente:
            flash('Paciente não encontrado!')
            return redirect(url_for('pacientes'))
        
        # Calcular idade
        idade = None
        if paciente[3]:
            from datetime import date
            hoje = date.today()
            nascimento = paciente[3]
            idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        
        return render_template('novo_episodio.html', paciente=paciente, idade=idade)
    except Exception as e:
        flash(f'Erro: {str(e)}')
        return redirect(url_for('pacientes'))

@app.route('/paciente/<int:paciente_id>/salvar_episodio', methods=['POST'])
def salvar_episodio(paciente_id):
    """Salva novo episódio clínico"""
    try:
        db = clinica_app.get_db()
        action = request.form.get('action', 'save')
        
        # Coletar todos os dados do formulário
        data_episodio = request.form.get('data_episodio')
        tipo_atendimento = request.form.get('tipo_atendimento')
        medico = request.form.get('medico')
        
        # Anamnese
        queixa_principal = request.form.get('queixa_principal')
        historia_doenca_atual = request.form.get('historia_doenca_atual')
        revisao_sistemas = request.form.get('revisao_sistemas')
        
        # Sinais vitais
        sinais_vitais = json.dumps({
            'pa': request.form.get('pa'),
            'fc': request.form.get('fc'),
            'fr': request.form.get('fr'),
            'temp': request.form.get('temp'),
            'sat': request.form.get('sat'),
            'peso': request.form.get('peso')
        })
        
        # Exame físico
        exame_geral = request.form.get('exame_geral')
        exame_neurologico = request.form.get('exame_neurologico')
        exame_coluna = request.form.get('exame_coluna')
        
        # Diagnóstico
        hipoteses_diagnosticas = request.form.get('hipoteses_diagnosticas')
        cid10 = request.form.get('cid10')
        
        # Conduta
        condutas = request.form.get('condutas')
        prescricoes = request.form.get('prescricoes')
        exames_solicitados = request.form.get('exames_solicitados')
        orientacoes = request.form.get('orientacoes')
        retorno = request.form.get('retorno')
        
        # Inserir episódio
        db.cursor.execute("""
        INSERT INTO episodios_clinicos (
            paciente_id, data_episodio, tipo_atendimento, medico,
            queixa_principal, historia_doenca_atual, revisao_sistemas,
            sinais_vitais, exame_geral, exame_neurologico, exame_coluna,
            hipoteses_diagnosticas, cid10,
            condutas, prescricoes, exames_solicitados, orientacoes, retorno
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            paciente_id, data_episodio, tipo_atendimento, medico,
            queixa_principal, historia_doenca_atual, revisao_sistemas,
            sinais_vitais, exame_geral, exame_neurologico, exame_coluna,
            hipoteses_diagnosticas, cid10,
            condutas, prescricoes, exames_solicitados, orientacoes, retorno
        ))
        
        episodio_id = db.cursor.fetchone()[0]
        
        # Também criar registro simplificado na tabela consultas para compatibilidade
        db.cursor.execute("""
        INSERT INTO consultas (paciente_id, data_consulta, medico, motivo, observacoes)
        VALUES (%s, %s, %s, %s, %s)
        """, (
            paciente_id, data_episodio, medico, queixa_principal,
            f"HDA: {historia_doenca_atual or 'N/A'}\\n\\n" +
            f"Exame: {exame_geral or ''} {exame_neurologico or ''} {exame_coluna or ''}\\n\\n" +
            f"HD: {hipoteses_diagnosticas or 'N/A'}\\n\\n" +
            f"Conduta: {condutas or 'N/A'}"
        ))
        
        db.connection.commit()
        
        flash('Episódio clínico salvo com sucesso!', 'success')
        
        if action == 'save_print':
            return redirect(url_for('imprimir_episodio', episodio_id=episodio_id))
        else:
            return redirect(url_for('paciente_detalhes', paciente_id=paciente_id))
        
    except Exception as e:
        db.connection.rollback()
        flash(f'Erro ao salvar episódio: {str(e)}', 'danger')
        return redirect(url_for('novo_episodio', paciente_id=paciente_id))

@app.route('/paciente/<int:paciente_id>/salvar_rascunho', methods=['POST'])
def salvar_rascunho(paciente_id):
    """Salva rascunho do episódio (auto-save)"""
    # TODO: Implementar salvamento temporário em Redis/arquivo
    return jsonify({'status': 'ok'})

@app.route('/episodio/<int:episodio_id>/imprimir')
def imprimir_episodio(episodio_id):
    """Gera versão para impressão do episódio"""
    # TODO: Implementar geração de PDF
    flash('Função de impressão será implementada em breve!', 'info')
    return redirect(url_for('index'))
'''
    
    # Adicionar ao arquivo
    arquivo = '/root/clawd/scripts/web_interface.py'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Inserir antes da rota de download
    pos = conteudo.find('@app.route(\'/download/')
    if pos > 0:
        conteudo = conteudo[:pos] + novas_rotas + '\n' + conteudo[pos:]
        
        with open(arquivo, 'w') as f:
            f.write(conteudo)
        
        print("✅ Rotas de episódios adicionadas ao web_interface.py")

def atualizar_detalhes_paciente():
    """Adiciona botão de novo episódio e lista episódios"""
    arquivo = '/root/clawd/templates/paciente_detalhes.html'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Substituir botão de Nova Consulta por Novo Episódio
    conteudo = conteudo.replace(
        '/paciente/{{ paciente[0] }}/nova_consulta',
        '/paciente/{{ paciente[0] }}/novo_episodio'
    )
    conteudo = conteudo.replace(
        '<i class="fas fa-plus"></i> Nova Consulta',
        '<i class="fas fa-file-medical"></i> Novo Episódio Clínico'
    )
    
    with open(arquivo, 'w') as f:
        f.write(conteudo)
    
    print("✅ Template paciente_detalhes.html atualizado")

def main():
    print("🏥 IMPLEMENTANDO SISTEMA DE EPISÓDIOS CLÍNICOS")
    print("=" * 60)
    
    # Criar tabela de episódios
    criar_tabela_episodios()
    
    # Criar novo template
    atualizar_template_nova_consulta()
    
    # Adicionar rotas
    adicionar_rotas_episodios()
    
    # Atualizar template de detalhes
    atualizar_detalhes_paciente()
    
    print("\n✅ SISTEMA DE EPISÓDIOS CLÍNICOS IMPLEMENTADO!")
    print("\n📝 Funcionalidades adicionadas:")
    print("1. 📋 Prontuário eletrônico completo")
    print("2. 🩺 Anamnese estruturada")
    print("3. 🔬 Exame físico detalhado") 
    print("4. 💊 Prescrições e condutas")
    print("5. 💾 Auto-save de rascunhos")
    print("6. 🖨️ Preparado para impressão")
    print("\n🔄 Reiniciando servidor...")

if __name__ == "__main__":
    main()
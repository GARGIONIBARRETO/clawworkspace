#!/usr/bin/env python3
"""
Interface Web para Sistema de Gestão da Clínica Dr. Felipe
Flask Web App para gestão de pacientes, consultas e importação
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
import sys
import os
import pandas as pd
from datetime import datetime
import json

sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

app = Flask(__name__, template_folder='/root/clawd/templates')
app.secret_key = 'clinica_dr_felipe_2026'

class ClinicaWebApp:
    def __init__(self):
        self.db = None
    
    def get_db(self):
        if not self.db:
            self.db = PostgreSQLLocal()
        return self.db
    
    def close_db(self):
        if self.db:
            self.db.close()
            self.db = None

clinica_app = ClinicaWebApp()

@app.route('/')
def index():
    """Página principal - Dashboard"""
    try:
        db = clinica_app.get_db()
        stats = db.get_stats()
        
        # Consultas recentes
        db.cursor.execute("""
        SELECT p.nome, c.data_consulta, c.motivo, c.medico 
        FROM consultas c 
        JOIN pacientes p ON c.paciente_id = p.id 
        ORDER BY c.data_consulta DESC 
        LIMIT 5
        """)
        consultas_recentes = db.cursor.fetchall()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             consultas_recentes=consultas_recentes)
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/pacientes')
def pacientes():
    """Lista de pacientes"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("SELECT id, nome, cpf, telefone, convenio FROM pacientes ORDER BY nome")
        pacientes_list = db.cursor.fetchall()
        
        return render_template('pacientes.html', pacientes=pacientes_list)
    except Exception as e:
        return f"Erro: {str(e)}"


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

@app.route('/paciente/<int:paciente_id>')
def paciente_detalhes(paciente_id):
    """Detalhes de um paciente específico"""
    try:
        db = clinica_app.get_db()
        
        # Dados do paciente
        db.cursor.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
        paciente = db.cursor.fetchone()
        
        if not paciente:
            flash("Paciente não encontrado!")
            return redirect(url_for('pacientes'))
        
        # Consultas do paciente
        db.cursor.execute("""
        SELECT data_consulta, medico, motivo, observacoes 
        FROM consultas 
        WHERE paciente_id = %s 
        ORDER BY data_consulta DESC
        """, (paciente_id,))
        consultas = db.cursor.fetchall()
        
        # Bioimpedância do paciente
        db.cursor.execute("""
        SELECT data_medicao, peso, altura, imc, gordura_corporal, massa_muscular, agua_corporal
        FROM bioimpedancia 
        WHERE paciente_id = %s 
        ORDER BY data_medicao DESC
        """, (paciente_id,))
        bioimpedancia = db.cursor.fetchall()
        
        # Exames laboratoriais
        db.cursor.execute("""
        SELECT data_exame, tipo_exame, laboratorio, parametros, observacoes
        FROM exames_laboratoriais 
        WHERE paciente_id = %s 
        ORDER BY data_exame DESC
        """, (paciente_id,))
        exames = db.cursor.fetchall()
        
        # Anexos (verificar se existem arquivos)
        cpf = paciente[2]  # CPF é a terceira coluna
        pasta_anexos = f'/root/clawd/anexos_pacientes/paciente_{paciente_id}_{cpf}'
        anexos = []
        if os.path.exists(pasta_anexos):
            for arquivo in os.listdir(pasta_anexos):
                if os.path.isfile(os.path.join(pasta_anexos, arquivo)):
                    anexos.append(arquivo)
        
        return render_template('paciente_detalhes.html', 
                             paciente=paciente, 
                             consultas=consultas,
                             bioimpedancia=bioimpedancia,
                             exames=exames,
                             anexos=anexos)
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/importar')
def importar():
    """Página de importação"""
    return render_template('importar.html')

@app.route('/api/status')
def api_status():
    """API para status do sistema"""
    try:
        db = clinica_app.get_db()
        stats = db.get_stats()
        return jsonify({
            'status': 'ok',
            'database': 'PostgreSQL Local',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Upload de arquivos CSV para importação"""
    try:
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('importar'))
        
        file = request.files['file']
        tipo_importacao = request.form.get('tipo', 'pacientes')
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('importar'))
        
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.zip') or 
                     file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf'))):
            # Salvar arquivo
            upload_folder = f'/root/clawd/importacao/{tipo_importacao}'
            os.makedirs(upload_folder, exist_ok=True)
            
            # Manter extensão original para anexos
            if tipo_importacao == 'anexos':
                filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file.filename}'
            else:
                filename = f'upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            flash(f'Arquivo {filename} salvo com sucesso!')
            
            # Processar importação imediatamente
            return processar_importacao_web(tipo_importacao, file_path)
        
        flash('Formato de arquivo inválido! Use apenas CSV.')
        return redirect(url_for('importar'))
        
    except Exception as e:
        flash(f'Erro no upload: {str(e)}')
        return redirect(url_for('importar'))

def processar_importacao_web(tipo, file_path):
    """Processa importação web"""
    try:
        db = clinica_app.get_db()
        df = pd.read_csv(file_path)
        
        importados = 0
        
        if tipo == 'pacientes':
            for _, row in df.iterrows():
                cpf = str(row['cpf']).replace('.', '').replace('-', '')
                
                db.cursor.execute("""
                INSERT INTO pacientes (nome, cpf, rg, telefone, email, endereco, data_nascimento, convenio, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (cpf) DO NOTHING
                """, (
                    row['nome'], cpf, str(row.get('rg', '')), 
                    str(row.get('telefone', '')), str(row.get('email', '')),
                    str(row.get('endereco', '')), row.get('data_nascimento'),
                    str(row.get('convenio', 'Particular'))
                ))
                
                if db.cursor.rowcount > 0:
                    importados += 1
        
        elif tipo == 'consultas':
            for _, row in df.iterrows():
                cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
                
                db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
                paciente = db.cursor.fetchone()
                
                if paciente:
                    db.cursor.execute("""
                    INSERT INTO consultas (paciente_id, data_consulta, medico, motivo, observacoes, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """, (
                        paciente[0], row['data_consulta'], 
                        str(row.get('medico', 'Dr. Felipe')),
                        str(row.get('motivo', '')), str(row.get('observacoes', ''))
                    ))
                    importados += 1
        
        elif tipo == 'bioimpedancia':
            for _, row in df.iterrows():
                cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
                
                db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
                paciente = db.cursor.fetchone()
                
                if paciente:
                    db.cursor.execute("""
                    INSERT INTO bioimpedancia (paciente_id, data_medicao, peso, altura, imc, 
                                             gordura_corporal, massa_muscular, agua_corporal, observacoes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        paciente[0], row['data_medicao'],
                        row.get('peso'), row.get('altura'), row.get('imc'),
                        row.get('gordura_corporal'), row.get('massa_muscular'), row.get('agua_corporal'),
                        str(row.get('observacoes', ''))
                    ))
                    importados += 1
        
        elif tipo == 'exames_laboratoriais':
            for _, row in df.iterrows():
                cpf = str(row['cpf_paciente']).replace('.', '').replace('-', '')
                
                db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
                paciente = db.cursor.fetchone()
                
                if paciente:
                    # Converter parametros para JSON se for string
                    parametros = row.get('parametros_json', '{}')
                    if isinstance(parametros, str):
                        try:
                            parametros = json.loads(parametros)
                        except:
                            parametros = {}
                    
                    db.cursor.execute("""
                    INSERT INTO exames_laboratoriais (paciente_id, data_exame, tipo_exame, laboratorio, parametros, observacoes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        paciente[0], row['data_exame'], 
                        str(row.get('tipo_exame', 'Exame Laboratorial')),
                        str(row.get('laboratorio', '')),
                        json.dumps(parametros), str(row.get('observacoes', ''))
                    ))
                    importados += 1
        
        elif tipo == 'anexos':
            # Para anexos, apenas mover arquivo para pasta organizada
            # Nome do arquivo deve ser: CPF_tipo_exame.extensao
            filename = os.path.basename(file_path)
            if '_' in filename:
                parts = filename.split('_')
                if len(parts) >= 2:
                    cpf = parts[0].replace('.', '').replace('-', '')
                    
                    # Verificar se paciente existe
                    db.cursor.execute("SELECT id FROM pacientes WHERE cpf = %s", (cpf,))
                    paciente = db.cursor.fetchone()
                    
                    if paciente:
                        # Criar pasta do paciente
                        pasta_destino = f'/root/clawd/anexos_pacientes/paciente_{paciente[0]}_{cpf}'
                        os.makedirs(pasta_destino, exist_ok=True)
                        
                        # Mover arquivo
                        import shutil
                        destino_final = os.path.join(pasta_destino, filename)
                        shutil.move(file_path, destino_final)
                        importados = 1
                        flash(f'Anexo organizado para paciente CPF: {cpf}')
                    else:
                        flash(f'Paciente com CPF {cpf} não encontrado!')
            else:
                flash('Formato de nome incorreto! Use: CPF_tipo_exame.extensao')
            
            return redirect(url_for('importar'))
        
        db.connection.commit()
        flash(f'Importação concluída! {importados} registros importados.')
        
    except Exception as e:
        flash(f'Erro na importação: {str(e)}')
    
    return redirect(url_for('importar'))

@app.route('/anexos/<int:paciente_id>/<filename>')
def servir_anexo(paciente_id, filename):
    """Serve arquivos de anexos do paciente"""
    try:
        db = clinica_app.get_db()
        
        # Verificar se paciente existe e obter CPF
        db.cursor.execute("SELECT cpf FROM pacientes WHERE id = %s", (paciente_id,))
        paciente = db.cursor.fetchone()
        
        if not paciente:
            abort(404)
        
        cpf = paciente[0]
        pasta_anexos = f'/root/clawd/anexos_pacientes/paciente_{paciente_id}_{cpf}'
        arquivo_path = os.path.join(pasta_anexos, filename)
        
        if os.path.exists(arquivo_path):
            return send_file(arquivo_path)
        else:
            abort(404)
    except Exception as e:
        abort(404)

@app.route('/templates/<filename>')
def download_template(filename):
    """Download de templates CSV"""
    template_path = f'/root/clawd/templates/{filename}'
    if os.path.exists(template_path):
        return send_file(template_path, as_attachment=True)
    else:
        abort(404)

@app.teardown_appcontext
def close_db_connection(error):
    """Fecha conexão do banco ao final da requisição"""
    clinica_app.close_db()

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
        cpf_result = db.cursor.fetchone()
        cpf = cpf_result[0] if cpf_result and cpf_result[0] else 'sem_cpf'
        
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
            f"HDA: {historia_doenca_atual or 'N/A'}\n\n" +
            f"Exame: {exame_geral or ''} {exame_neurologico or ''} {exame_coluna or ''}\n\n" +
            f"HD: {hipoteses_diagnosticas or 'N/A'}\n\n" +
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

@app.route('/download/<int:paciente_id>/<arquivo>')
def download_anexo(paciente_id, arquivo):
    """Download de anexos do paciente"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("SELECT cpf FROM pacientes WHERE id = %s", (paciente_id,))
        cpf_result = db.cursor.fetchone()
        cpf = cpf_result[0] if cpf_result and cpf_result[0] else 'sem_cpf'
        
        pasta = f'/root/clawd/anexos_pacientes/paciente_{paciente_id}_{cpf}'
        caminho = os.path.join(pasta, arquivo)
        
        if os.path.exists(caminho):
            return send_file(caminho, as_attachment=True)
        else:
            abort(404)
    except Exception as e:
        abort(404)

if __name__ == '__main__':
    # Criar templates se não existirem
    templates_dir = '/root/clawd/templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    print("🚀 Iniciando Interface Web da Clínica...")
    print("🌐 Acesse: http://YOUR_SERVER_IP:5000")
    print("💡 Para parar: Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
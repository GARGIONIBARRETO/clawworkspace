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

if __name__ == '__main__':
    # Criar templates se não existirem
    templates_dir = '/root/clawd/templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    print("🚀 Iniciando Interface Web da Clínica...")
    print("🌐 Acesse: http://YOUR_SERVER_IP:5000")
    print("💡 Para parar: Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
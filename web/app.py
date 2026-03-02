#!/usr/bin/env python3
"""
API Web para Sistema de Pacientes - Dr. Felipe
Versão simplificada para PostgreSQL local
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
import sys
import os
from datetime import datetime
from functools import wraps

# Adiciona o diretório scripts ao path
sys.path.append('/root/clawd/scripts')

try:
    from web_db_adapter import PacientesManager
    DB_AVAILABLE = True
    print("✅ Usando PostgreSQL local")
except Exception as e:
    print(f"⚠️ Banco indisponível: {e}")
    DB_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.secret_key = 'dr_felipe_clinica_2026_secure_key'

# =================== AUTENTICAÇÃO ===================

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'drfelipe' and password == 'clinica2026':
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# =================== ROTAS PRINCIPAIS ===================

@app.route('/')
@require_login
def dashboard():
    """Dashboard principal"""
    if not DB_AVAILABLE:
        return render_template('no_connection.html')
    
    manager = PacientesManager()
    stats = manager.get_stats()
    manager.close()
    
    return render_template('dashboard.html', stats=stats)

@app.route('/pacientes')
@require_login
def listar_pacientes():
    """Lista todos os pacientes"""
    if not DB_AVAILABLE:
        return render_template('no_connection.html')
    
    termo_busca = request.args.get('busca', '')
    
    manager = PacientesManager()
    
    if termo_busca:
        pacientes = manager.buscar_paciente(termo_busca)
    else:
        # Se não há busca, buscar todos (temporário)
        pacientes = manager.buscar_paciente('')
    
    manager.close()
    
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/paciente/<int:paciente_id>')
@require_login
def detalhes_paciente(paciente_id):
    """Detalhes do paciente"""
    if not DB_AVAILABLE:
        return render_template('no_connection.html')
    
    manager = PacientesManager()
    
    # Buscar dados do paciente
    paciente = manager.buscar_paciente_por_id(paciente_id)
    
    if not paciente:
        flash('Paciente não encontrado!', 'error')
        return redirect(url_for('listar_pacientes'))
    
    # Buscar consultas
    consultas = manager.buscar_consultas_paciente(paciente_id)
    exames = manager.buscar_exames_paciente(paciente_id)
    bioimpedancia = manager.buscar_bioimpedancia_paciente(paciente_id)
    
    manager.close()
    
    return render_template('paciente_detalhes.html', 
                         paciente=paciente,
                         consultas=consultas,
                         exames=exames,
                         bioimpedancia=bioimpedancia)

@app.route('/paciente/novo', methods=['GET', 'POST'])
@require_login
def novo_paciente():
    """Adicionar novo paciente"""
    if not DB_AVAILABLE:
        return render_template('no_connection.html')
    
    if request.method == 'POST':
        dados = {
            'nome': request.form.get('nome'),
            'cpf': request.form.get('cpf'),
            'telefone': request.form.get('telefone'),
            'email': request.form.get('email'),
            'data_nascimento': request.form.get('data_nascimento'),
            'endereco': request.form.get('endereco'),
            'convenio': request.form.get('convenio', 'Particular')
        }
        
        manager = PacientesManager()
        paciente_id = manager.adicionar_paciente(dados)
        manager.close()
        
        if paciente_id:
            flash('Paciente adicionado com sucesso!', 'success')
            return redirect(url_for('detalhes_paciente', paciente_id=paciente_id))
        else:
            flash('Erro ao adicionar paciente!', 'error')
    
    return render_template('paciente_form.html')

@app.route('/consulta/nova/<int:paciente_id>', methods=['GET', 'POST'])
@require_login
def nova_consulta(paciente_id):
    """Adicionar nova consulta"""
    if not DB_AVAILABLE:
        return render_template('no_connection.html')
    
    if request.method == 'POST':
        dados = {
            'paciente_id': paciente_id,
            'data_consulta': request.form.get('data_consulta', datetime.now().date()),
            'motivo': request.form.get('motivo'),
            'observacoes': request.form.get('observacoes')
        }
        
        manager = PacientesManager()
        consulta_id = manager.adicionar_consulta(dados)
        manager.close()
        
        if consulta_id:
            flash('Consulta adicionada com sucesso!', 'success')
            return redirect(url_for('detalhes_paciente', paciente_id=paciente_id))
        else:
            flash('Erro ao adicionar consulta!', 'error')
    
    return render_template('consulta_form.html', paciente_id=paciente_id)

# =================== API ===================

@app.route('/api/status')
def api_status():
    """Status da API"""
    return jsonify({
        'database_available': DB_AVAILABLE,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/stats')
@require_login
def api_stats():
    """Estatísticas gerais"""
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database unavailable'}), 503
    
    manager = PacientesManager()
    stats = manager.get_stats()
    manager.close()
    
    return jsonify(stats)

@app.route('/api/search')
@require_login
def api_search():
    """Busca de pacientes"""
    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify([])
    
    manager = PacientesManager()
    pacientes = manager.buscar_paciente(termo)
    manager.close()
    
    return jsonify(pacientes)

# =================== INICIALIZAÇÃO ===================

if __name__ == '__main__':
    print("🌐 Iniciando servidor web local...")
    print(f"📊 Database disponível: {DB_AVAILABLE}")
    print("🔑 Login: drfelipe / Senha: clinica2026")
    app.run(host='0.0.0.0', port=5000, debug=False)
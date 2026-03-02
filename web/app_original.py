#!/usr/bin/env python3
"""
API Web para Sistema de Pacientes - Dr. Felipe
Backend completo com interface web responsiva
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime, date, timedelta
import hashlib
from functools import wraps

# Adiciona o diretório scripts ao path
sys.path.append('/root/clawd/scripts')

try:
    # Usar o adaptador web específico
    from web_db_adapter import PacientesManager, RelatoriosClinico
    DB_AVAILABLE = True
    print("✅ Usando PostgreSQL local via adaptador web")
except Exception as e:
    print(f"⚠️ Banco indisponível: {e}")
    DB_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.secret_key = 'dr_felipe_clinica_2026_secure_key_change_in_production'

# Configurações
ADMIN_USER = 'drfelipe'
ADMIN_PASSWORD_HASH = hashlib.sha256('clinica2026'.encode()).hexdigest()  # Senha: clinica2026

def require_login(f):
    """Decorator para exigir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """Inicializa conexão com banco se disponível"""
    if DB_AVAILABLE:
        try:
            manager = PacientesManager()
            relatorios = RelatoriosClinico()
            return manager, relatorios
        except:
            return None, None
    return None, None

# =================== ROTAS DE AUTENTICAÇÃO ===================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == ADMIN_USER and password_hash == ADMIN_PASSWORD_HASH:
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
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

# =================== ROTAS PRINCIPAIS ===================

@app.route('/')
@require_login
def dashboard():
    """Dashboard principal"""
    manager, relatorios = init_db()
    
    if not manager:
        return render_template('no_connection.html')
    
    # Estatísticas básicas
    try:
        stats = manager.get_stats()
        # Adicionar campos faltantes se necessário
        if 'total_exames' not in stats:
            stats['total_exames'] = 0
        if 'total_bioimpedancia' not in stats:
            stats['total_bioimpedancia'] = 0
        if 'pacientes_recentes' not in stats:
            stats['pacientes_recentes'] = 0
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        stats = {
            'total_pacientes': 0,
            'total_exames': 0,
            'total_bioimpedancia': 0,
            'pacientes_recentes': 0
        }
    
    finally:
        manager.close()
    
    return render_template('dashboard.html', stats=stats)

@app.route('/pacientes')
@require_login
def listar_pacientes():
    """Lista todos os pacientes"""
    manager, _ = init_db()
    
    if not manager:
        return render_template('no_connection.html')
    
    try:
        # Busca com paginação
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        sql = """
        SELECT id, nome, cpf, telefone, email, created_at
        FROM pacientes 
        ORDER BY nome 
        LIMIT %s OFFSET %s;
        """
        
        manager.cursor.execute(sql, (per_page, offset))
        pacientes = manager.cursor.fetchall()
        
        # Total para paginação
        manager.cursor.execute("SELECT COUNT(*) FROM pacientes;")
        total = manager.cursor.fetchone()[0]
        
        pacientes_list = []
        for p in pacientes:
            pacientes_list.append({
                'id': p[0],
                'nome': p[1],
                'cpf': p[2],
                'telefone': p[3],
                'email': p[4],
                'created_at': p[5].strftime('%d/%m/%Y') if p[5] else ''
            })
        
    except Exception as e:
        print(f"Erro ao listar pacientes: {e}")
        pacientes_list = []
        total = 0
    
    finally:
        manager.close()
    
    return render_template('pacientes.html', 
                         pacientes=pacientes_list, 
                         page=page, 
                         total=total, 
                         per_page=per_page)

@app.route('/paciente/<int:paciente_id>')
@require_login
def detalhes_paciente(paciente_id):
    """Detalhes completos do paciente"""
    manager, relatorios = init_db()
    
    if not manager:
        return render_template('no_connection.html')
    
    try:
        # Dados do paciente
        manager.cursor.execute("SELECT * FROM pacientes WHERE id = %s;", (paciente_id,))
        paciente_data = manager.cursor.fetchone()
        
        if not paciente_data:
            flash('Paciente não encontrado!', 'error')
            return redirect(url_for('listar_pacientes'))
        
        paciente = {
            'id': paciente_data[0],
            'nome': paciente_data[1],
            'cpf': paciente_data[2],
            'data_nascimento': paciente_data[3],
            'telefone': paciente_data[4],
            'email': paciente_data[5],
            'endereco': paciente_data[6],
            'observacoes': paciente_data[7]
        }
        
        # Bioimpedância recente
        bioimpedancia = manager.buscar_bioimpedancia_paciente(paciente_id, limite=5)
        
        # Exames recentes
        exames = manager.buscar_exames_paciente(paciente_id)[:10]
        
    except Exception as e:
        print(f"Erro ao buscar paciente: {e}")
        flash('Erro ao carregar dados do paciente!', 'error')
        return redirect(url_for('listar_pacientes'))
    
    finally:
        manager.close()
    
    return render_template('paciente_detalhes.html', 
                         paciente=paciente, 
                         bioimpedancia=bioimpedancia, 
                         exames=exames)

@app.route('/buscar')
@require_login
def buscar():
    """Busca pacientes"""
    termo = request.args.get('q', '')
    
    if not termo:
        return redirect(url_for('listar_pacientes'))
    
    manager, _ = init_db()
    
    if not manager:
        return render_template('no_connection.html')
    
    try:
        pacientes = manager.buscar_paciente(termo)
    except Exception as e:
        print(f"Erro na busca: {e}")
        pacientes = []
    finally:
        manager.close()
    
    return render_template('buscar_resultado.html', 
                         pacientes=pacientes, 
                         termo=termo)

# =================== API ENDPOINTS ===================

@app.route('/api/pacientes')
@require_login
def api_pacientes():
    """API - Lista pacientes"""
    manager, _ = init_db()
    
    if not manager:
        return jsonify({'error': 'Banco indisponível'}), 503
    
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        sql = """
        SELECT id, nome, cpf, telefone 
        FROM pacientes 
        ORDER BY nome 
        LIMIT %s OFFSET %s;
        """
        
        manager.cursor.execute(sql, (limit, offset))
        results = manager.cursor.fetchall()
        
        pacientes = []
        for p in results:
            pacientes.append({
                'id': p[0],
                'nome': p[1],
                'cpf': p[2],
                'telefone': p[3]
            })
        
        return jsonify({
            'success': True,
            'data': pacientes,
            'total': len(pacientes)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        manager.close()

@app.route('/api/paciente/<int:paciente_id>/bioimpedancia')
@require_login
def api_bioimpedancia(paciente_id):
    """API - Bioimpedância do paciente"""
    manager, _ = init_db()
    
    if not manager:
        return jsonify({'error': 'Banco indisponível'}), 503
    
    try:
        bioimpedancia = manager.buscar_bioimpedancia_paciente(paciente_id, limite=20)
        
        # Converte datas para string
        for b in bioimpedancia:
            if b['data_medicao']:
                b['data_medicao'] = b['data_medicao'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'data': bioimpedancia
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        manager.close()

@app.route('/api/status')
def api_status():
    """API - Status do sistema"""
    manager, _ = init_db()
    
    return jsonify({
        'database_available': manager is not None,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# =================== FUNÇÃO PRINCIPAL ===================

if __name__ == '__main__':
    # Cria diretório para templates se não existir
    os.makedirs('/root/clawd/web/templates', exist_ok=True)
    os.makedirs('/root/clawd/web/static', exist_ok=True)
    
    print("🚀 Iniciando servidor web...")
    print(f"📊 Database disponível: {DB_AVAILABLE}")
    print("🌐 Acesse: http://localhost:5000")
    print("👤 Login: drfelipe / Senha: clinica2026")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
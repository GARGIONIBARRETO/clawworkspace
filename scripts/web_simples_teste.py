#!/usr/bin/env python3
"""
Interface Web SIMPLES para testar - Clínica Dr. Felipe
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os

sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

app = Flask(__name__)
app.secret_key = 'teste_clinica'

# Template básico inline
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Clínica Dr. Felipe - TESTE</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-primary">🏥 Clínica Dr. Felipe</h1>
        <p class="text-success">✅ Sistema funcionando corretamente!</p>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>📊 Estatísticas</h5>
                        <p>Pacientes: {{ stats.pacientes }}</p>
                        <p>Consultas: {{ stats.consultas }}</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>🔍 Buscar Paciente</h5>
                        <form method="POST" action="/buscar">
                            <div class="mb-3">
                                <input type="text" name="busca" class="form-control" placeholder="Nome do paciente">
                            </div>
                            <button type="submit" class="btn btn-primary">Buscar</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        {% if pacientes %}
        <div class="mt-4">
            <h3>👥 Pacientes Encontrados</h3>
            <div class="list-group">
                {% for p in pacientes %}
                <div class="list-group-item">
                    <strong>{{ p.nome }}</strong><br>
                    CPF: {{ p.cpf or 'N/A' }} | Telefone: {{ p.telefone or 'N/A' }}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        db = PostgreSQLLocal()
        stats = db.get_stats()
        db.close()
        return render_template_string(TEMPLATE, stats=stats)
    except Exception as e:
        return f"❌ Erro: {str(e)}"

@app.route('/buscar', methods=['POST'])
def buscar():
    try:
        busca = request.form.get('busca', '')
        db = PostgreSQLLocal()
        stats = db.get_stats()
        
        if busca:
            db.cursor.execute("""
                SELECT id, nome, cpf, telefone 
                FROM pacientes 
                WHERE LOWER(nome) LIKE LOWER(%s) 
                LIMIT 10
            """, (f'%{busca}%',))
            
            pacientes = []
            for row in db.cursor.fetchall():
                pacientes.append({
                    'id': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                    'telefone': row[3]
                })
        else:
            pacientes = []
            
        db.close()
        return render_template_string(TEMPLATE, stats=stats, pacientes=pacientes)
    except Exception as e:
        return f"❌ Erro na busca: {str(e)}"

if __name__ == '__main__':
    print("🌐 Interface SIMPLES funcionando!")
    print("🌐 Acesse: http://129.121.33.120:6000")
    app.run(host='0.0.0.0', port=6000, debug=True)
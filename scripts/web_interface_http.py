#!/usr/bin/env python3
"""
Versão HTTP simples para teste
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
import sys
import os

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
    """Página principal - Dashboard simplificado"""
    return "<h1>Sistema Clínica Online</h1><p>HTTP funcionando na porta 5000</p><a href='/pacientes'>Ver Pacientes</a>"

@app.route('/pacientes')
def pacientes():
    """Lista de pacientes simplificada"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("SELECT id, nome FROM pacientes LIMIT 10")
        pacientes = db.cursor.fetchall()
        
        html = "<h1>Pacientes</h1><ul>"
        for p in pacientes:
            html += f"<li>{p[1]} (ID: {p[0]})</li>"
        html += "</ul><a href='/'>Voltar</a>"
        
        return html
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == '__main__':
    print("🚀 Teste HTTP - Porta 5000")
    print("🌐 Acesse: http://129.121.33.120:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
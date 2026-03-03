#!/usr/bin/env python3
"""
Script para iniciar a interface web na porta 8080 (mais comum)
"""

import os
import sys

# Adicionar imports do Flask
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
import pandas as pd
from datetime import datetime
import json

sys.path.append('/root/clawd/scripts')
from db_local_adapter import PostgreSQLLocal

app = Flask(__name__, template_folder='/root/clawd/templates', static_folder='/root/clawd/static')
app.secret_key = 'clinica_dr_felipe_2026'

# Importar todas as rotas do web_interface.py original
exec(open('/root/clawd/scripts/web_interface.py').read())

if __name__ == '__main__':
    print("🚀 Interface Web da Clínica - Porta 8080")
    print("🌐 HTTP: http://129.121.33.120:8080")
    print("💡 Para parar: Ctrl+C")
    
    # Abrir porta no firewall
    os.system('sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT 2>/dev/null')
    
    # Rodar em HTTP na porta 8080
    app.run(host='0.0.0.0', port=8080, debug=False)
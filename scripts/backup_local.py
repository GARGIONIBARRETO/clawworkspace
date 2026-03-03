#!/usr/bin/env python3
"""
Sistema de backup local do banco PostgreSQL
"""

import os
import subprocess
from datetime import datetime

def criar_backup():
    """Cria backup do banco de dados local"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "/root/clawd/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_file = f"{backup_dir}/clinica_backup_{timestamp}.sql"
    
    try:
        # Comando de backup
        cmd = [
            'pg_dump',
            '-h', 'localhost',
            '-U', 'clinica_admin',
            '-d', 'clinica_dr_felipe',
            '-f', backup_file
        ]
        
        # Executar com senha via ambiente
        env = os.environ.copy()
        env['PGPASSWORD'] = 'clinica2026!'
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Comprimir o backup
            subprocess.run(['gzip', backup_file])
            print(f"✅ Backup criado: {backup_file}.gz")
            
            # Limpar backups antigos (manter últimos 7)
            limpar_backups_antigos(backup_dir)
            
            return True
        else:
            print(f"❌ Erro no backup: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def limpar_backups_antigos(backup_dir, manter=7):
    """Mantém apenas os últimos N backups"""
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.gz')])
    
    if len(backups) > manter:
        for backup in backups[:-manter]:
            os.remove(os.path.join(backup_dir, backup))
            print(f"🗑️ Removido backup antigo: {backup}")

if __name__ == "__main__":
    print("🔄 Iniciando backup do banco de dados...")
    criar_backup()
#!/usr/bin/env python3
"""
Script de backup automatizado para GitHub
- Backup do PostgreSQL local
- Commit e push das mudanças para GitHub
- Limpeza de backups antigos
"""

import os
import subprocess
import datetime
import glob
from pathlib import Path

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def backup_postgresql():
    """Faz backup do PostgreSQL local"""
    print("🔄 Fazendo backup do PostgreSQL...")
    
    # Usa o script de backup que já funciona
    success, stdout, stderr = run_command("python3 /root/clawd/scripts/backup_local.py")
    
    if success:
        # Extrai o nome do arquivo do output
        lines = stdout.split('\n')
        for line in lines:
            if 'Backup criado:' in line:
                backup_file = line.split(': ')[-1]
                print(f"✅ Backup criado: {backup_file}")
                return backup_file
        print("✅ Backup executado com sucesso")
        return "backup_ok"
    else:
        print(f"❌ Erro no backup: {stderr}")
        return None

def cleanup_old_backups():
    """Remove backups antigos, mantém apenas os 5 mais recentes"""
    print("🧹 Limpando backups antigos...")
    
    backup_files = glob.glob("/root/clawd/backups/clinica_backup_*.sql.gz")
    backup_files.sort(reverse=True)  # Mais recentes primeiro
    
    if len(backup_files) > 5:
        for old_backup in backup_files[5:]:
            try:
                os.remove(old_backup)
                print(f"🗑️ Removido: {os.path.basename(old_backup)}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {old_backup}: {e}")

def git_backup():
    """Faz commit e push das mudanças para GitHub"""
    print("📤 Fazendo backup para GitHub...")
    
    workspace_dir = "/root/clawd"
    
    # Adiciona arquivos importantes (exclui backups .gz que são muito grandes)
    important_files = [
        "*.md",
        "scripts/*.py", 
        "templates/",
        "memory/",
        ".gitignore"
    ]
    
    # Git add dos arquivos importantes
    for pattern in important_files:
        run_command(f"git add {pattern}", cwd=workspace_dir)
    
    # Verifica se há mudanças para commit
    success, stdout, stderr = run_command("git diff --cached --quiet", cwd=workspace_dir)
    
    if not success:  # Há mudanças para commit
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Auto-backup: {timestamp}"
        
        # Commit
        success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"', cwd=workspace_dir)
        
        if success:
            print(f"✅ Commit criado: {commit_msg}")
            
            # Push para GitHub
            success, stdout, stderr = run_command("git push origin master", cwd=workspace_dir)
            
            if success:
                print("✅ Push realizado com sucesso para GitHub")
            else:
                print(f"❌ Erro no push: {stderr}")
        else:
            print(f"❌ Erro no commit: {stderr}")
    else:
        print("ℹ️ Nenhuma mudança para commit")

def main():
    """Função principal do backup"""
    print("🚀 INICIANDO BACKUP AUTOMATIZADO")
    print("=" * 50)
    
    # 1. Backup do PostgreSQL
    backup_file = backup_postgresql()
    
    # 2. Backup para GitHub
    git_backup()
    
    # 3. Limpeza de backups antigos
    cleanup_old_backups()
    
    print("=" * 50)
    print("✅ BACKUP CONCLUÍDO")
    
    return backup_file is not None

if __name__ == "__main__":
    main()
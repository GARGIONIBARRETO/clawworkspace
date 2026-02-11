#!/usr/bin/env python3
"""
Sistema de Autenticação 2FA - Clínica Dr. Felipe Barreto
"""

import os
import json
import hashlib
import secrets
import pyotp
import qrcode
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
AUTH_FILE = BASE_DIR / '.auth_config.json'
SESSIONS_FILE = BASE_DIR / '.sessions.json'

# Configuração padrão
DEFAULT_CONFIG = {
    "users": {},
    "2fa_enabled": True,
    "session_duration_hours": 8,
    "max_failed_attempts": 5,
    "lockout_minutes": 30
}


def _load_config():
    if AUTH_FILE.exists():
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def _save_config(config):
    with open(AUTH_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(AUTH_FILE, 0o600)  # Apenas root pode ler


def _hash_password(password: str, salt: str = None) -> tuple:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def setup_user(username: str, password: str) -> dict:
    """Configura um novo usuário com 2FA"""
    config = _load_config()
    
    # Hash da senha
    hashed_pw, salt = _hash_password(password)
    
    # Gera secret TOTP
    totp_secret = pyotp.random_base32()
    
    config['users'][username] = {
        'password_hash': hashed_pw,
        'salt': salt,
        'totp_secret': totp_secret,
        '2fa_verified': False,
        'failed_attempts': 0,
        'locked_until': None,
        'created_at': datetime.now().isoformat()
    }
    
    _save_config(config)
    
    # Gera QR code para Google Authenticator
    totp = pyotp.TOTP(totp_secret)
    uri = totp.provisioning_uri(name=username, issuer_name="Clinica Dr Felipe Barreto")
    
    qr_path = BASE_DIR / f'.2fa_setup_{username}.png'
    qr = qrcode.make(uri)
    qr.save(str(qr_path))
    os.chmod(qr_path, 0o600)
    
    print(f"✅ Usuário '{username}' criado!")
    print(f"📱 QR Code salvo em: {qr_path}")
    print(f"🔑 Secret (backup): {totp_secret}")
    
    return {
        'username': username,
        'qr_path': str(qr_path),
        'secret': totp_secret,
        'uri': uri
    }


def verify_2fa_setup(username: str, code: str) -> bool:
    """Verifica o código 2FA para completar setup"""
    config = _load_config()
    
    if username not in config['users']:
        return False
    
    user = config['users'][username]
    totp = pyotp.TOTP(user['totp_secret'])
    
    if totp.verify(code):
        config['users'][username]['2fa_verified'] = True
        _save_config(config)
        print(f"✅ 2FA verificado para '{username}'!")
        return True
    
    print("❌ Código inválido")
    return False


def authenticate(username: str, password: str, totp_code: str = None) -> dict:
    """Autentica usuário com senha + 2FA"""
    config = _load_config()
    
    if username not in config['users']:
        return {'success': False, 'error': 'Usuário não encontrado'}
    
    user = config['users'][username]
    
    # Verifica lockout
    if user.get('locked_until'):
        locked_until = datetime.fromisoformat(user['locked_until'])
        if datetime.now() < locked_until:
            remaining = (locked_until - datetime.now()).seconds // 60
            return {'success': False, 'error': f'Conta bloqueada. Tente em {remaining} minutos.'}
        else:
            # Reset lockout
            config['users'][username]['locked_until'] = None
            config['users'][username]['failed_attempts'] = 0
    
    # Verifica senha
    hashed, _ = _hash_password(password, user['salt'])
    if hashed != user['password_hash']:
        config['users'][username]['failed_attempts'] += 1
        
        if config['users'][username]['failed_attempts'] >= config['max_failed_attempts']:
            lockout_time = datetime.now() + timedelta(minutes=config['lockout_minutes'])
            config['users'][username]['locked_until'] = lockout_time.isoformat()
            _save_config(config)
            return {'success': False, 'error': 'Muitas tentativas. Conta bloqueada por 30 minutos.'}
        
        _save_config(config)
        remaining = config['max_failed_attempts'] - config['users'][username]['failed_attempts']
        return {'success': False, 'error': f'Senha incorreta. {remaining} tentativas restantes.'}
    
    # Verifica 2FA se habilitado
    if config['2fa_enabled'] and user.get('2fa_verified'):
        if not totp_code:
            return {'success': False, 'error': '2FA obrigatório', 'requires_2fa': True}
        
        totp = pyotp.TOTP(user['totp_secret'])
        if not totp.verify(totp_code):
            return {'success': False, 'error': 'Código 2FA inválido'}
    
    # Sucesso - cria sessão
    config['users'][username]['failed_attempts'] = 0
    _save_config(config)
    
    session_token = secrets.token_urlsafe(32)
    sessions = {}
    if SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, 'r') as f:
            sessions = json.load(f)
    
    sessions[session_token] = {
        'username': username,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=config['session_duration_hours'])).isoformat()
    }
    
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f)
    os.chmod(SESSIONS_FILE, 0o600)
    
    return {
        'success': True,
        'session_token': session_token,
        'expires_in_hours': config['session_duration_hours']
    }


def verify_session(token: str) -> dict:
    """Verifica se uma sessão é válida"""
    if not SESSIONS_FILE.exists():
        return {'valid': False, 'error': 'Sessão não encontrada'}
    
    with open(SESSIONS_FILE, 'r') as f:
        sessions = json.load(f)
    
    if token not in sessions:
        return {'valid': False, 'error': 'Sessão não encontrada'}
    
    session = sessions[token]
    expires_at = datetime.fromisoformat(session['expires_at'])
    
    if datetime.now() > expires_at:
        del sessions[token]
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f)
        return {'valid': False, 'error': 'Sessão expirada'}
    
    return {'valid': True, 'username': session['username']}


def logout(token: str) -> bool:
    """Encerra uma sessão"""
    if not SESSIONS_FILE.exists():
        return False
    
    with open(SESSIONS_FILE, 'r') as f:
        sessions = json.load(f)
    
    if token in sessions:
        del sessions[token]
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f)
        return True
    return False


def get_current_code(username: str) -> str:
    """Obtém código TOTP atual (para debug/admin)"""
    config = _load_config()
    if username in config['users']:
        totp = pyotp.TOTP(config['users'][username]['totp_secret'])
        return totp.now()
    return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Sistema de Autenticação 2FA")
        print("\nComandos:")
        print("  setup <usuario> <senha>     - Cria usuário com 2FA")
        print("  verify <usuario> <codigo>   - Verifica 2FA no setup")
        print("  login <usuario> <senha> [codigo_2fa]  - Faz login")
        print("  check <token>               - Verifica sessão")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "setup" and len(sys.argv) >= 4:
        setup_user(sys.argv[2], sys.argv[3])
    
    elif cmd == "verify" and len(sys.argv) >= 4:
        verify_2fa_setup(sys.argv[2], sys.argv[3])
    
    elif cmd == "login" and len(sys.argv) >= 4:
        code = sys.argv[4] if len(sys.argv) > 4 else None
        result = authenticate(sys.argv[2], sys.argv[3], code)
        print(json.dumps(result, indent=2))
    
    elif cmd == "check" and len(sys.argv) >= 3:
        result = verify_session(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Comando inválido: {cmd}")

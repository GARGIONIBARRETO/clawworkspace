#!/usr/bin/env python3
"""
Google OAuth2 Authentication for Gmail + Calendar APIs
"""

import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
]

CREDENTIALS_PATH = '/root/.secrets/google_oauth_credentials.json'
TOKEN_PATH = '/root/.secrets/google_token.json'


def get_auth_url():
    """Generate authorization URL for user to visit."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    flow.redirect_uri = 'http://localhost'
    
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url


def exchange_code(auth_code):
    """Exchange authorization code for tokens."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    flow.redirect_uri = 'http://localhost'
    
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    
    # Save tokens
    with open(TOKEN_PATH, 'w') as f:
        f.write(creds.to_json())
    os.chmod(TOKEN_PATH, 0o600)
    
    return {
        'status': 'success',
        'message': 'Tokens salvos com sucesso!',
        'token_path': TOKEN_PATH
    }


def get_credentials():
    """Get valid credentials, refreshing if needed."""
    if not os.path.exists(TOKEN_PATH):
        return None
    
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    
    return creds


def check_status():
    """Check if we have valid credentials."""
    creds = get_credentials()
    if creds and creds.valid:
        return {'status': 'authenticated', 'message': 'Credenciais válidas!'}
    elif creds and creds.expired:
        return {'status': 'expired', 'message': 'Token expirado, tentando renovar...'}
    else:
        return {'status': 'not_authenticated', 'message': 'Não autenticado. Execute: python3 google_auth.py auth'}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 google_auth.py status     - Verificar status")
        print("  python3 google_auth.py auth       - Gerar URL de autorização")
        print("  python3 google_auth.py code CODE  - Trocar código por tokens")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'status':
        result = check_status()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'auth':
        url = get_auth_url()
        print("Abra este link no navegador e autorize:")
        print()
        print(url)
        print()
        print("Depois de autorizar, você será redirecionado para uma página que não carrega.")
        print("Copie o 'code' da URL e execute: python3 google_auth.py code CODIGO")
    
    elif cmd == 'code':
        if len(sys.argv) < 3:
            print("Uso: python3 google_auth.py code CODIGO")
            sys.exit(1)
        code = sys.argv[2]
        result = exchange_code(code)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Comando desconhecido: {cmd}")
        sys.exit(1)

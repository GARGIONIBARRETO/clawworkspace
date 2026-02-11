#!/usr/bin/env python3
"""
Integração Google Calendar - Clínica Dr. Felipe Barreto
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).parent
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = BASE_DIR / 'calendar_token.pickle'
CREDENTIALS_FILE = Path('/root/.secrets/google_calendar_credentials.json')


def get_calendar_service():
    """Obtém serviço autenticado do Google Calendar"""
    creds = None
    
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"❌ Arquivo de credenciais não encontrado: {CREDENTIALS_FILE}")
                print("\nPara configurar:")
                print("1. Vá em https://console.cloud.google.com/apis/credentials")
                print("2. Crie credenciais OAuth 2.0 (Desktop app)")
                print("3. Baixe o JSON e salve em:", CREDENTIALS_FILE)
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)


def listar_eventos(dias_futuros: int = 7) -> list:
    """Lista eventos dos próximos dias"""
    service = get_calendar_service()
    if not service:
        return []
    
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=dias_futuros)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    eventos = []
    for event in events_result.get('items', []):
        start = event['start'].get('dateTime', event['start'].get('date'))
        eventos.append({
            'id': event['id'],
            'titulo': event.get('summary', 'Sem título'),
            'inicio': start,
            'local': event.get('location', ''),
            'descricao': event.get('description', ''),
            'participantes': [a.get('email') for a in event.get('attendees', [])]
        })
    
    return eventos


def consultas_amanha() -> list:
    """Retorna consultas agendadas para amanhã"""
    eventos = listar_eventos(dias_futuros=2)
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    consultas = []
    for e in eventos:
        data_evento = e['inicio'][:10] if e['inicio'] else ''
        if data_evento == amanha:
            consultas.append(e)
    
    return consultas


def extrair_telefone_evento(evento: dict) -> str:
    """Tenta extrair telefone da descrição ou participantes do evento"""
    descricao = evento.get('descricao', '')
    
    # Procura padrões de telefone na descrição
    import re
    telefones = re.findall(r'(?:\+?55)?[\s-]?\(?(\d{2})\)?[\s-]?(\d{4,5})[\s-]?(\d{4})', descricao)
    if telefones:
        return '55' + ''.join(telefones[0])
    
    return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python calendar_integration.py <comando>")
        print("\nComandos:")
        print("  eventos [dias]  - Lista eventos")
        print("  amanha          - Consultas de amanhã")
        print("  auth            - Autenticar com Google")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "eventos":
        dias = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        for e in listar_eventos(dias):
            print(f"📅 {e['inicio']} - {e['titulo']}")
    
    elif cmd == "amanha":
        for e in consultas_amanha():
            print(f"📅 {e['inicio']} - {e['titulo']}")
    
    elif cmd == "auth":
        service = get_calendar_service()
        if service:
            print("✅ Autenticado com sucesso!")

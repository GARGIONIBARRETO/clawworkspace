#!/usr/bin/env python3
"""
Google Calendar API - Ver e gerenciar eventos
"""

import os
import sys
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
]
TOKEN_PATH = '/root/.secrets/google_token.json'


def get_credentials():
    """Get valid credentials."""
    if not os.path.exists(TOKEN_PATH):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_service():
    """Get Calendar API service."""
    creds = get_credentials()
    if not creds:
        raise Exception("Não autenticado. Execute google_auth.py primeiro.")
    return build('calendar', 'v3', credentials=creds)


def list_calendars():
    """List all calendars."""
    service = get_service()
    result = service.calendarList().list().execute()
    calendars = result.get('items', [])
    return [{'id': c['id'], 'name': c.get('summary', 'Sem nome'), 'primary': c.get('primary', False)} for c in calendars]


def get_events(calendar_id='primary', days=7, max_results=20):
    """Get upcoming events."""
    service = get_service()
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
    
    result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        timeMax=end,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = result.get('items', [])
    return [{
        'id': e['id'],
        'summary': e.get('summary', 'Sem título'),
        'start': e['start'].get('dateTime', e['start'].get('date')),
        'end': e['end'].get('dateTime', e['end'].get('date')),
        'location': e.get('location', ''),
        'description': e.get('description', ''),
        'attendees': [a.get('email') for a in e.get('attendees', [])]
    } for e in events]


def create_event(summary, start_time, end_time, description='', location='', attendees=None, calendar_id='primary'):
    """Create a new event."""
    service = get_service()
    
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': end_time, 'timeZone': 'America/Sao_Paulo'},
    }
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    result = service.events().insert(calendarId=calendar_id, body=event).execute()
    return {'status': 'success', 'event_id': result['id'], 'link': result.get('htmlLink')}


def delete_event(event_id, calendar_id='primary'):
    """Delete an event."""
    service = get_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return {'status': 'success', 'message': f'Evento {event_id} deletado'}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 google_calendar.py calendars              - Listar calendários")
        print("  python3 google_calendar.py events [dias]          - Ver eventos")
        print("  python3 google_calendar.py create 'titulo' 'inicio' 'fim' ['desc'] ['local']")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'calendars':
        result = list_calendars()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == 'events':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        result = get_events(days=days)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == 'create':
        if len(sys.argv) < 5:
            print("Uso: python3 google_calendar.py create 'titulo' '2024-01-15T10:00:00' '2024-01-15T11:00:00'")
            sys.exit(1)
        result = create_event(
            summary=sys.argv[2],
            start_time=sys.argv[3],
            end_time=sys.argv[4],
            description=sys.argv[5] if len(sys.argv) > 5 else '',
            location=sys.argv[6] if len(sys.argv) > 6 else ''
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Comando desconhecido: {cmd}")

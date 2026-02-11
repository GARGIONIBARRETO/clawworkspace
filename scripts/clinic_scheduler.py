#!/usr/bin/env python3
"""
Clínica da Coluna - Sistema de Agendamento
Dr. Felipe Barreto - Neurocirurgia de Coluna

Horários: Ter/Qua/Qui, 9h-18h, consultas de 90min
"""

import os
import sys
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

TOKEN_PATH = '/root/.secrets/google_token.json'
CALENDAR_ID = 'clinicadacolunadrfelipebarreto@gmail.com'

# Configuração da clínica
CLINIC_CONFIG = {
    'days': [1, 2, 3],  # Terça=1, Quarta=2, Quinta=3 (weekday())
    'start_hour': 9,
    'end_hour': 18,
    'slot_duration': 90,  # minutos
    'timezone': 'America/Sao_Paulo'
}

# Slots fixos do dia
SLOTS = ['09:00', '10:30', '12:00', '13:30', '15:00', '16:30']


def get_credentials():
    if not os.path.exists(TOKEN_PATH):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_service():
    creds = get_credentials()
    if not creds:
        raise Exception("Não autenticado")
    return build('calendar', 'v3', credentials=creds)


def get_day_name(weekday):
    names = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
    return names.get(weekday, '')


def is_clinic_day(date):
    """Verifica se é dia de atendimento (Ter/Qua/Qui)"""
    return date.weekday() in CLINIC_CONFIG['days']


def get_events_for_day(service, date):
    """Busca eventos de um dia específico"""
    start = datetime(date.year, date.month, date.day, 0, 0, 0)
    end = start + timedelta(days=1)
    
    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + '-03:00',
        timeMax=end.isoformat() + '-03:00',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return result.get('items', [])


def get_available_slots(date):
    """Retorna horários disponíveis para uma data"""
    if not is_clinic_day(date):
        return []
    
    service = get_service()
    events = get_events_for_day(service, date)
    
    # Horários ocupados
    busy_times = set()
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start:
            time_str = start.split('T')[1][:5]
            busy_times.add(time_str)
        else:
            # Evento de dia inteiro = dia bloqueado
            return []
    
    # Retorna slots livres
    available = [s for s in SLOTS if s not in busy_times]
    return available


def get_availability(days_ahead=14):
    """Mostra disponibilidade para os próximos dias"""
    today = datetime.now()
    availability = []
    
    for i in range(days_ahead):
        date = today + timedelta(days=i)
        if is_clinic_day(date):
            slots = get_available_slots(date)
            if slots:
                availability.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'weekday': get_day_name(date.weekday()),
                    'display': date.strftime('%d/%m/%Y'),
                    'slots': slots
                })
    
    return availability


def schedule_appointment(patient_name, date_str, time_str, phone='', email='', notes=''):
    """Agenda uma consulta"""
    # Parse da data
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    if not is_clinic_day(date):
        return {'status': 'error', 'message': f'{get_day_name(date.weekday())} não é dia de atendimento'}
    
    if time_str not in SLOTS:
        return {'status': 'error', 'message': f'Horário {time_str} inválido. Opções: {", ".join(SLOTS)}'}
    
    # Verifica disponibilidade
    available = get_available_slots(date)
    if time_str not in available:
        return {'status': 'error', 'message': f'Horário {time_str} não disponível em {date_str}', 'available': available}
    
    # Cria o evento
    service = get_service()
    
    start_dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
    end_dt = start_dt + timedelta(minutes=90)
    
    description_parts = [f'Paciente: {patient_name}']
    if phone:
        description_parts.append(f'Telefone: {phone}')
    if email:
        description_parts.append(f'Email: {email}')
    if notes:
        description_parts.append(f'Obs: {notes}')
    
    event = {
        'summary': f'Consulta - {patient_name}',
        'description': '\n'.join(description_parts),
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60},
                {'method': 'popup', 'minutes': 10}
            ]
        }
    }
    
    result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    
    return {
        'status': 'success',
        'message': f'Consulta agendada!',
        'patient': patient_name,
        'date': date.strftime('%d/%m/%Y'),
        'weekday': get_day_name(date.weekday()),
        'time': time_str,
        'end_time': end_dt.strftime('%H:%M'),
        'event_id': result['id']
    }


def cancel_appointment(event_id):
    """Cancela uma consulta"""
    service = get_service()
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    return {'status': 'success', 'message': 'Consulta cancelada'}


def list_appointments(days_ahead=7):
    """Lista consultas agendadas"""
    service = get_service()
    today = datetime.now()
    end = today + timedelta(days=days_ahead)
    
    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=today.isoformat() + '-03:00',
        timeMax=end.isoformat() + '-03:00',
        singleEvents=True,
        orderBy='startTime',
        q='Consulta -'
    ).execute()
    
    appointments = []
    for event in result.get('items', []):
        start = event['start'].get('dateTime', '')
        if start and 'Consulta' in event.get('summary', ''):
            dt = datetime.fromisoformat(start.replace('-03:00', ''))
            appointments.append({
                'id': event['id'],
                'patient': event.get('summary', '').replace('Consulta - ', ''),
                'date': dt.strftime('%d/%m/%Y'),
                'weekday': get_day_name(dt.weekday()),
                'time': dt.strftime('%H:%M'),
                'description': event.get('description', '')
            })
    
    return appointments


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 clinic_scheduler.py available [dias]     - Ver horários disponíveis")
        print("  python3 clinic_scheduler.py appointments [dias]  - Ver consultas agendadas")
        print("  python3 clinic_scheduler.py schedule 'nome' 'YYYY-MM-DD' 'HH:MM' ['tel'] ['email'] ['obs']")
        print("  python3 clinic_scheduler.py cancel EVENT_ID      - Cancelar consulta")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'available':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 14
        result = get_availability(days)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == 'appointments':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        result = list_appointments(days)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == 'schedule':
        if len(sys.argv) < 5:
            print("Uso: python3 clinic_scheduler.py schedule 'nome' 'YYYY-MM-DD' 'HH:MM'")
            sys.exit(1)
        result = schedule_appointment(
            patient_name=sys.argv[2],
            date_str=sys.argv[3],
            time_str=sys.argv[4],
            phone=sys.argv[5] if len(sys.argv) > 5 else '',
            email=sys.argv[6] if len(sys.argv) > 6 else '',
            notes=sys.argv[7] if len(sys.argv) > 7 else ''
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == 'cancel':
        if len(sys.argv) < 3:
            print("Uso: python3 clinic_scheduler.py cancel EVENT_ID")
            sys.exit(1)
        result = cancel_appointment(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Comando desconhecido: {cmd}")

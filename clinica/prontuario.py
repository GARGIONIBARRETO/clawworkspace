#!/usr/bin/env python3
"""
Sistema de Prontuário Eletrônico - Clínica Dr. Felipe Barreto
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
PACIENTES_DIR = BASE_DIR / "pacientes"
CONSULTAS_DIR = BASE_DIR / "consultas"
EXAMES_DIR = BASE_DIR / "exames"

# Ensure directories exist
PACIENTES_DIR.mkdir(exist_ok=True)
CONSULTAS_DIR.mkdir(exist_ok=True)
EXAMES_DIR.mkdir(exist_ok=True)


class Prontuario:
    
    # ==================== PACIENTES ====================
    
    @staticmethod
    def criar_paciente(nome: str, telefone: str, **kwargs) -> dict:
        """Cria um novo paciente"""
        paciente = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "telefone": telefone.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""),
            "dataCadastro": datetime.now().isoformat(),
            "status": "ativo",
            **kwargs
        }
        
        filepath = PACIENTES_DIR / f"{paciente['id']}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(paciente, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Paciente criado: {nome} (ID: {paciente['id'][:8]}...)")
        return paciente
    
    @staticmethod
    def buscar_paciente(termo: str) -> list:
        """Busca pacientes por nome ou telefone"""
        resultados = []
        termo_lower = termo.lower()
        
        for filepath in PACIENTES_DIR.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                paciente = json.load(f)
                if termo_lower in paciente.get('nome', '').lower() or \
                   termo in paciente.get('telefone', ''):
                    resultados.append(paciente)
        
        return resultados
    
    @staticmethod
    def obter_paciente(paciente_id: str) -> dict:
        """Obtém paciente por ID"""
        filepath = PACIENTES_DIR / f"{paciente_id}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def atualizar_paciente(paciente_id: str, **kwargs) -> dict:
        """Atualiza dados do paciente"""
        paciente = Prontuario.obter_paciente(paciente_id)
        if not paciente:
            return None
        
        paciente.update(kwargs)
        filepath = PACIENTES_DIR / f"{paciente_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(paciente, f, ensure_ascii=False, indent=2)
        
        return paciente
    
    @staticmethod
    def listar_pacientes() -> list:
        """Lista todos os pacientes"""
        pacientes = []
        for filepath in PACIENTES_DIR.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                pacientes.append(json.load(f))
        return sorted(pacientes, key=lambda x: x.get('nome', ''))
    
    # ==================== CONSULTAS ====================
    
    @staticmethod
    def criar_consulta(paciente_id: str, data: str, tipo: str = "retorno", **kwargs) -> dict:
        """Cria uma nova consulta"""
        paciente = Prontuario.obter_paciente(paciente_id)
        if not paciente:
            print(f"❌ Paciente não encontrado: {paciente_id}")
            return None
        
        consulta = {
            "id": str(uuid.uuid4()),
            "pacienteId": paciente_id,
            "pacienteNome": paciente.get('nome'),
            "data": data,
            "tipo": tipo,
            "status": "agendada",
            "dataCriacao": datetime.now().isoformat(),
            **kwargs
        }
        
        filepath = CONSULTAS_DIR / f"{consulta['id']}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(consulta, f, ensure_ascii=False, indent=2)
        
        # Atualizar próxima consulta do paciente
        Prontuario.atualizar_paciente(paciente_id, proximaConsulta=data)
        
        print(f"✅ Consulta criada para {paciente.get('nome')} em {data}")
        return consulta
    
    @staticmethod
    def obter_consulta(consulta_id: str) -> dict:
        """Obtém consulta por ID"""
        filepath = CONSULTAS_DIR / f"{consulta_id}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def atualizar_consulta(consulta_id: str, **kwargs) -> dict:
        """Atualiza dados da consulta"""
        consulta = Prontuario.obter_consulta(consulta_id)
        if not consulta:
            return None
        
        consulta.update(kwargs)
        filepath = CONSULTAS_DIR / f"{consulta_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(consulta, f, ensure_ascii=False, indent=2)
        
        return consulta
    
    @staticmethod
    def listar_consultas(paciente_id: str = None, status: str = None, data_inicio: str = None) -> list:
        """Lista consultas com filtros opcionais"""
        consultas = []
        for filepath in CONSULTAS_DIR.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                consulta = json.load(f)
                
                if paciente_id and consulta.get('pacienteId') != paciente_id:
                    continue
                if status and consulta.get('status') != status:
                    continue
                if data_inicio and consulta.get('data', '') < data_inicio:
                    continue
                    
                consultas.append(consulta)
        
        return sorted(consultas, key=lambda x: x.get('data', ''))
    
    @staticmethod
    def consultas_pendentes_confirmacao() -> list:
        """Lista consultas que precisam de confirmação via WhatsApp"""
        from datetime import datetime, timedelta
        
        amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        consultas = Prontuario.listar_consultas(status='agendada')
        
        pendentes = []
        for c in consultas:
            data_consulta = c.get('data', '')[:10]
            confirmacao = c.get('confirmacaoWhatsApp', {})
            
            # Se a consulta é amanhã e não foi enviada confirmação
            if data_consulta == amanha and not confirmacao.get('enviada'):
                pendentes.append(c)
        
        return pendentes
    
    # ==================== EXAMES ====================
    
    @staticmethod
    def registrar_exame(paciente_id: str, tipo: str, arquivo: str = None, resultados: dict = None) -> dict:
        """Registra um exame para o paciente"""
        paciente = Prontuario.obter_paciente(paciente_id)
        if not paciente:
            return None
        
        exame = {
            "id": str(uuid.uuid4()),
            "pacienteId": paciente_id,
            "tipo": tipo,
            "dataRegistro": datetime.now().isoformat(),
            "arquivo": arquivo,
            "resultados": resultados or {}
        }
        
        filepath = EXAMES_DIR / f"{exame['id']}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(exame, f, ensure_ascii=False, indent=2)
        
        return exame
    
    @staticmethod
    def listar_exames(paciente_id: str) -> list:
        """Lista exames de um paciente"""
        exames = []
        for filepath in EXAMES_DIR.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                exame = json.load(f)
                if exame.get('pacienteId') == paciente_id:
                    exames.append(exame)
        
        return sorted(exames, key=lambda x: x.get('dataRegistro', ''), reverse=True)
    
    @staticmethod
    def comparar_exames(paciente_id: str, tipo: str) -> list:
        """Compara exames do mesmo tipo ao longo do tempo"""
        exames = Prontuario.listar_exames(paciente_id)
        return [e for e in exames if e.get('tipo') == tipo]


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python prontuario.py <comando> [args]")
        print("\nComandos:")
        print("  criar_paciente <nome> <telefone>")
        print("  buscar <termo>")
        print("  listar_pacientes")
        print("  criar_consulta <paciente_id> <data> [tipo]")
        print("  listar_consultas [paciente_id]")
        print("  pendentes")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "criar_paciente" and len(sys.argv) >= 4:
        Prontuario.criar_paciente(sys.argv[2], sys.argv[3])
    
    elif cmd == "buscar" and len(sys.argv) >= 3:
        resultados = Prontuario.buscar_paciente(sys.argv[2])
        for p in resultados:
            print(f"- {p['nome']} | Tel: {p['telefone']} | ID: {p['id'][:8]}...")
    
    elif cmd == "listar_pacientes":
        for p in Prontuario.listar_pacientes():
            print(f"- {p['nome']} | Tel: {p['telefone']}")
    
    elif cmd == "criar_consulta" and len(sys.argv) >= 4:
        tipo = sys.argv[4] if len(sys.argv) > 4 else "retorno"
        Prontuario.criar_consulta(sys.argv[2], sys.argv[3], tipo)
    
    elif cmd == "listar_consultas":
        paciente_id = sys.argv[2] if len(sys.argv) > 2 else None
        for c in Prontuario.listar_consultas(paciente_id=paciente_id):
            print(f"- {c['data']} | {c['pacienteNome']} | {c['status']}")
    
    elif cmd == "pendentes":
        for c in Prontuario.consultas_pendentes_confirmacao():
            print(f"- {c['data']} | {c['pacienteNome']}")
    
    else:
        print(f"Comando desconhecido: {cmd}")

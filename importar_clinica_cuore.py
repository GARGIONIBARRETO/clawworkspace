#!/usr/bin/env python3
"""
Importador de pacientes da CLINICA CUORE
Processa lista de pacientes com prontuários detalhados
"""

import psycopg2
from datetime import datetime, date
import re

def conectar_db():
    """Conecta ao PostgreSQL local"""
    return psycopg2.connect(
        dbname="clinica_dr_felipe",
        user="clinica_admin",
        password="clinica2026!",
        host="localhost",
        port="5432"
    )

def extrair_idade(texto):
    """Extrai idade do texto"""
    match = re.search(r'(\d+)\s*anos', texto)
    if match:
        idade = int(match.group(1))
        # Calcular data aproximada de nascimento
        ano_nascimento = 2026 - idade
        return f"{ano_nascimento}-01-01"
    return "1970-01-01"

def deduzir_sexo(nome):
    """Deduz sexo baseado no nome"""
    nome_lower = nome.lower()
    nomes_femininos = ['maria', 'ana', 'claudia', 'fernanda', 'patricia', 'sonia', 
                       'bianca', 'debora', 'daniela', 'jessica', 'gislaine', 'lilian',
                       'renata', 'monique', 'karina', 'leonice', 'vanderlene', 'leila',
                       'gilmelia', 'vivian', 'antonia', 'rafaella', 'marta']
    
    for nome_fem in nomes_femininos:
        if nome_fem in nome_lower:
            return 'F'
    
    # Se termina com 'a' provavelmente é feminino
    if nome.strip().endswith('a'):
        return 'F'
    
    return 'M'

def processar_pacientes_cuore():
    """Processa e importa pacientes da CLINICA CUORE"""
    
    # Dados dos pacientes
    pacientes_texto = """
Marta Martins da Silva, 56 anos, CNU CERVIBRAQUIALGIA HÁ 30 DIAS RELATA AINDA PIORA DA FORÇA EM MSE HIPOSENSIBILIDADE C6 FORCA G4 MENOS TRICEPS E BICEPS. HOFFMANN NEGATIVO RM: Hernia c5-7 Cd: artrodese C5-7

Monique Pereira Lins, 27 anos Dor lombar e irradiação para MIE RM espondilolise e hernia L5-s1 esquerda. Cd: bloqueio

Fabio, 50 anos, Logística Dormência em perna direita, piora há 1 ano, melhora ao caminhar e correr, piora fica em pé. Dor lombar crönica Piora ao ficar muito tempo sentado. Histórico de Hérnia Discal. Solicito RM e exames de sangue (histórico de pre diabetes)

Renata Cristina Rosa, Dor cervical há 2 meses (10/25) com irradiacao para MSD Melhorou do braço, mantem dor cervical e limtiacao para trabalho (tecnica enfermagem) Neurologico normal RM: hernia C5-6 direita sem compressão medular Plano: bloqueio cervical

Bianca Cardacci, 37 anos, enfermeira Dor lombar paravertebral esquerda Tem artrite reumatoide Em uso de pregabalina 75mg 12/12h Hipotireoidismo puran 50mg Contrave (bupropiona + naltrexona) Cd: RM Lombar

Cláudio Marcio Rodrigues da Silva, 54 anos Lombociatalgia direita há 2 anos Parestesias em ambos os pés Em uso de forxiga (dapaglifozina) RM: listese l4-5 Cd: rx dinâmico + nova RM

Lilian Almeida de Morais, 58 anos, Gerente de Vendas. Parestesias em mãos e pés Diabética Melhorou de dor lombar após bloqueio Plano: Nova RM Controlede diabetes ALA 600mg (Thioctacid 600mg)

Carlos Alberto de Araújo, 54 anos, analista Dor cervical e lombar com irradiação para coxa esquerda, pior há 2 semanas, inicio há 30 dias Ao Exame Força g4- a esquerda para extensão coxa e perna Sem desvios posturais Plano: RM lombar e cervical Avaliação com Oseopata Diprospan

Ricardo Feres, 74 anos, Lombociatalgia esquerda intermitente há 1 ano Stent em 2012 MUC: AAS 100MG CONCOR 5MG (BISOPROLOL) EZETIMIBA Cd: Rx panorâmico, retorno com RM para indicar bloqueio

Fernada Ferreira, 30 anos, Já vai operar.. e viajar..

Rogério de Deus, 50 anos, Trabalha com Mercado. Fez bloqueio e melhorou Está com coccidinea Solicito osteopata e bloqueio anestésico.

Leonice Carvalho, 68 anos Vem para avaliação de atividade física Em uso de whey, cálcio e vitamina B Indico bioimpedância Pepti Strong E RM

Rafael Aragão, 16 Corcunda e ma postura Cd: rx panorâmico Encaminho p Bruno/ Marilia Retorna com Rx: 22 graus de escoliose toracolombar lenke 5. 41 de cifose Reforço realizar exercícios de fortalecimento. Novo Rx em 1 ano.

Karina Araújo, 46 anos, auxiliar de expedição Discecção de vertebral – displasia fibromuscular Em uso de pradaxa Oriento acompanhar com endovascular

Heitor dos Santos Guedes, 28 anos, TI Lombalgia Pior há 6 meses Irradiação pra perna direita eventual Cd: Rm lombar

Debora Lopes, 42 anos, analista de sistemas Dor lombar mais a esquerda Obesidade Sem irradiação Cd: oriento perda de peso RM lombar para bloqueio

João Rodrigues, 84 anos Dor em quaril esquerdo – fratura com haste prévia e lombar Cd: Rm lombar Formula pra dor articular

Bianca Pereira dos Santos, 38 anos Dor lombar refrataria Esta amamentando Limita uso de medicações RM: sobrecarga Indico bloqueio lombar.

Eduardo Faria Santos, 49 anos Dor lombar refratária RM: artrose facetaria cd: bloqueio lombar

Sonia Maria Ottoboni, 77 anos Varizes/dor lombar/artrose Ostomia Indico nutricionista

Leandro Scarabotto , 37 anos, Cervical + lombar RM cervical com artefato, mas hérnia C5-6 com compressão radícular Ao exame Forca G4 flexao e extensão do braco esquerdo Solicito TC cervical e eletroneuro de MMSS. Bloqueio lombar

Daniela Lopes, 49 anos, Manicure Relata dor lombar e irradiação para membro inferior esquerdo há 7 dias. Trajeto L5 (dorso do pé) Está fazendo uso de estradiol vaginal por ressecamento Perda de cabelo Dores generalizadas Peço perfil laboratorial completo Fórmula pra sono por 30 dias Naproxeno RM lombar

Jessica Santos, 34 anos, do lar Lombalgia há 2 meses após esforço físico RM com pequena protrusão L5-S1. Ferritina: 26 Homocisteina: 12Indico Mana Move + Fórmula com magnésio Ferro EV

Gislaine Rodrigues, 46 anos, técnica enfermagem Dor lombar crônica ARtordese cervial prévia Distúrbio de sono Fibromialgia Cd: Naltrexona 1,5mg a noite aumentado pra 4,5 em 20 dias Trazodona (formula lana) Vagifem pra perda urinária.

Dernivaldo Francisco de Oliveira, 56 anos, Químico Dor lombar eventual Solicito RM

Fernanda Garcia Mariano Voros, 43 anos, auditor Dor lombar Escoliose RM: denegeracao lombar Cd: telespondilografia Exames laboratoriais Solicito bloqueio.

Vanderlene Azevedo, Dor lombar e obesidade Solicito RM

Leila Aparecida dos Santos Roque, 57 anos, dona de colégio Parestesias em MSE, dor lombar Cd: Rm cervical e lombar

Gilmelia Cerqueira, 46 anos, líder de caixa- supermecado (trabalha em pé) Relata dores em membros inferiores. Dor cervical eventual Solicito RM cervical e lombar Formula pra circulação e cúrcuma Labs

Vivian Fabiana Bacchin, 44 anos Dor lombar, piora após queda sentada em novembro Está em menopausa com LH e FSH altos colesterol tb Sono ruim Inicio ômega com q10 por inicio de lipless RM lombar

Aldo Rodrigues da Silva, 47 anos, policial Dor lombar há 4 anos, sem exames recentes Apresenta ainda formigamento nos braços eventualmente Histórico de fratura cervical Sono fragmentado Cd: solicito RM cervical e lombar

Antonia Alzira de Oliveira, 57 anos, aposentada (costureira) Dor lombar refrataria Rm lombar

Patricia conceição verdi, 52 anos, comunicação visual Iniciou travamento de mao esquerda há 20 dias, Dor lombar há 3 meses Cd: RM cervical e lombar

Nilson Vieira, 52 anos, gerente de recursos humanos Parestesia em MSD a extensão de cervical há 3 meses. Parestesia vai até 5 quirodáctilo principalmente Rm com hernia C6-7 pegando raiz c7 Cd: nova RM e rx panorâmico ACDF C6-7?

Rafaella de Oliveira Rodrigues, 12 anos Dor lombar, há 1 ano Sem fator de piora Melhora eventual com dipirona Adams com giba a esquerda Cd: RM lombar, rx panoramico
"""
    
    # Processar cada linha
    linhas = [l.strip() for l in pacientes_texto.strip().split('\n') if l.strip()]
    
    pacientes = []
    
    for linha in linhas:
        # Extrair nome (até a primeira vírgula ou número)
        match_nome = re.match(r'^([^,\d]+)', linha)
        if match_nome:
            nome = match_nome.group(1).strip()
            resto_texto = linha[len(nome):].strip()
            
            # Extrair idade e calcular data de nascimento
            data_nascimento = extrair_idade(resto_texto)
            
            # Todo o resto é o prontuário
            prontuario = resto_texto
            
            # Extrair profissão se houver
            match_prof = re.search(r',\s*([^,]+?)\s*(?:Dor|Relata|Lombo|Cerv|Para|Já)', resto_texto)
            profissao = match_prof.group(1).strip() if match_prof else ""
            
            pacientes.append({
                'nome': nome,
                'data_nascimento': data_nascimento,
                'profissao': profissao,
                'prontuario': prontuario
            })
    
    print(f"🏥 IMPORTADOR CLINICA CUORE - DR. FELIPE")
    print("=" * 60)
    print(f"📋 {len(pacientes)} pacientes encontrados")
    
    conn = conectar_db()
    cur = conn.cursor()
    
    pacientes_novos = 0
    consultas_criadas = 0
    
    for p in pacientes:
        try:
            # Verificar se paciente já existe
            cur.execute("""
                SELECT id FROM pacientes 
                WHERE LOWER(nome) = LOWER(%s)
            """, (p['nome'],))
            
            result = cur.fetchone()
            
            if result:
                paciente_id = result[0]
                print(f"   ✓ {p['nome']} já existe (ID: {paciente_id})")
            else:
                # Criar novo paciente
                cur.execute("""
                    INSERT INTO pacientes (
                        nome, data_nascimento, telefone, email, convenio
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    p['nome'],
                    p['data_nascimento'],
                    '(11) 0000-0000',
                    '',
                    'CLINICA CUORE'
                ))
                
                paciente_id = cur.fetchone()[0]
                pacientes_novos += 1
                print(f"   ✅ Novo: {p['nome']} (ID: {paciente_id})")
            
            # Criar consulta com prontuário
            prontuario_completo = f"PROFISSÃO: {p['profissao']}\n\n{p['prontuario']}" if p['profissao'] else p['prontuario']
            
            cur.execute("""
                INSERT INTO consultas (
                    paciente_id, data_consulta, medico,
                    motivo, observacoes
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                paciente_id,
                date.today(),
                'Dr. Felipe - CLINICA CUORE',
                'Consulta na CLINICA CUORE',
                prontuario_completo
            ))
            
            consulta_id = cur.fetchone()[0]
            consultas_criadas += 1
            
        except Exception as e:
            print(f"   ❌ Erro com {p['nome']}: {str(e)[:60]}")
            conn.rollback()
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMO DA IMPORTAÇÃO:")
    print(f"✅ Novos pacientes: {pacientes_novos}")
    print(f"✅ Consultas criadas: {consultas_criadas}")
    print(f"📁 Total processado: {len(pacientes)} pacientes")

if __name__ == "__main__":
    processar_pacientes_cuore()
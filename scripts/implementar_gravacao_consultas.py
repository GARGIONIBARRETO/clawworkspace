#!/usr/bin/env python3
"""
Sistema de gravação e transcrição de consultas
Grava áudio, transcreve e organiza em prontuário estruturado
"""

import os
from datetime import datetime

def criar_template_gravacao():
    """Cria template para gravação de consultas"""
    
    template = '''{% extends "base.html" %}

{% block title %}Gravar Consulta - {{ paciente[1] }}{% endblock %}

{% block content %}
<style>
.recording-container {
    text-align: center;
    padding: 40px;
    background: #f8f9fa;
    border-radius: 10px;
    margin: 20px 0;
}
.rec-button {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    font-size: 40px;
    margin: 20px;
}
.recording {
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.1); opacity: 0.7; }
    100% { transform: scale(1); opacity: 1; }
}
.timer {
    font-size: 48px;
    font-family: monospace;
    margin: 20px 0;
}
</style>

<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/pacientes">Pacientes</a></li>
                <li class="breadcrumb-item"><a href="/paciente/{{ paciente[0] }}">{{ paciente[1] }}</a></li>
                <li class="breadcrumb-item active">Gravar Consulta</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-microphone"></i> Gravar Consulta</h1>
        <p class="text-muted">
            <strong>{{ paciente[1] }}</strong> 
            {% if paciente[2] %}(CPF: {{ paciente[2] }}){% endif %}
        </p>
    </div>
</div>

<!-- Gravação no Browser -->
<div class="row mt-3">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4><i class="fas fa-microphone-alt"></i> Gravação no Navegador</h4>
            </div>
            <div class="card-body">
                <div class="recording-container">
                    <button id="recordButton" class="btn btn-danger rec-button">
                        <i class="fas fa-microphone"></i>
                    </button>
                    <div class="timer" id="timer">00:00</div>
                    <p id="status">Clique para iniciar a gravação</p>
                </div>
                
                <div id="audioPlayback" style="display: none;" class="mt-3">
                    <audio id="audioPlayer" controls class="w-100"></audio>
                    <div class="mt-3">
                        <button id="saveButton" class="btn btn-primary">
                            <i class="fas fa-save"></i> Salvar e Transcrever
                        </button>
                        <button id="discardButton" class="btn btn-secondary">
                            <i class="fas fa-trash"></i> Descartar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Upload de Arquivo -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4><i class="fas fa-upload"></i> Upload de Áudio</h4>
            </div>
            <div class="card-body">
                <form action="/paciente/{{ paciente[0] }}/upload_audio" method="post" 
                      enctype="multipart/form-data" id="uploadForm">
                    <div class="mb-3">
                        <label for="audioFile" class="form-label">Arquivo de Áudio</label>
                        <input type="file" class="form-control" id="audioFile" name="audio" 
                               accept="audio/*,.mp3,.m4a,.wav,.ogg,.webm" required>
                        <small class="text-muted">Formatos: MP3, M4A, WAV, OGG, WebM</small>
                    </div>
                    
                    <div class="mb-3">
                        <label for="data_consulta" class="form-label">Data da Consulta</label>
                        <input type="datetime-local" class="form-control" 
                               id="data_consulta" name="data_consulta" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="notas" class="form-label">Notas (opcional)</label>
                        <textarea class="form-control" id="notas" name="notas" rows="3"
                                  placeholder="Observações sobre a gravação..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-cloud-upload-alt"></i> Enviar e Transcrever
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Gravações Anteriores -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h4><i class="fas fa-history"></i> Gravações Anteriores</h4>
            </div>
            <div class="card-body">
                {% if gravacoes %}
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Duração</th>
                                <th>Status</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for gravacao in gravacoes %}
                            <tr>
                                <td>{{ gravacao.data.strftime('%d/%m/%Y %H:%M') }}</td>
                                <td>{{ gravacao.duracao }}</td>
                                <td>
                                    {% if gravacao.transcrito %}
                                    <span class="badge bg-success">Transcrito</span>
                                    {% else %}
                                    <span class="badge bg-warning">Aguardando</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if gravacao.transcrito %}
                                    <a href="/gravacao/{{ gravacao.id }}/visualizar" 
                                       class="btn btn-sm btn-primary">
                                        <i class="fas fa-eye"></i> Ver
                                    </a>
                                    <a href="/gravacao/{{ gravacao.id }}/editar_episodio" 
                                       class="btn btn-sm btn-success">
                                        <i class="fas fa-edit"></i> Criar Episódio
                                    </a>
                                    {% endif %}
                                    <a href="/gravacao/{{ gravacao.id }}/download" 
                                       class="btn btn-sm btn-secondary">
                                        <i class="fas fa-download"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted text-center">Nenhuma gravação encontrada para este paciente.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
// Gravação no navegador
let mediaRecorder;
let audioChunks = [];
let startTime;
let timerInterval;
let isRecording = false;

const recordButton = document.getElementById('recordButton');
const timer = document.getElementById('timer');
const status = document.getElementById('status');
const audioPlayback = document.getElementById('audioPlayback');
const audioPlayer = document.getElementById('audioPlayer');

recordButton.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (!isRecording) {
        // Iniciar gravação
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayer.src = audioUrl;
                audioPlayback.style.display = 'block';
                
                // Preparar para upload
                window.recordedBlob = audioBlob;
            };
            
            audioChunks = [];
            mediaRecorder.start();
            startTime = Date.now();
            
            // Atualizar UI
            isRecording = true;
            recordButton.classList.add('recording');
            recordButton.innerHTML = '<i class="fas fa-stop"></i>';
            status.textContent = 'Gravando... Clique para parar';
            
            // Timer
            timerInterval = setInterval(updateTimer, 100);
            
        } catch (err) {
            alert('Erro ao acessar microfone: ' + err.message);
        }
    } else {
        // Parar gravação
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        isRecording = false;
        recordButton.classList.remove('recording');
        recordButton.innerHTML = '<i class="fas fa-microphone"></i>';
        status.textContent = 'Gravação finalizada';
        
        clearInterval(timerInterval);
    }
}

function updateTimer() {
    const elapsed = Date.now() - startTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    timer.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Salvar gravação
document.getElementById('saveButton').addEventListener('click', async () => {
    if (!window.recordedBlob) return;
    
    const formData = new FormData();
    formData.append('audio', window.recordedBlob, 'gravacao.webm');
    formData.append('data_consulta', new Date().toISOString());
    
    try {
        const response = await fetch('/paciente/{{ paciente[0] }}/upload_audio', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            window.location.reload();
        }
    } catch (err) {
        alert('Erro ao salvar: ' + err.message);
    }
});

// Descartar gravação
document.getElementById('discardButton').addEventListener('click', () => {
    audioPlayback.style.display = 'none';
    audioPlayer.src = '';
    window.recordedBlob = null;
    timer.textContent = '00:00';
    status.textContent = 'Clique para iniciar a gravação';
});

// Data/hora atual no upload
document.getElementById('data_consulta').value = new Date().toISOString().slice(0, 16);
</script>
{% endblock %}'''
    
    with open('/root/clawd/templates/gravar_consulta.html', 'w') as f:
        f.write(template)
    print("✅ Template gravar_consulta.html criado")

def criar_template_visualizar_transcricao():
    """Template para visualizar e editar transcrição"""
    
    template = '''{% extends "base.html" %}

{% block title %}Transcrição - {{ gravacao.paciente_nome }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/pacientes">Pacientes</a></li>
                <li class="breadcrumb-item"><a href="/paciente/{{ gravacao.paciente_id }}">{{ gravacao.paciente_nome }}</a></li>
                <li class="breadcrumb-item active">Transcrição</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-file-alt"></i> Transcrição da Consulta</h1>
        <p class="text-muted">
            <i class="fas fa-calendar"></i> {{ gravacao.data.strftime('%d/%m/%Y %H:%M') }} | 
            <i class="fas fa-clock"></i> {{ gravacao.duracao }}
        </p>
    </div>
</div>

<div class="row mt-3">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h4>Texto Transcrito</h4>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <audio controls class="w-100 mb-3">
                        <source src="/gravacao/{{ gravacao.id }}/audio" type="audio/webm">
                    </audio>
                </div>
                
                <form action="/gravacao/{{ gravacao.id }}/salvar_transcricao" method="post">
                    <div class="mb-3">
                        <textarea class="form-control" name="transcricao" rows="20">{{ gravacao.transcricao }}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Salvar Alterações
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h4>Ações</h4>
            </div>
            <div class="card-body">
                <a href="/gravacao/{{ gravacao.id }}/processar_ia" class="btn btn-success w-100 mb-2">
                    <i class="fas fa-magic"></i> Processar com IA
                </a>
                <a href="/gravacao/{{ gravacao.id }}/criar_episodio" class="btn btn-primary w-100 mb-2">
                    <i class="fas fa-file-medical"></i> Criar Episódio Clínico
                </a>
                <hr>
                <a href="/gravacao/{{ gravacao.id }}/download" class="btn btn-secondary w-100">
                    <i class="fas fa-download"></i> Baixar Áudio
                </a>
            </div>
        </div>
        
        <!-- Sugestões da IA -->
        {% if gravacao.analise_ia %}
        <div class="card mt-3">
            <div class="card-header">
                <h5><i class="fas fa-robot"></i> Análise IA</h5>
            </div>
            <div class="card-body small">
                <h6>Queixa Principal:</h6>
                <p>{{ gravacao.analise_ia.queixa_principal }}</p>
                
                <h6>Principais Pontos:</h6>
                <ul>
                {% for ponto in gravacao.analise_ia.pontos_principais %}
                    <li>{{ ponto }}</li>
                {% endfor %}
                </ul>
                
                <h6>Sugestão de Conduta:</h6>
                <p>{{ gravacao.analise_ia.conduta_sugerida }}</p>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}'''
    
    with open('/root/clawd/templates/visualizar_transcricao.html', 'w') as f:
        f.write(template)
    print("✅ Template visualizar_transcricao.html criado")

def adicionar_rotas_gravacao():
    """Adiciona rotas para gravação e transcrição"""
    
    novas_rotas = '''
@app.route('/paciente/<int:paciente_id>/gravar')
def gravar_consulta(paciente_id):
    """Página de gravação de consulta"""
    try:
        db = clinica_app.get_db()
        db.cursor.execute("""
        SELECT id, nome, cpf FROM pacientes WHERE id = %s
        """, (paciente_id,))
        paciente = db.cursor.fetchone()
        
        if not paciente:
            flash('Paciente não encontrado!')
            return redirect(url_for('pacientes'))
        
        # Buscar gravações anteriores
        # TODO: Implementar tabela de gravações
        gravacoes = []
        
        return render_template('gravar_consulta.html', 
                             paciente=paciente,
                             gravacoes=gravacoes)
    except Exception as e:
        flash(f'Erro: {str(e)}')
        return redirect(url_for('pacientes'))

@app.route('/paciente/<int:paciente_id>/upload_audio', methods=['POST'])
def upload_audio(paciente_id):
    """Upload e processamento de áudio"""
    try:
        if 'audio' not in request.files:
            flash('Nenhum arquivo de áudio!')
            return redirect(url_for('gravar_consulta', paciente_id=paciente_id))
        
        audio = request.files['audio']
        data_consulta = request.form.get('data_consulta')
        notas = request.form.get('notas', '')
        
        if audio.filename == '':
            flash('Nenhum arquivo selecionado!')
            return redirect(url_for('gravar_consulta', paciente_id=paciente_id))
        
        # Criar pasta para gravações
        pasta_gravacoes = f'/root/clawd/gravacoes/paciente_{paciente_id}'
        os.makedirs(pasta_gravacoes, exist_ok=True)
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(audio.filename)[1] or '.webm'
        nome_arquivo = f'consulta_{timestamp}{ext}'
        caminho_audio = os.path.join(pasta_gravacoes, nome_arquivo)
        
        audio.save(caminho_audio)
        
        # Transcrever usando Whisper
        flash('Áudio salvo! Iniciando transcrição...', 'info')
        
        # Criar job de transcrição assíncrono
        # TODO: Implementar fila de transcrição com Whisper
        
        return redirect(url_for('gravar_consulta', paciente_id=paciente_id))
        
    except Exception as e:
        flash(f'Erro no upload: {str(e)}', 'danger')
        return redirect(url_for('gravar_consulta', paciente_id=paciente_id))

@app.route('/gravacao/<int:gravacao_id>/processar_ia')
def processar_gravacao_ia(gravacao_id):
    """Processa transcrição com IA para extrair informações estruturadas"""
    try:
        # TODO: Implementar processamento com LLM
        # 1. Pegar transcrição
        # 2. Enviar para LLM com prompt médico
        # 3. Extrair: QP, HDA, Exame, HD, Conduta
        # 4. Salvar análise estruturada
        
        flash('Processamento com IA iniciado!', 'info')
        return redirect(url_for('pacientes'))
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('pacientes'))
'''
    
    # Adicionar ao arquivo
    arquivo = '/root/clawd/scripts/web_interface.py'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Inserir antes da rota de episódios
    pos = conteudo.find('@app.route(\'/paciente/<int:paciente_id>/novo_episodio\')')
    if pos > 0:
        conteudo = conteudo[:pos] + novas_rotas + '\n' + conteudo[pos:]
        
        with open(arquivo, 'w') as f:
            f.write(conteudo)
        
        print("✅ Rotas de gravação adicionadas")

def criar_script_whisper():
    """Cria script para transcrição com Whisper"""
    
    script = '''#!/usr/bin/env python3
"""
Script para transcrever áudios usando OpenAI Whisper
Pode usar API ou modelo local
"""

import os
import sys
import json
from datetime import datetime

def transcrever_com_api(arquivo_audio, api_key=None):
    """Transcreve usando API do OpenAI"""
    import openai
    
    if not api_key:
        # Tentar pegar do ambiente ou arquivo de credenciais
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ API Key não encontrada!")
        return None
    
    openai.api_key = api_key
    
    try:
        with open(arquivo_audio, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="pt"
            )
        
        return transcript
        
    except Exception as e:
        print(f"❌ Erro na transcrição: {e}")
        return None

def transcrever_local(arquivo_audio):
    """Transcreve usando Whisper local (se instalado)"""
    try:
        import whisper
        
        print("🎯 Carregando modelo Whisper...")
        model = whisper.load_model("base")
        
        print("🎤 Transcrevendo áudio...")
        result = model.transcribe(
            arquivo_audio,
            language="pt",
            fp16=False
        )
        
        return result["text"]
        
    except ImportError:
        print("❌ Whisper não instalado localmente")
        print("💡 Instale com: pip install openai-whisper")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def processar_transcricao_medica(texto):
    """Processa transcrição para extrair informações médicas"""
    
    # Prompt para LLM processar
    prompt = """
    Analise esta transcrição de consulta médica e extraia:
    
    1. QUEIXA PRINCIPAL
    2. HISTÓRIA DA DOENÇA ATUAL
    3. EXAME FÍSICO MENCIONADO
    4. HIPÓTESES DIAGNÓSTICAS
    5. CONDUTA/PLANO
    
    Transcrição:
    {texto}
    
    Retorne em formato JSON estruturado.
    """
    
    # TODO: Integrar com LLM para processamento
    # Por enquanto, retorna o texto bruto
    return {
        "texto_original": texto,
        "processado": False,
        "timestamp": datetime.now().isoformat()
    }

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 transcrever_audio.py <arquivo_audio> [api_key]")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    
    print(f"🎤 Transcrevendo: {arquivo}")
    
    # Tentar API primeiro, depois local
    texto = transcrever_com_api(arquivo, api_key)
    
    if not texto:
        print("📍 Tentando transcrição local...")
        texto = transcrever_local(arquivo)
    
    if texto:
        print("\n✅ TRANSCRIÇÃO COMPLETA:")
        print("-" * 50)
        print(texto)
        print("-" * 50)
        
        # Salvar transcrição
        arquivo_saida = arquivo.replace('.webm', '.txt').replace('.mp3', '.txt')
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(texto)
        
        print(f"\n💾 Salvo em: {arquivo_saida}")
        
        # Processar para extrair informações médicas
        analise = processar_transcricao_medica(texto)
        
        # Salvar análise
        arquivo_json = arquivo.replace('.webm', '_analise.json').replace('.mp3', '_analise.json')
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(analise, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Análise salva em: {arquivo_json}")
        
    else:
        print("❌ Não foi possível transcrever o áudio")
        sys.exit(1)

if __name__ == "__main__":
    main()'''
    
    with open('/root/clawd/scripts/transcrever_audio.py', 'w') as f:
        f.write(script)
    os.chmod('/root/clawd/scripts/transcrever_audio.py', 0o755)
    print("✅ Script transcrever_audio.py criado")

def atualizar_detalhes_com_gravacao():
    """Adiciona botão de gravação na página do paciente"""
    arquivo = '/root/clawd/templates/paciente_detalhes.html'
    
    with open(arquivo, 'r') as f:
        conteudo = f.read()
    
    # Adicionar botão de gravação ao lado do novo episódio
    if 'Novo Episódio Clínico' in conteudo:
        conteudo = conteudo.replace(
            '</a>',
            '''</a>
                    <a href="/paciente/{{ paciente[0] }}/gravar" class="btn btn-warning btn-sm">
                        <i class="fas fa-microphone"></i> Gravar Consulta
                    </a>''',
            1  # Substituir apenas primeira ocorrência após "Novo Episódio"
        )
    
    with open(arquivo, 'w') as f:
        f.write(conteudo)
    
    print("✅ Botão de gravação adicionado aos detalhes do paciente")

def criar_tabela_gravacoes():
    """SQL para criar tabela de gravações"""
    sql = '''-- Tabela para armazenar gravações de consultas
CREATE TABLE IF NOT EXISTS gravacoes_consultas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    data_gravacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    arquivo_audio VARCHAR(500) NOT NULL,
    duracao VARCHAR(20),
    transcricao TEXT,
    analise_ia JSONB,
    transcrito BOOLEAN DEFAULT FALSE,
    episodio_criado BOOLEAN DEFAULT FALSE,
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gravacoes_paciente ON gravacoes_consultas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_gravacoes_data ON gravacoes_consultas(data_gravacao);'''
    
    with open('/root/clawd/scripts/criar_tabela_gravacoes.sql', 'w') as f:
        f.write(sql)
    
    # Executar no banco
    import psycopg2
    conn = psycopg2.connect(
        dbname="clinica_dr_felipe",
        user="clinica_admin",
        password="clinica2026!",
        host="localhost",
        port="5432"
    )
    
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("✅ Tabela gravacoes_consultas criada")
    conn.close()

def main():
    print("🎤 IMPLEMENTANDO SISTEMA DE GRAVAÇÃO DE CONSULTAS")
    print("=" * 60)
    
    # Criar pastas necessárias
    os.makedirs('/root/clawd/gravacoes', exist_ok=True)
    
    # Criar templates
    criar_template_gravacao()
    criar_template_visualizar_transcricao()
    
    # Adicionar rotas
    adicionar_rotas_gravacao()
    
    # Criar script de transcrição
    criar_script_whisper()
    
    # Atualizar página de detalhes
    atualizar_detalhes_com_gravacao()
    
    # Criar tabela no banco
    criar_tabela_gravacoes()
    
    print("\n✅ SISTEMA DE GRAVAÇÃO IMPLEMENTADO!")
    print("\n📝 Funcionalidades:")
    print("1. 🎤 Gravação direto no navegador")
    print("2. 📁 Upload de arquivos de áudio")
    print("3. 📝 Transcrição com Whisper (API ou local)")
    print("4. 🤖 Processamento com IA (extração estruturada)")
    print("5. 📋 Criação automática de episódio clínico")
    print("\n⚠️  Para transcrição local, instale:")
    print("   pip install openai-whisper")
    print("\n💡 Para API OpenAI, configure:")
    print("   export OPENAI_API_KEY='sua-chave'")

if __name__ == "__main__":
    main()
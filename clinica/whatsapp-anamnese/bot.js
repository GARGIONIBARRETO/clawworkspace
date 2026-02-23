const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');
const path = require('path');
const qrcode = require('qrcode-terminal');

// Configuração
const ANAMNESES_DIR = '/root/clawd/clinica/anamneses';
const SESSIONS_FILE = './sessions.json';

// Estado das sessões de anamnese
let sessions = {};

// Carregar sessões existentes
if (fs.existsSync(SESSIONS_FILE)) {
    sessions = JSON.parse(fs.readFileSync(SESSIONS_FILE, 'utf8'));
}

function saveSessions() {
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify(sessions, null, 2));
}

// Estrutura do questionário (sem histamina)
const QUESTIONS = [
    // Identificação
    { id: 'nome', section: 'identificacao', text: '📋 *ANAMNESE - Dr. Felipe Barreto*\nNeurocirurgia de Coluna | Medicina Funcional\n\nVamos começar!\n\nQual é o seu *nome completo*?' },
    { id: 'dataNascimento', section: 'identificacao', text: 'Qual sua *data de nascimento*? (dd/mm/aaaa)' },
    { id: 'sexo', section: 'identificacao', text: 'Qual seu *sexo biológico*?\n\n1️⃣ Masculino\n2️⃣ Feminino', options: ['masculino', 'feminino'] },
    { id: 'profissao', section: 'identificacao', text: 'Qual sua *profissão/ocupação* atual?' },
    { id: 'telefone', section: 'identificacao', text: 'Confirme seu *telefone* (WhatsApp):' },
    
    // Queixa Principal
    { id: 'queixaPrincipal', section: 'queixa', text: '🎯 *QUEIXA PRINCIPAL*\n\nQual o *principal motivo* da sua consulta? Descreva com suas palavras o que está sentindo.' },
    { id: 'tempoProblema', section: 'queixa', text: 'Há quanto tempo esse problema começou?\n\n1️⃣ Menos de 1 semana\n2️⃣ 1 a 4 semanas\n3️⃣ 1 a 3 meses\n4️⃣ 3 a 6 meses\n5️⃣ 6 a 12 meses\n6️⃣ Mais de 1 ano', options: ['menos_1_semana', '1_4_semanas', '1_3_meses', '3_6_meses', '6_12_meses', 'mais_1_ano'] },
    { id: 'eventoDesencadeante', section: 'queixa', text: 'Houve algum *evento específico* que desencadeou os sintomas? (queda, esforço, estresse, etc.)\n\nSe não, digite "não".' },
    
    // Investigação da Dor
    { id: 'dorLocal', section: 'dor', text: '💢 *INVESTIGAÇÃO DA DOR*\n\nOnde você sente dor? (pode marcar mais de uma)\n\n0️⃣ Não sinto dor\n1️⃣ Pescoço/Cervical\n2️⃣ Região torácica (meio das costas)\n3️⃣ Lombar\n4️⃣ Glúteo/Quadril\n5️⃣ Perna\n6️⃣ Braço\n7️⃣ Cabeça\n\nDigite os números separados por vírgula (ex: 1,3,5)', multi: true, options: ['sem_dor', 'cervical', 'toracica', 'lombar', 'gluteo', 'perna', 'braco', 'cabeca'] },
    { id: 'dorIntensidade', section: 'dor', text: 'Qual a *intensidade média* da sua dor? (0 = sem dor, 10 = pior dor)\n\nDigite um número de 0 a 10:', conditional: (data) => !data.dorLocal?.includes('sem_dor') },
    { id: 'dorTipo', section: 'dor', text: 'Como você descreveria sua dor?\n\n1️⃣ Queimação/Ardência\n2️⃣ Pontada/Facada\n3️⃣ Peso/Pressão\n4️⃣ Choque/Fisgada\n5️⃣ Formigamento/Dormência\n6️⃣ Latejante\n\nDigite os números (ex: 1,3)', multi: true, options: ['queimacao', 'pontada', 'peso', 'choque', 'formigamento', 'latejante'], conditional: (data) => !data.dorLocal?.includes('sem_dor') },
    
    // Sinais de Alerta
    { id: 'redFlags', section: 'alertas', text: '⚠️ *SINTOMAS IMPORTANTES*\n\nMarque se apresenta algum destes sintomas:\n\n0️⃣ Nenhum dos abaixo\n1️⃣ Fraqueza nas pernas\n2️⃣ Fraqueza nas mãos/braços\n3️⃣ Dificuldade para segurar urina\n4️⃣ Dificuldade para segurar fezes\n5️⃣ Dormência na região genital\n6️⃣ Perda de equilíbrio ao caminhar\n7️⃣ Dor que acorda durante a noite\n8️⃣ Febre associada à dor\n9️⃣ Perda de peso inexplicada\n\nDigite os números (ex: 0 ou 1,7)', multi: true, options: ['nenhum', 'fraqueza_pernas', 'fraqueza_bracos', 'dificuldade_urina', 'dificuldade_fezes', 'anestesia_sela', 'perda_equilibrio', 'dor_noturna', 'febre', 'perda_peso'] },
    
    // Sono e Estresse
    { id: 'sonoQualidade', section: 'sono', text: '😴 *SONO E ESTRESSE*\n\nComo se sente ao acordar?\n\n1️⃣ Descansado e com energia\n2️⃣ Um pouco cansado, mas ok\n3️⃣ Cansado como se não tivesse dormido\n4️⃣ Exausto', options: ['descansado', 'pouco_cansado', 'cansado', 'exausto'] },
    { id: 'horasDormidas', section: 'sono', text: 'Quantas horas dorme por noite (em média)?\n\n1️⃣ Menos de 4h\n2️⃣ 4-5h\n3️⃣ 5-6h\n4️⃣ 6-7h\n5️⃣ 7-8h\n6️⃣ Mais de 8h', options: ['menos_4', '4_5', '5_6', '6_7', '7_8', 'mais_8'] },
    { id: 'estresseNivel', section: 'sono', text: 'Nível de estresse atual (0 = nenhum, 10 = máximo):\n\nDigite um número de 0 a 10:' },
    
    // Função GI (resumido, sem histamina)
    { id: 'frequenciaEvacuacao', section: 'gi', text: '🦠 *FUNÇÃO GASTROINTESTINAL*\n\nQuantas vezes evacua por semana?\n\n1️⃣ Menos de 3x\n2️⃣ 3-7x (até 1x/dia)\n3️⃣ 7-14x (1-2x/dia)\n4️⃣ Mais de 14x', options: ['menos_3', '3_7', '7_14', 'mais_14'] },
    { id: 'distensaoAbdominal', section: 'gi', text: 'Sente barriga inchada após refeições?\n\n1️⃣ Não\n2️⃣ Às vezes\n3️⃣ Frequentemente\n4️⃣ Sempre', options: ['nao', 'as_vezes', 'frequente', 'sempre'] },
    
    // Histórico Médico
    { id: 'condicoes', section: 'historico', text: '🏥 *HISTÓRICO MÉDICO*\n\nPossui alguma dessas condições?\n\n0️⃣ Nenhuma\n1️⃣ Diabetes\n2️⃣ Hipertensão\n3️⃣ Colesterol alto\n4️⃣ Depressão/Ansiedade\n5️⃣ Problemas de tireoide\n6️⃣ Hérnia de disco\n7️⃣ Osteoporose\n\nDigite os números (ex: 0 ou 2,4,6)', multi: true, options: ['nenhuma', 'diabetes', 'hipertensao', 'colesterol', 'depressao_ansiedade', 'tireoide', 'hernia', 'osteoporose'] },
    { id: 'medicamentosLista', section: 'historico', text: 'Lista de *medicamentos* que usa atualmente:\n\n(Digite "nenhum" se não usar)' },
    { id: 'alergias', section: 'historico', text: '*Alergias* a medicamentos:\n\n(Digite "nenhuma" se não tiver)' },
    
    // Tratamentos
    { id: 'tratamentos', section: 'tratamentos', text: '💪 *TRATAMENTOS ANTERIORES*\n\nJá fez algum tratamento para esse problema?\n\n0️⃣ Nenhum\n1️⃣ Medicações\n2️⃣ Fisioterapia\n3️⃣ Acupuntura\n4️⃣ Infiltração/Bloqueio\n5️⃣ Cirurgia\n6️⃣ Pilates/RPG\n\nDigite os números:', multi: true, options: ['nenhum', 'medicacoes', 'fisioterapia', 'acupuntura', 'infiltracao', 'cirurgia', 'pilates_rpg'] },
    { id: 'atividadeFisica', section: 'tratamentos', text: 'Pratica *atividade física*?\n\n1️⃣ Não\n2️⃣ 1-2x por semana\n3️⃣ 3-4x por semana\n4️⃣ 5+ vezes por semana', options: ['nao', '1_2x', '3_4x', '5_mais'] },
    
    // Expectativas
    { id: 'expectativas', section: 'final', text: '🎯 *EXPECTATIVAS*\n\nO que você espera da consulta? Qual seu principal objetivo com o tratamento?' },
];

function getNextQuestion(session) {
    const currentIndex = session.currentQuestion;
    
    for (let i = currentIndex; i < QUESTIONS.length; i++) {
        const q = QUESTIONS[i];
        // Verificar condicionais
        if (q.conditional && !q.conditional(session.data)) {
            continue;
        }
        return { question: q, index: i };
    }
    return null;
}

function parseAnswer(question, answer) {
    answer = answer.trim();
    
    if (question.options) {
        if (question.multi) {
            // Múltipla escolha
            const nums = answer.split(/[,\s]+/).map(n => parseInt(n.trim()));
            return nums.filter(n => !isNaN(n) && n >= 0 && n < question.options.length)
                       .map(n => question.options[n]);
        } else {
            // Escolha única
            const num = parseInt(answer) - 1;
            if (num >= 0 && num < question.options.length) {
                return question.options[num];
            }
            return null;
        }
    }
    
    return answer;
}

function generateSummary(data) {
    let summary = `📋 *RESUMO DA ANAMNESE*\n`;
    summary += `━━━━━━━━━━━━━━━━━━━━━\n\n`;
    summary += `👤 *Paciente:* ${data.nome || '-'}\n`;
    summary += `📅 *Nascimento:* ${data.dataNascimento || '-'}\n`;
    summary += `📱 *Telefone:* ${data.telefone || '-'}\n\n`;
    summary += `🎯 *Queixa:* ${data.queixaPrincipal || '-'}\n`;
    summary += `⏱️ *Tempo:* ${data.tempoProblema || '-'}\n\n`;
    
    if (data.dorLocal && !data.dorLocal.includes('sem_dor')) {
        summary += `💢 *Dor:* ${data.dorLocal?.join(', ') || '-'}\n`;
        summary += `📊 *Intensidade:* ${data.dorIntensidade || '-'}/10\n\n`;
    }
    
    if (data.redFlags && !data.redFlags.includes('nenhum')) {
        summary += `⚠️ *Red Flags:* ${data.redFlags?.join(', ')}\n\n`;
    }
    
    summary += `💊 *Medicamentos:* ${data.medicamentosLista || '-'}\n`;
    summary += `🎯 *Expectativas:* ${data.expectativas || '-'}\n`;
    
    return summary;
}

async function savePDF(data, jid) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `anamnese_whatsapp_${data.nome?.replace(/\s+/g, '_') || 'paciente'}_${timestamp}.json`;
    const filepath = path.join(ANAMNESES_DIR, filename);
    
    if (!fs.existsSync(ANAMNESES_DIR)) {
        fs.mkdirSync(ANAMNESES_DIR, { recursive: true });
    }
    
    const record = {
        source: 'whatsapp',
        whatsappJid: jid,
        timestamp: new Date().toISOString(),
        data: data
    };
    
    fs.writeFileSync(filepath, JSON.stringify(record, null, 2));
    console.log(`Anamnese salva: ${filepath}`);
    return filepath;
}

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    
    const sock = makeWASocket({
        auth: state,
        logger: pino({ level: 'silent' })
    });
    
    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log('\n📱 Escaneie o QR Code com o WhatsApp do número (11) 93048-8315\n');
            qrcode.generate(qr, { small: true });
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Conexão fechada. Reconectando:', shouldReconnect);
            if (shouldReconnect) {
                startBot();
            }
        } else if (connection === 'open') {
            console.log('✅ Bot conectado ao WhatsApp!');
        }
    });
    
    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.message || msg.key.fromMe) return;
        
        const jid = msg.key.remoteJid;
        const text = msg.message.conversation || 
                     msg.message.extendedTextMessage?.text || '';
        
        if (!text) return;
        
        const textLower = text.toLowerCase().trim();
        
        // Comandos
        if (textLower === 'anamnese' || textLower === 'começar' || textLower === 'iniciar') {
            // Iniciar nova anamnese
            sessions[jid] = {
                currentQuestion: 0,
                data: {},
                startedAt: new Date().toISOString()
            };
            saveSessions();
            
            const next = getNextQuestion(sessions[jid]);
            await sock.sendMessage(jid, { text: next.question.text });
            return;
        }
        
        if (textLower === 'cancelar') {
            delete sessions[jid];
            saveSessions();
            await sock.sendMessage(jid, { text: '❌ Anamnese cancelada. Digite *anamnese* para começar novamente.' });
            return;
        }
        
        // Processando resposta de anamnese em andamento
        if (sessions[jid]) {
            const session = sessions[jid];
            const nextQ = getNextQuestion(session);
            
            if (!nextQ) {
                // Já terminou
                return;
            }
            
            const answer = parseAnswer(nextQ.question, text);
            
            if (answer === null && nextQ.question.options) {
                await sock.sendMessage(jid, { text: '⚠️ Resposta inválida. Por favor, digite o número correspondente.' });
                return;
            }
            
            // Salvar resposta
            session.data[nextQ.question.id] = answer;
            session.currentQuestion = nextQ.index + 1;
            saveSessions();
            
            // Próxima pergunta
            const next = getNextQuestion(session);
            
            if (next) {
                await sock.sendMessage(jid, { text: next.question.text });
            } else {
                // Finalizar
                const summary = generateSummary(session.data);
                await savePDF(session.data, jid);
                
                await sock.sendMessage(jid, { text: summary });
                await sock.sendMessage(jid, { text: '✅ *Anamnese concluída!*\n\nSuas informações foram registradas. O Dr. Felipe receberá seus dados antes da consulta.\n\nObrigado!' });
                
                delete sessions[jid];
                saveSessions();
            }
        } else {
            // Sem sessão ativa
            await sock.sendMessage(jid, { 
                text: '👋 Olá! Sou o assistente do *Dr. Felipe Barreto*.\n\nPara preencher a anamnese antes da consulta, digite:\n\n*anamnese*' 
            });
        }
    });
}

// Iniciar
console.log('🚀 Iniciando Bot WhatsApp Anamnese...\n');
startBot();

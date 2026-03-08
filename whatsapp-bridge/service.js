const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');

const logger = pino({ level: 'silent' });

let sock;

async function connectWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        logger: logger
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect } = update;
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('[WhatsApp] Conexão fechada. Reconectando:', shouldReconnect);
            if (shouldReconnect) {
                setTimeout(connectWhatsApp, 5000);
            }
        } else if (connection === 'open') {
            console.log('[WhatsApp] ✅ Conectado!');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.key.fromMe && m.type === 'notify') {
            await handleIncomingMessage(msg);
        }
    });

    return sock;
}

async function handleIncomingMessage(msg) {
    const sender = msg.key.remoteJid;
    const text = msg.message?.conversation || 
                msg.message?.extendedTextMessage?.text || '';
    
    console.log(`[WhatsApp] 📩 ${sender}: ${text}`);
    
    // Log message to file for processing
    const logEntry = {
        timestamp: new Date().toISOString(),
        from: sender,
        text: text,
        messageId: msg.key.id
    };
    
    fs.appendFileSync('./messages.jsonl', JSON.stringify(logEntry) + '\n');
    
    // Handle confirmation responses
    if (text === '1') {
        await sendMessage(sender, '✅ Consulta confirmada! Aguardamos você. 😊');
    } else if (text === '2') {
        await sendMessage(sender, '📞 Entendido! Nossa equipe entrará em contato para reagendar.');
    }
}

async function sendMessage(to, text) {
    if (!sock) {
        console.log('[WhatsApp] ❌ Não conectado');
        return false;
    }
    
    try {
        await sock.sendMessage(to, { text });
        console.log(`[WhatsApp] ✉️ Enviado para ${to}`);
        return true;
    } catch (err) {
        console.log('[WhatsApp] ❌ Erro ao enviar:', err.message);
        return false;
    }
}

// Export for external use
module.exports = { sendMessage, connectWhatsApp };

// Start if run directly
if (require.main === module) {
    console.log('[WhatsApp] Iniciando serviço...');
    connectWhatsApp();
}

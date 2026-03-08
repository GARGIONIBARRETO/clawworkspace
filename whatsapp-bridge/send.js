#!/usr/bin/env node
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');

const logger = pino({ level: 'silent' });

const phoneNumber = process.argv[2];
const message = process.argv.slice(3).join(' ');

if (!phoneNumber || !message) {
    console.log('Uso: node send.js <numero> <mensagem>');
    console.log('Exemplo: node send.js 5511999999999 Olá, tudo bem?');
    process.exit(1);
}

// Format phone number
const jid = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`;

async function send() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    
    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        logger: logger
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection } = update;
        
        if (connection === 'open') {
            try {
                await sock.sendMessage(jid, { text: message });
                console.log(`✅ Mensagem enviada para ${phoneNumber}`);
                process.exit(0);
            } catch (err) {
                console.log('❌ Erro:', err.message);
                process.exit(1);
            }
        }
    });
}

send();

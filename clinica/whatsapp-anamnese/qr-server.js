const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const fs = require('fs');

async function start() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    
    const sock = makeWASocket({
        auth: state,
        logger: pino({ level: 'silent' })
    });
    
    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log('Gerando QR code...');
            await QRCode.toFile('./qr-code.png', qr, { 
                width: 400,
                margin: 2 
            });
            console.log('QR salvo em: /root/clawd/clinica/whatsapp-anamnese/qr-code.png');
            console.log('PRONTO');
        }
        
        if (connection === 'open') {
            console.log('CONECTADO!');
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            if (shouldReconnect) {
                start();
            }
        }
    });
}

start();

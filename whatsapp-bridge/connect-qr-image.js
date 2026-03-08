const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const QRCode = require('qrcode');
const pino = require('pino');
const fs = require('fs');

const logger = pino({ level: 'silent' });

async function connectWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    
    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        logger: logger
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log('\n📱 QR CODE GERADO!\n');
            // Save QR as image
            await QRCode.toFile('/tmp/whatsapp_qr.png', qr, {
                scale: 8,
                margin: 2,
                color: {
                    dark: '#000000',
                    light: '#ffffff'
                }
            });
            console.log('✅ QR Code salvo em: /tmp/whatsapp_qr.png');
            console.log('\n⏳ Aguardando você escanear...\n');
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Conexão fechada. Reconectando:', shouldReconnect);
            if (shouldReconnect) {
                connectWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('\n✅ CONECTADO COM SUCESSO!\n');
            console.log('WhatsApp pronto para uso.');
            
            // Get connection info
            const user = sock.user;
            console.log('Número conectado:', user.id.split(':')[0]);
            console.log('\nSessão salva. O bot vai reconectar automaticamente.');
            console.log('Pressione Ctrl+C para encerrar.\n');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.key.fromMe && m.type === 'notify') {
            const sender = msg.key.remoteJid;
            const text = msg.message?.conversation || 
                        msg.message?.extendedTextMessage?.text || 
                        '[mídia]';
            console.log(`📩 Nova mensagem de ${sender}: ${text}`);
        }
    });

    return sock;
}

connectWhatsApp();

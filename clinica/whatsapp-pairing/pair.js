const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, makeCacheableSignalKeyStore, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');

const PHONE_NUMBER = '5511930488315';

async function start() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth');
    const { version } = await fetchLatestBaileysVersion();
    
    const sock = makeWASocket({
        version,
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, pino({ level: 'silent' }))
        },
        printQRInTerminal: false,
        logger: pino({ level: 'warn' }),
        browser: ['Chrome', 'Desktop', '127.0.0.1']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            // QR disponível - vamos pedir pairing code
            console.log('📱 Solicitando código de pareamento...\n');
            try {
                const code = await sock.requestPairingCode(PHONE_NUMBER);
                console.log(`\n🔢 CÓDIGO: ${code}\n`);
                console.log('No WhatsApp do (11) 93048-8315:');
                console.log('Configurações → Dispositivos → Conectar → Conectar com número\n');
                fs.writeFileSync('code.txt', code);
            } catch (err) {
                console.error('Erro:', err.message);
            }
        }
        
        if (connection === 'close') {
            const reason = lastDisconnect?.error?.output?.statusCode;
            console.log('Conexão fechada. Razão:', reason);
            if (reason !== DisconnectReason.loggedOut) {
                console.log('Reconectando...');
                start();
            }
        } else if (connection === 'open') {
            console.log('✅ CONECTADO!');
        }
    });
}

start();

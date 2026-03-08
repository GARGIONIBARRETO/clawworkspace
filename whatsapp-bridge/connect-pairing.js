const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');
const readline = require('readline');

const logger = pino({ level: 'silent' });

// Get phone number from command line
const phoneNumber = process.argv[2];

if (!phoneNumber) {
    console.log('❌ Uso: node connect-pairing.js <numero>');
    console.log('   Exemplo: node connect-pairing.js 5511999999999');
    console.log('   (código do país + DDD + número, sem espaços ou símbolos)');
    process.exit(1);
}

async function connectWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    
    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        logger: logger
    });

    sock.ev.on('creds.update', saveCreds);

    // Request pairing code
    if (!sock.authState.creds.registered) {
        setTimeout(async () => {
            try {
                const code = await sock.requestPairingCode(phoneNumber);
                console.log('\n========================================');
                console.log('📱 CÓDIGO DE VINCULAÇÃO:');
                console.log('========================================');
                console.log(`\n   🔑  ${code}\n`);
                console.log('========================================');
                console.log('\nNo WhatsApp do celular:');
                console.log('1. Menu (⋮) > Aparelhos conectados');
                console.log('2. Conectar aparelho');
                console.log('3. Toque em "Conectar com número de telefone"');
                console.log('4. Digite o código acima');
                console.log('\n⏳ Aguardando conexão...\n');
            } catch (err) {
                console.log('❌ Erro ao gerar código:', err.message);
            }
        }, 3000);
    }

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect } = update;
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            if (shouldReconnect) {
                connectWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('\n✅ CONECTADO COM SUCESSO!\n');
            const user = sock.user;
            console.log('Número conectado:', user.id.split(':')[0]);
            console.log('\nSessão salva. Pode fechar com Ctrl+C.');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.key.fromMe && m.type === 'notify') {
            const sender = msg.key.remoteJid;
            const text = msg.message?.conversation || 
                        msg.message?.extendedTextMessage?.text || 
                        '[mídia]';
            console.log(`📩 Mensagem de ${sender}: ${text}`);
        }
    });

    return sock;
}

connectWhatsApp();

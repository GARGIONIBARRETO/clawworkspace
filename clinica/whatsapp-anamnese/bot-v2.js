const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { createClient } = require('@supabase/supabase-js');
const PDFDocument = require('pdfkit');

console.log('🚀 Iniciando Bot WhatsApp Anamnese...\n');

const ANAMNESES_DIR = '/root/clawd/clinica/anamneses';
const SESSIONS_FILE = './sessions.json';
const FELIPE_EMAIL = 'clinicadacolunadrfelipebarreto@gmail.com';
// Felipe - números admin (apenas transcrição de áudio)
const ADMIN_PHONES = [
    '5511974651414@c.us',
    '5541917887972@c.us', 
    '5511910667799@c.us',
    '5511930488315@c.us'
];

// Supabase
const supabaseConfig = JSON.parse(fs.readFileSync('/root/.secrets/supabase_clinica.json', 'utf8'));
const supabase = createClient(supabaseConfig.url, supabaseConfig.anon_key);

// Gerar PDF da anamnese
async function generatePDF(data) {
    return new Promise((resolve) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const nome = (data.nome || 'paciente').replace(/\s+/g, '_').substring(0, 30);
        const pdfPath = path.join(ANAMNESES_DIR, `anamnese_${nome}_${timestamp}.pdf`);
        
        const doc = new PDFDocument({ margin: 50 });
        const stream = fs.createWriteStream(pdfPath);
        doc.pipe(stream);
        
        // Header
        doc.fontSize(20).font('Helvetica-Bold').text('ANAMNESE', { align: 'center' });
        doc.fontSize(12).font('Helvetica').text('Dr. Felipe Barreto - Neurocirurgia de Coluna', { align: 'center' });
        doc.moveDown();
        doc.fontSize(10).text(`Data: ${new Date().toLocaleDateString('pt-BR')} ${new Date().toLocaleTimeString('pt-BR')}`, { align: 'right' });
        doc.moveDown();
        
        // Linha separadora
        doc.moveTo(50, doc.y).lineTo(550, doc.y).stroke();
        doc.moveDown();
        
        // Identificação
        doc.fontSize(14).font('Helvetica-Bold').text('IDENTIFICAÇÃO');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Nome: ${data.nome || '-'}`);
        doc.text(`Data de Nascimento: ${data.dataNascimento || '-'}`);
        doc.text(`Sexo: ${data.sexo || '-'}`);
        doc.text(`Profissão: ${data.profissao || '-'}`);
        doc.moveDown();
        
        // Queixa Principal
        doc.fontSize(14).font('Helvetica-Bold').text('QUEIXA PRINCIPAL');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Queixa: ${data.queixaPrincipal || '-'}`);
        doc.text(`Tempo: ${data.tempoProblema || '-'}`);
        doc.text(`Evento desencadeante: ${data.eventoDesencadeante || '-'}`);
        doc.moveDown();
        
        // Dor
        if (data.temDor === 'sim') {
            doc.fontSize(14).font('Helvetica-Bold').text('DOR');
            doc.fontSize(11).font('Helvetica');
            doc.text(`Localização: ${Array.isArray(data.dorLocal) ? data.dorLocal.join(', ') : data.dorLocal || '-'}`);
            doc.text(`Intensidade: ${data.dorIntensidade || '-'}/10`);
            doc.text(`Tipo: ${Array.isArray(data.dorTipo) ? data.dorTipo.join(', ') : data.dorTipo || '-'}`);
            doc.moveDown();
        }
        
        // Red Flags
        if (data.redFlags && !data.redFlags.includes('nenhum')) {
            doc.fontSize(14).font('Helvetica-Bold').fillColor('red').text('⚠️ RED FLAGS');
            doc.fontSize(11).font('Helvetica').fillColor('black');
            doc.text(Array.isArray(data.redFlags) ? data.redFlags.join(', ') : data.redFlags);
            doc.moveDown();
        }
        
        // Scores NDI/ODI
        if (data.ndi_score) {
            doc.fontSize(14).font('Helvetica-Bold').text('NDI (Incapacidade Cervical)');
            doc.fontSize(11).font('Helvetica');
            doc.text(`Score: ${data.ndi_score.total}/50 (${data.ndi_score.pct}%) - ${data.ndi_score.interp}`);
            doc.moveDown();
        }
        if (data.odi_score) {
            doc.fontSize(14).font('Helvetica-Bold').text('ODI (Incapacidade Lombar)');
            doc.fontSize(11).font('Helvetica');
            doc.text(`Score: ${data.odi_score.total}/50 (${data.odi_score.pct}%) - ${data.odi_score.interp}`);
            doc.moveDown();
        }
        
        // Função GI
        doc.fontSize(14).font('Helvetica-Bold').text('FUNÇÃO GASTROINTESTINAL');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Evacuação: ${data.frequenciaEvacuacao || '-'}`);
        doc.text(`Bristol: ${data.escalaBristol || '-'}`);
        doc.text(`Distensão: ${data.distensaoAbdominal || '-'}`);
        doc.text(`Flatulência: ${data.flatulencia || '-'}`);
        doc.moveDown();
        
        // Sono
        doc.fontSize(14).font('Helvetica-Bold').text('SONO E ESTRESSE');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Qualidade sono: ${data.sonoQualidade || '-'}`);
        doc.text(`Horas: ${data.horasDormidas || '-'}`);
        doc.text(`Estresse: ${data.estresseNivel || '-'}/10`);
        doc.moveDown();
        
        // Histórico
        doc.fontSize(14).font('Helvetica-Bold').text('HISTÓRICO');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Condições: ${Array.isArray(data.condicoes) ? data.condicoes.join(', ') : data.condicoes || '-'}`);
        doc.text(`Medicamentos: ${data.medicamentos || '-'}`);
        doc.text(`Alergias: ${data.alergias || '-'}`);
        doc.text(`Cirurgias: ${data.cirurgias || '-'}`);
        doc.moveDown();
        
        // Hábitos
        doc.fontSize(14).font('Helvetica-Bold').text('HÁBITOS');
        doc.fontSize(11).font('Helvetica');
        doc.text(`Atividade física: ${data.atividadeFisica || '-'}`);
        doc.text(`Tabagismo: ${data.tabagismo || '-'}`);
        doc.text(`Álcool: ${data.alcool || '-'}`);
        doc.moveDown();
        
        // Expectativas
        doc.fontSize(14).font('Helvetica-Bold').text('EXPECTATIVAS');
        doc.fontSize(11).font('Helvetica');
        doc.text(data.expectativas || '-');
        
        doc.end();
        
        stream.on('finish', () => {
            console.log(`📄 PDF gerado: ${pdfPath}`);
            resolve(pdfPath);
        });
    });
}

// Salvar no Supabase
async function saveToSupabase(data, phone) {
    try {
        const record = {
            nome: data.nome,
            data_nascimento: data.dataNascimento,
            sexo: data.sexo,
            telefone: phone.replace('@c.us', '').replace('@lid', ''),
            queixa_principal: data.queixaPrincipal,
            tempo_problema: data.tempoProblema,
            tem_dor: data.temDor === 'sim',
            dor_local: data.dorLocal,
            dor_intensidade: parseInt(data.dorIntensidade) || null,
            red_flags: data.redFlags,
            ndi_score: data.ndi_score?.total || null,
            ndi_percent: data.ndi_score?.pct || null,
            odi_score: data.odi_score?.total || null,
            odi_percent: data.odi_score?.pct || null,
            dados_completos: data,
            source: 'whatsapp',
            created_at: new Date().toISOString()
        };
        
        const { data: result, error } = await supabase
            .from('anamneses')
            .insert([record])
            .select();
        
        if (error) {
            console.error('Erro Supabase:', error.message);
            return null;
        }
        console.log('✅ Salvo no Supabase:', result[0]?.id);
        return result[0];
    } catch (err) {
        console.error('Erro Supabase:', err.message);
        return null;
    }
}

// Enviar email com PDF
async function sendEmailWithPDF(data, pdfPath) {
    return new Promise((resolve) => {
        const nome = data.nome || 'Paciente';
        const subject = `Nova Anamnese WhatsApp - ${nome}`;
        const body = `Nova anamnese recebida via WhatsApp:\n\nPaciente: ${nome}\nQueixa: ${data.queixaPrincipal || '-'}\nData: ${new Date().toLocaleString('pt-BR')}\n\nPDF em anexo.`;
        
        const cmd = `python3 /root/clawd/scripts/email_sender.py "${FELIPE_EMAIL}" "${subject}" "${body}" "${pdfPath}"`;
        
        exec(cmd, { timeout: 30000 }, (err, stdout, stderr) => {
            if (err) {
                console.error('Erro email:', stderr);
                resolve(false);
            } else {
                console.log('✅ Email enviado');
                resolve(true);
            }
        });
    });
}

// Transcrever áudio usando Whisper LOCAL (gratuito)
async function transcribeAudio(audioBuffer, mimetype) {
    return new Promise((resolve) => {
        try {
            const timestamp = Date.now();
            const ext = mimetype.includes('ogg') ? 'ogg' : (mimetype.includes('mp4') ? 'm4a' : 'mp3');
            const tempFile = `/tmp/wsp_${timestamp}.${ext}`;
            
            fs.writeFileSync(tempFile, audioBuffer);
            
            // Whisper local - modelo "base" é rápido e bom pra português
            const cmd = `whisper "${tempFile}" --model base --language pt --output_format txt --output_dir /tmp`;
            
            exec(cmd, { timeout: 90000 }, (err, stdout, stderr) => {
                try {
                    // Whisper salva como /tmp/wsp_TIMESTAMP.txt
                    const txtFile = `/tmp/wsp_${timestamp}.txt`;
                    console.log(`Procurando: ${txtFile}`);
                    
                    if (fs.existsSync(txtFile)) {
                        const text = fs.readFileSync(txtFile, 'utf8').trim();
                        console.log(`✅ Transcrição: ${text}`);
                        try { fs.unlinkSync(tempFile); } catch(e) {}
                        try { fs.unlinkSync(txtFile); } catch(e) {}
                        resolve(text || null);
                    } else {
                        console.error('Arquivo não encontrado:', txtFile);
                        console.error('Stderr:', stderr);
                        try { fs.unlinkSync(tempFile); } catch(e) {}
                        resolve(null);
                    }
                } catch (e) {
                    console.error('Erro lendo transcrição:', e.message);
                    resolve(null);
                }
            });
        } catch (err) {
            console.error('Erro transcrição:', err.message);
            resolve(null);
        }
    });
}

let sessions = {};
if (fs.existsSync(SESSIONS_FILE)) {
    sessions = JSON.parse(fs.readFileSync(SESSIONS_FILE, 'utf8'));
}

function saveSessions() {
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify(sessions, null, 2));
}

// Helper: verifica se tem dor cervical
const temDorCervical = (d) => d.temDor === 'sim' && d.dorLocal && d.dorLocal.includes('cervical');
// Helper: verifica se tem dor lombar
const temDorLombar = (d) => d.temDor === 'sim' && d.dorLocal && d.dorLocal.includes('lombar');

// Questionário completo com NDI/ODI
const QUESTIONS = [
    // === IDENTIFICAÇÃO ===
    { id: 'nome', text: '📋 *ANAMNESE - Dr. Felipe Barreto*\nNeurocirurgia de Coluna | Medicina Funcional\n\nVamos começar!\n\n💡 _Digite *cancelar* para recomeçar ou *pular* para pular uma pergunta._\n\nQual é o seu *nome completo*?' },
    { id: 'dataNascimento', text: 'Qual sua *data de nascimento*? (dd/mm/aaaa)' },
    { id: 'sexo', text: 'Qual seu *sexo biológico*?\n\n1️⃣ Masculino\n2️⃣ Feminino', options: ['masculino', 'feminino'] },
    { id: 'profissao', text: 'Qual sua *profissão/ocupação* atual?' },
    
    // === QUEIXA PRINCIPAL ===
    { id: 'queixaPrincipal', text: '🎯 *QUEIXA PRINCIPAL*\n\nQual o *principal motivo* da sua consulta? Descreva com suas palavras.' },
    { id: 'tempoProblema', text: 'Há quanto tempo esse problema começou?\n\n1️⃣ Menos de 1 semana\n2️⃣ 1 a 4 semanas\n3️⃣ 1 a 3 meses\n4️⃣ 3 a 6 meses\n5️⃣ 6 a 12 meses\n6️⃣ Mais de 1 ano', options: ['menos_1_semana', '1_4_semanas', '1_3_meses', '3_6_meses', '6_12_meses', 'mais_1_ano'] },
    { id: 'eventoDesencadeante', text: 'Houve algum *evento específico* que desencadeou os sintomas?\n\n(queda, esforço, estresse, etc. ou "não")' },
    
    // === INVESTIGAÇÃO DA DOR ===
    { id: 'temDor', text: '💢 *INVESTIGAÇÃO DA DOR*\n\nVocê sente dor?\n\n1️⃣ Sim\n2️⃣ Não', options: ['sim', 'nao'] },
    { id: 'dorLocal', text: 'Onde você sente dor? (ex: 1,3,5)\n\n1️⃣ Pescoço/Cervical\n2️⃣ Meio das costas\n3️⃣ Lombar\n4️⃣ Glúteo/Quadril\n5️⃣ Perna\n6️⃣ Braço\n7️⃣ Cabeça', options: ['cervical', 'toracica', 'lombar', 'gluteo', 'perna', 'braco', 'cabeca'], multi: true, condition: (d) => d.temDor === 'sim' },
    { id: 'dorIntensidade', text: 'Intensidade média da dor (0-10):', condition: (d) => d.temDor === 'sim' },
    { id: 'dorTipo', text: 'Como é sua dor? (ex: 1,3)\n\n1️⃣ Queimação\n2️⃣ Pontada\n3️⃣ Peso/Pressão\n4️⃣ Choque\n5️⃣ Formigamento\n6️⃣ Latejante', options: ['queimacao', 'pontada', 'peso', 'choque', 'formigamento', 'latejante'], multi: true, condition: (d) => d.temDor === 'sim' },
    
    // === SINAIS DE ALERTA ===
    { id: 'redFlags', text: '⚠️ *SINTOMAS IMPORTANTES*\n\n0️⃣ Nenhum\n1️⃣ Fraqueza pernas\n2️⃣ Fraqueza braços\n3️⃣ Dificuldade urina\n4️⃣ Dificuldade fezes\n5️⃣ Dormência genital\n6️⃣ Perda equilíbrio\n7️⃣ Dor noturna\n8️⃣ Febre\n9️⃣ Perda peso', options: ['nenhum', 'fraqueza_pernas', 'fraqueza_bracos', 'dif_urina', 'dif_fezes', 'dormencia_genital', 'perda_equilibrio', 'dor_noturna', 'febre', 'perda_peso'], multi: true },
    
    // === SONO E ESTRESSE ===
    { id: 'sonoQualidade', text: '😴 *SONO*\n\nComo acorda?\n\n1️⃣ Descansado\n2️⃣ Pouco cansado\n3️⃣ Cansado\n4️⃣ Exausto', options: ['descansado', 'pouco_cansado', 'cansado', 'exausto'] },
    { id: 'horasDormidas', text: 'Horas de sono/noite?\n\n1️⃣ <5h\n2️⃣ 5-6h\n3️⃣ 6-7h\n4️⃣ 7-8h\n5️⃣ >8h', options: ['menos_5', '5_6', '6_7', '7_8', 'mais_8'] },
    { id: 'estresseNivel', text: 'Estresse (0-10):' },
    
    // === FUNÇÃO GI ===
    { id: 'frequenciaEvacuacao', text: '🦠 *FUNÇÃO INTESTINAL*\n\nEvacuações/semana?\n\n1️⃣ <3x\n2️⃣ 3-7x\n3️⃣ 7-14x\n4️⃣ >14x', options: ['menos_3', '3_7', '7_14', 'mais_14'] },
    { id: 'escalaBristol', text: 'Fezes?\n\n1️⃣ Duras/bolinhas\n2️⃣ Salsicha (ideal)\n3️⃣ Moles/pastosas\n4️⃣ Líquidas', options: ['tipo_1_2', 'tipo_3_4', 'tipo_5_6', 'tipo_7'] },
    { id: 'esforcoEvacuar', text: 'Força p/ evacuar?\n\n1️⃣ Não\n2️⃣ Às vezes\n3️⃣ Sempre', options: ['nao', 'as_vezes', 'sempre'] },
    { id: 'distensaoAbdominal', text: 'Barriga inchada?\n\n1️⃣ Não\n2️⃣ Às vezes\n3️⃣ Frequente\n4️⃣ Sempre', options: ['nao', 'as_vezes', 'frequente', 'sempre'] },
    { id: 'flatulencia', text: 'Gases?\n\n1️⃣ Normal\n2️⃣ Aumentado\n3️⃣ Muito aumentado', options: ['normal', 'aumentado', 'muito_aumentado'] },
    { id: 'siboTriggers', text: 'O que piora? (0=nada)\n\n0️⃣ Nada\n1️⃣ Carboidratos\n2️⃣ Fibras\n3️⃣ Leite\n4️⃣ Feijão/cebola\n5️⃣ Jejum melhora', options: ['nenhum', 'carbo', 'fibra', 'lactose', 'fodmap', 'jejum_melhora'], multi: true },
    { id: 'usoAntibiotico', text: 'Antibióticos (6 meses)?\n\n1️⃣ Não\n2️⃣ 1x\n3️⃣ 2-3x\n4️⃣ >3x', options: ['nao', '1_vez', '2_3_vezes', 'mais_3'] },
    { id: 'usoIBP', text: 'Omeprazol/pantoprazol?\n\n1️⃣ Não\n2️⃣ Eventual\n3️⃣ Contínuo', options: ['nao', 'eventual', 'continuo'] },
    
    // === HISTÓRICO ===
    { id: 'condicoes', text: '🏥 *HISTÓRICO*\n\nCondições? (0=nenhuma)\n\n0️⃣ Nenhuma\n1️⃣ Diabetes\n2️⃣ Hipertensão\n3️⃣ Colesterol\n4️⃣ Depressão\n5️⃣ Tireoide\n6️⃣ Hérnia disco\n7️⃣ Osteoporose', options: ['nenhuma', 'diabetes', 'hipertensao', 'colesterol', 'depressao', 'tireoide', 'hernia', 'osteoporose'], multi: true },
    { id: 'medicamentos', text: 'Medicamentos? (ou "nenhum")' },
    { id: 'alergias', text: 'Alergias? (ou "nenhuma")' },
    { id: 'cirurgias', text: 'Cirurgias anteriores? (ou "nenhuma")' },
    
    // === TRATAMENTOS ===
    { id: 'tratamentos', text: '💪 *TRATAMENTOS*\n\n0️⃣ Nenhum\n1️⃣ Medicações\n2️⃣ Fisio\n3️⃣ Acupuntura\n4️⃣ Infiltração\n5️⃣ Cirurgia\n6️⃣ Pilates', options: ['nenhum', 'medicacoes', 'fisio', 'acupuntura', 'infiltracao', 'cirurgia', 'pilates'], multi: true },
    { id: 'atividadeFisica', text: 'Atividade física?\n\n1️⃣ Não\n2️⃣ 1-2x/sem\n3️⃣ 3-4x/sem\n4️⃣ 5+x/sem', options: ['nao', '1_2x', '3_4x', '5_mais'] },
    { id: 'tabagismo', text: 'Fuma?\n\n1️⃣ Nunca\n2️⃣ Ex-fumante\n3️⃣ Sim', options: ['nunca', 'ex_fumante', 'fumante'] },
    { id: 'alcool', text: 'Álcool?\n\n1️⃣ Não\n2️⃣ Ocasional\n3️⃣ Semanal\n4️⃣ Diário', options: ['nao', 'ocasional', 'semanal', 'diario'] },
    
    // === NDI (Cervical) ===
    { id: 'ndi_intro', text: '📊 *NDI - Índice de Incapacidade Cervical*\n\nComo você tem dor no pescoço, vamos avaliar o impacto nas suas atividades.\n\nDigite OK para continuar.', condition: temDorCervical },
    { id: 'ndi_1', text: '*NDI 1/10 - Intensidade da dor no pescoço*\n\n0️⃣ Sem dor agora\n1️⃣ Muito leve\n2️⃣ Moderada\n3️⃣ Forte\n4️⃣ Muito forte\n5️⃣ Pior imaginável', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_2', text: '*NDI 2/10 - Cuidados pessoais*\n\n0️⃣ Normal, sem dor\n1️⃣ Normal, com dor\n2️⃣ Doloroso, sou lento\n3️⃣ Preciso ajuda parcial\n4️⃣ Preciso ajuda diária\n5️⃣ Não consigo me vestir', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_3', text: '*NDI 3/10 - Levantar coisas*\n\n0️⃣ Pesados sem dor\n1️⃣ Pesados com dor\n2️⃣ Só se bem posicionados\n3️⃣ Só leves/moderados\n4️⃣ Só muito leves\n5️⃣ Não consigo nada', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_4', text: '*NDI 4/10 - Leitura*\n\n0️⃣ Sem dor\n1️⃣ Dor leve\n2️⃣ Dor moderada\n3️⃣ Limitado pela dor\n4️⃣ Mal consigo ler\n5️⃣ Não consigo', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_5', text: '*NDI 5/10 - Dor de cabeça*\n\n0️⃣ Não tenho\n1️⃣ Leve, pouco frequente\n2️⃣ Moderada, pouco frequente\n3️⃣ Moderada, frequente\n4️⃣ Forte, frequente\n5️⃣ Quase sempre', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_6', text: '*NDI 6/10 - Concentração*\n\n0️⃣ Total\n1️⃣ Dificuldade leve\n2️⃣ Dificuldade razoável\n3️⃣ Muita dificuldade\n4️⃣ Imensa dificuldade\n5️⃣ Não consigo', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_7', text: '*NDI 7/10 - Trabalho*\n\n0️⃣ Quanto quiser\n1️⃣ Só o habitual\n2️⃣ Maior parte\n3️⃣ Não consigo habitual\n4️⃣ Mal consigo\n5️⃣ Não consigo nada', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_8', text: '*NDI 8/10 - Dirigir*\n\n0️⃣ Sem dor\n1️⃣ Dor leve\n2️⃣ Dor moderada\n3️⃣ Limitado pela dor\n4️⃣ Mal consigo\n5️⃣ Não consigo', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_9', text: '*NDI 9/10 - Sono*\n\n0️⃣ Sem problemas\n1️⃣ <1h sem dormir\n2️⃣ 1-2h sem dormir\n3️⃣ 2-3h sem dormir\n4️⃣ 3-5h sem dormir\n5️⃣ 5-7h sem dormir', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    { id: 'ndi_10', text: '*NDI 10/10 - Lazer*\n\n0️⃣ Tudo sem dor\n1️⃣ Tudo com dor\n2️⃣ Maioria\n3️⃣ Poucas\n4️⃣ Mal consigo\n5️⃣ Nenhuma', options: ['0','1','2','3','4','5'], condition: temDorCervical },
    
    // === ODI (Lombar) ===
    { id: 'odi_intro', text: '📊 *ODI - Índice de Incapacidade Lombar*\n\nComo você tem dor lombar, vamos avaliar o impacto nas suas atividades.\n\nDigite OK para continuar.', condition: temDorLombar },
    { id: 'odi_1', text: '*ODI 1/10 - Intensidade da dor*\n\n0️⃣ Tolero sem analgésico\n1️⃣ Forte, mas sem analgésico\n2️⃣ Analgésico alivia total\n3️⃣ Analgésico alivia moderado\n4️⃣ Analgésico alivia pouco\n5️⃣ Analgésico não funciona', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_2', text: '*ODI 2/10 - Cuidados pessoais*\n\n0️⃣ Normal, sem dor\n1️⃣ Normal, com dor\n2️⃣ Doloroso, sou lento\n3️⃣ Preciso ajuda parcial\n4️⃣ Preciso ajuda diária\n5️⃣ Fico na cama', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_3', text: '*ODI 3/10 - Levantar objetos*\n\n0️⃣ Pesados sem dor\n1️⃣ Pesados com dor\n2️⃣ Não do chão\n3️⃣ Só se bem posicionados\n4️⃣ Só muito leves\n5️⃣ Nada', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_4', text: '*ODI 4/10 - Andar*\n\n0️⃣ Qualquer distância\n1️⃣ Até 1,5km\n2️⃣ Até 800m\n3️⃣ Até 400m\n4️⃣ Só com bengala\n5️⃣ Fico na cama', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_5', text: '*ODI 5/10 - Sentar*\n\n0️⃣ Quanto quiser\n1️⃣ Cadeira favorita\n2️⃣ Até 1 hora\n3️⃣ Até 30 min\n4️⃣ Até 10 min\n5️⃣ Não consigo', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_6', text: '*ODI 6/10 - Ficar em pé*\n\n0️⃣ Quanto quiser, sem dor\n1️⃣ Quanto quiser, com dor\n2️⃣ Até 1 hora\n3️⃣ Até 30 min\n4️⃣ Até 10 min\n5️⃣ Não consigo', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_7', text: '*ODI 7/10 - Sono*\n\n0️⃣ Não perturbado\n1️⃣ Ocasionalmente\n2️⃣ <6h de sono\n3️⃣ <4h de sono\n4️⃣ <2h de sono\n5️⃣ Não durmo', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_8', text: '*ODI 8/10 - Vida sexual*\n\n0️⃣ Normal, sem dor\n1️⃣ Normal, com dor\n2️⃣ Quase normal, dolorosa\n3️⃣ Restrita\n4️⃣ Quase inexistente\n5️⃣ Impossível', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_9', text: '*ODI 9/10 - Vida social*\n\n0️⃣ Normal, sem dor\n1️⃣ Normal, com dor\n2️⃣ Exceto físicas\n3️⃣ Restrita\n4️⃣ Só em casa\n5️⃣ Não tenho', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    { id: 'odi_10', text: '*ODI 10/10 - Viajar*\n\n0️⃣ Sem dor\n1️⃣ Com dor\n2️⃣ >2h ok\n3️⃣ <1h\n4️⃣ <30min\n5️⃣ Só p/ tratamento', options: ['0','1','2','3','4','5'], condition: temDorLombar },
    
    // === EXPECTATIVAS ===
    { id: 'expectativas', text: '🎯 *EXPECTATIVAS*\n\nO que você espera da consulta? Qual seu objetivo?' },
];

function getNextQuestion(session) {
    for (let i = session.currentQuestion; i < QUESTIONS.length; i++) {
        const q = QUESTIONS[i];
        if (q.condition && !q.condition(session.data)) continue;
        return { question: q, index: i };
    }
    return null;
}

function parseAnswer(question, text) {
    text = text.trim();
    if (question.id.includes('_intro')) return 'ok';
    
    if (question.options) {
        if (question.multi) {
            const nums = text.split(/[,\s]+/).map(n => parseInt(n.trim()));
            return nums.filter(n => !isNaN(n) && n >= 0 && n <= question.options.length)
                       .map(n => n === 0 ? question.options[0] : question.options[n - 1])
                       .filter((v, i, a) => a.indexOf(v) === i);
        } else {
            const num = parseInt(text);
            if (question.id.startsWith('ndi_') || question.id.startsWith('odi_')) {
                if (num >= 0 && num <= 5) return String(num);
                return null;
            }
            if (num >= 1 && num <= question.options.length) {
                return question.options[num - 1];
            }
            return null;
        }
    }
    return text;
}

function calcNDI(data) {
    let total = 0;
    for (let i = 1; i <= 10; i++) {
        const val = parseInt(data[`ndi_${i}`] || '0');
        if (!isNaN(val)) total += val;
    }
    const pct = Math.round((total / 50) * 100);
    let interp = '';
    if (pct <= 8) interp = 'Sem incapacidade';
    else if (pct <= 28) interp = 'Incapacidade leve';
    else if (pct <= 48) interp = 'Incapacidade moderada';
    else if (pct <= 68) interp = 'Incapacidade severa';
    else interp = 'Incapacidade completa';
    return { total, pct, interp };
}

function calcODI(data) {
    let total = 0;
    for (let i = 1; i <= 10; i++) {
        const val = parseInt(data[`odi_${i}`] || '0');
        if (!isNaN(val)) total += val;
    }
    const pct = Math.round((total / 50) * 100);
    let interp = '';
    if (pct <= 20) interp = 'Incapacidade mínima';
    else if (pct <= 40) interp = 'Incapacidade moderada';
    else if (pct <= 60) interp = 'Incapacidade severa';
    else if (pct <= 80) interp = 'Invalidez';
    else interp = 'Acamado';
    return { total, pct, interp };
}

function generateSummary(data) {
    let s = `📋 *RESUMO DA ANAMNESE*\n━━━━━━━━━━━━━━━━━━━\n\n`;
    s += `👤 *Paciente:* ${data.nome || '-'}\n`;
    s += `📅 *Nascimento:* ${data.dataNascimento || '-'}\n`;
    s += `👔 *Profissão:* ${data.profissao || '-'}\n\n`;
    s += `🎯 *Queixa:* ${data.queixaPrincipal || '-'}\n`;
    s += `⏱️ *Tempo:* ${data.tempoProblema || '-'}\n\n`;
    
    if (data.temDor === 'sim') {
        s += `💢 *Dor:* ${Array.isArray(data.dorLocal) ? data.dorLocal.join(', ') : data.dorLocal || '-'}\n`;
        s += `📊 *Intensidade:* ${data.dorIntensidade || '-'}/10\n\n`;
    }
    
    if (data.redFlags && !data.redFlags.includes('nenhum')) {
        s += `⚠️ *Red Flags:* ${Array.isArray(data.redFlags) ? data.redFlags.join(', ') : data.redFlags}\n\n`;
    }
    
    // NDI
    if (data.ndi_1) {
        const ndi = calcNDI(data);
        s += `📊 *NDI:* ${ndi.total}/50 (${ndi.pct}%) - ${ndi.interp}\n`;
    }
    
    // ODI
    if (data.odi_1) {
        const odi = calcODI(data);
        s += `📊 *ODI:* ${odi.total}/50 (${odi.pct}%) - ${odi.interp}\n`;
    }
    
    s += `\n🦠 *Evacuação:* ${data.frequenciaEvacuacao || '-'}\n`;
    s += `💨 *Distensão:* ${data.distensaoAbdominal || '-'}\n\n`;
    s += `💊 *Medicamentos:* ${data.medicamentos || '-'}\n`;
    s += `🎯 *Expectativas:* ${data.expectativas || '-'}\n`;
    
    return s;
}

async function saveAnamnese(data, phone) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const nome = (data.nome || 'paciente').replace(/\s+/g, '_').substring(0, 30);
    const filename = `anamnese_whatsapp_${nome}_${timestamp}.json`;
    const filepath = path.join(ANAMNESES_DIR, filename);
    
    if (!fs.existsSync(ANAMNESES_DIR)) fs.mkdirSync(ANAMNESES_DIR, { recursive: true });
    
    // Calcular scores
    if (data.ndi_1) data.ndi_score = calcNDI(data);
    if (data.odi_1) data.odi_score = calcODI(data);
    
    fs.writeFileSync(filepath, JSON.stringify({ source: 'whatsapp', phone, timestamp: new Date().toISOString(), data }, null, 2));
    console.log(`✅ Anamnese salva: ${filename}`);
    return filepath;
}

// Número para pairing code (sem +, só números, com código do país)
const PAIRING_PHONE = '5511930488315';
const USE_PAIRING_CODE = true; // Usar código de 8 dígitos em vez de QR

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './wwebjs_auth' }),
    puppeteer: { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'] }
});

client.on('qr', async (qr) => {
    if (USE_PAIRING_CODE) {
        console.log('📱 Aguardando pairing code...');
        // QR chegou mas vamos ignorar e esperar o pairing code
        await qrcode.toFile('./qr-code.png', qr, { width: 400, margin: 2 });
        console.log('(QR salvo como backup em qr-code.png)');
    } else {
        console.log('📱 QR Code recebido!');
        await qrcode.toFile('./qr-code.png', qr, { width: 400, margin: 2 });
        console.log('✅ QR salvo\n');
    }
});

// Gerar pairing code assim que o cliente estiver pronto para autenticação
client.on('loading_screen', async (percent, message) => {
    console.log(`Carregando: ${percent}% - ${message}`);
});

// Tentar gerar pairing code após inicialização
setTimeout(async () => {
    if (USE_PAIRING_CODE && !client.info) {
        try {
            console.log('🔢 Solicitando código de pareamento...');
            const pairingCode = await client.requestPairingCode(PAIRING_PHONE, true);
            console.log(`\n✅ CÓDIGO DE PAREAMENTO: ${pairingCode}\n`);
            console.log('No WhatsApp do (11) 93048-8315:');
            console.log('Configurações → Dispositivos conectados → Conectar dispositivo → Conectar com número\n');
            fs.writeFileSync('./pairing-code.txt', pairingCode);
        } catch (err) {
            console.error('Erro ao gerar pairing code:', err.message);
            console.log('Use o QR code em qr-code.png como alternativa');
        }
    }
}, 15000);

client.on('ready', () => console.log('✅ BOT CONECTADO!\n'));
client.on('authenticated', () => console.log('🔐 Autenticado!'));

client.on('message_create', async (msg) => {
    // Ignorar mensagens enviadas pelo próprio bot
    if (msg.fromMe) return;
    
    const phone = msg.from;
    let text = (msg.body || '').toLowerCase().trim();
    
    console.log(`📨 Mensagem recebida de ${phone} | tipo: ${msg.type} | hasMedia: ${msg.hasMedia}`);
    
    // === MODO ADMIN: Felipe - apenas transcrição de áudio ===
    if (ADMIN_PHONES.includes(phone) && msg.hasMedia && (msg.type === 'audio' || msg.type === 'ptt')) {
        console.log(`🎤 [ADMIN] ${phone}: [ÁUDIO]`);
        try {
            const media = await msg.downloadMedia();
            if (media && media.data) {
                const audioBuffer = Buffer.from(media.data, 'base64');
                await msg.reply('🎧 Transcrevendo...');
                const transcribed = await transcribeAudio(audioBuffer, media.mimetype);
                if (transcribed) {
                    console.log(`📝 [ADMIN] Transcrição: ${transcribed}`);
                    await msg.reply(`📝 *Transcrição:*\n\n${transcribed}`);
                } else {
                    await msg.reply('❌ Não consegui transcrever o áudio.');
                }
            }
        } catch (err) {
            console.error('Erro ao processar áudio admin:', err);
            await msg.reply('❌ Erro ao processar áudio.');
        }
        return; // Admin não entra no fluxo de anamnese
    }
    
    // === MODO PACIENTE: Transcrever e processar como resposta ===
    if (msg.hasMedia && (msg.type === 'audio' || msg.type === 'ptt')) {
        console.log(`🎤 ${phone}: [ÁUDIO]`);
        try {
            const media = await msg.downloadMedia();
            if (media && media.data) {
                const audioBuffer = Buffer.from(media.data, 'base64');
                await msg.reply('🎧 Transcrevendo áudio...');
                const transcribed = await transcribeAudio(audioBuffer, media.mimetype);
                if (transcribed) {
                    console.log(`📝 Transcrição: ${transcribed}`);
                    text = transcribed.toLowerCase().trim();
                    // Confirmar transcrição
                    await msg.reply(`📝 *Entendi:* "${transcribed}"\n\n_(Processando como sua resposta)_`);
                } else {
                    await msg.reply('❌ Não consegui transcrever o áudio. Por favor, digite sua resposta.');
                    return;
                }
            }
        } catch (err) {
            console.error('Erro ao processar áudio:', err);
            await msg.reply('❌ Erro ao processar áudio. Por favor, digite sua resposta.');
            return;
        }
    }
    
    console.log(`📩 ${phone}: ${text.substring(0, 50)}`);
    
    if (text === 'anamnese' || text === 'começar' || text === 'iniciar' || text === 'comecar') {
        sessions[phone] = { currentQuestion: 0, data: {}, startedAt: new Date().toISOString() };
        saveSessions();
        const next = getNextQuestion(sessions[phone]);
        await msg.reply(next.question.text);
        return;
    }
    
    if (text === 'cancelar') {
        delete sessions[phone];
        saveSessions();
        await msg.reply('❌ Cancelado. Digite *anamnese* para recomeçar.');
        return;
    }
    
    if (sessions[phone]) {
        const session = sessions[phone];
        const nextQ = getNextQuestion(session);
        if (!nextQ) return;
        
        // Verificar se é pergunta NDI/ODI (não pode pular)
        const isNdiOdi = nextQ.question.id.startsWith('ndi_') || nextQ.question.id.startsWith('odi_');
        
        // Comando pular
        if (text === 'pular' || text === 'pula') {
            if (isNdiOdi) {
                await msg.reply('⚠️ Esta pergunta faz parte do questionário de avaliação e não pode ser pulada.');
                return;
            }
            session.data[nextQ.question.id] = null; // Marca como pulada
            session.currentQuestion = nextQ.index + 1;
            saveSessions();
            
            const next = getNextQuestion(session);
            if (next) {
                await msg.reply(next.question.text);
            }
            return;
        }
        
        const answer = parseAnswer(nextQ.question, msg.body);
        
        if (answer === null && nextQ.question.options) {
            const skipHint = isNdiOdi ? '' : ' Ou digite *pular* para ir à próxima.';
            await msg.reply('⚠️ Resposta inválida. Digite o número.' + skipHint);
            return;
        }
        
        session.data[nextQ.question.id] = answer;
        session.currentQuestion = nextQ.index + 1;
        saveSessions();
        
        const next = getNextQuestion(session);
        
        if (next) {
            await msg.reply(next.question.text);
        } else {
            // Calcular scores antes de salvar
            if (session.data.ndi_1) session.data.ndi_score = calcNDI(session.data);
            if (session.data.odi_1) session.data.odi_score = calcODI(session.data);
            
            // Mostrar resumo
            const summary = generateSummary(session.data);
            await msg.reply(summary);
            await msg.reply('⏳ Gerando PDF e salvando dados...');
            
            // Salvar JSON local
            await saveAnamnese(session.data, phone);
            
            // Gerar PDF
            const pdfPath = await generatePDF(session.data);
            
            // Salvar no Supabase
            await saveToSupabase(session.data, phone);
            
            // Enviar email pro Felipe
            await sendEmailWithPDF(session.data, pdfPath);
            
            // Enviar PDF pro paciente via WhatsApp
            try {
                const pdfMedia = MessageMedia.fromFilePath(pdfPath);
                await msg.reply(pdfMedia, null, { caption: '📄 Sua anamnese em PDF' });
            } catch (e) {
                console.error('Erro enviando PDF:', e.message);
            }
            
            await msg.reply('✅ *Anamnese concluída!*\n\nSeus dados foram salvos e o Dr. Felipe já recebeu por email.\n\nObrigado! 🙏');
            delete sessions[phone];
            saveSessions();
        }
        return;
    }
    
    if (text.match(/^(oi|olá|ola|bom dia|boa tarde|boa noite|opa)$/)) {
        await msg.reply('👋 Olá! Sou o assistente do *Dr. Felipe Barreto*.\n\nDigite *anamnese* para começar.\n\n💡 _Digite *cancelar* para recomeçar ou *pular* para pular perguntas._');
    }
});

console.log('Inicializando...');
client.initialize();

/**
 * ANAMNESE WEBAPP - Dr. Felipe Barreto
 * Form handling and PDF generation
 */

// ============================================
// STATE & ELEMENTS
// ============================================

let currentStep = 1;
const totalSteps = 8;
let formData = {};

const elements = {
    form: document.getElementById('anamneseForm'),
    progressFill: document.getElementById('progressFill'),
    currentStepEl: document.getElementById('currentStep'),
    totalStepsEl: document.getElementById('totalSteps'),
    btnAnterior: document.getElementById('btnAnterior'),
    btnProximo: document.getElementById('btnProximo'),
    btnEnviar: document.getElementById('btnEnviar'),
    successContainer: document.getElementById('successContainer'),
    btnDownloadPDF: document.getElementById('btnDownloadPDF')
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    elements.totalStepsEl.textContent = totalSteps;
    updateProgress();
    setupEventListeners();
    setupConditionalFields();
});

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Navigation
    elements.btnProximo.addEventListener('click', nextStep);
    elements.btnAnterior.addEventListener('click', prevStep);
    elements.form.addEventListener('submit', handleSubmit);
    elements.btnDownloadPDF.addEventListener('click', generatePDF);
    
    // Sliders
    const dorSlider = document.getElementById('dorIntensidade');
    const estresseSlider = document.getElementById('estresseNivel');
    
    if (dorSlider) {
        dorSlider.addEventListener('input', (e) => {
            document.getElementById('dorValor').textContent = e.target.value;
        });
    }
    
    if (estresseSlider) {
        estresseSlider.addEventListener('input', (e) => {
            document.getElementById('estresseValor').textContent = e.target.value;
        });
    }
    
    // "Sem dor" checkbox logic
    const semDorCheckbox = document.getElementById('semDor');
    if (semDorCheckbox) {
        semDorCheckbox.addEventListener('change', handleSemDor);
    }
    
    // "Nenhum" checkbox exclusivity
    ['nenhumRedFlag', 'nenhumaCondicao', 'nenhumTratamento'].forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', handleNenhumCheckbox);
        }
    });
    
    // Medicamentos conditional
    const usaMedicamentos = document.getElementById('usaMedicamentos');
    if (usaMedicamentos) {
        usaMedicamentos.addEventListener('change', handleMedicamentosChange);
    }
}

function setupConditionalFields() {
    // Check initial state of "sem dor"
    handleSemDor();
}

// ============================================
// NAVIGATION
// ============================================

function nextStep() {
    if (!validateCurrentStep()) return;
    
    if (currentStep < totalSteps) {
        goToStep(currentStep + 1);
    }
}

function prevStep() {
    if (currentStep > 1) {
        goToStep(currentStep - 1);
    }
}

function goToStep(step) {
    // Hide current step
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.remove('active');
    
    // Show new step
    currentStep = step;
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');
    
    updateProgress();
    updateButtons();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgress() {
    const progress = (currentStep / totalSteps) * 100;
    elements.progressFill.style.width = `${progress}%`;
    elements.currentStepEl.textContent = currentStep;
}

function updateButtons() {
    elements.btnAnterior.style.display = currentStep > 1 ? 'block' : 'none';
    elements.btnProximo.style.display = currentStep < totalSteps ? 'block' : 'none';
    elements.btnEnviar.style.display = currentStep === totalSteps ? 'block' : 'none';
}

// ============================================
// VALIDATION
// ============================================

function validateCurrentStep() {
    const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    const requiredFields = currentStepEl.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
        
        // Special handling for checkboxes
        if (field.type === 'checkbox' && !field.checked) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        // Find first invalid field and focus
        const firstInvalid = currentStepEl.querySelector('.error, [required]:invalid');
        if (firstInvalid) {
            firstInvalid.focus();
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        alert('Por favor, preencha todos os campos obrigatórios.');
    }
    
    return isValid;
}

// ============================================
// CONDITIONAL LOGIC
// ============================================

function handleSemDor() {
    const semDorCheckbox = document.getElementById('semDor');
    const dorDependentes = document.querySelectorAll('.dor-dependente');
    const dorCheckboxes = document.querySelectorAll('input[name="dorLocal"]:not(#semDor)');
    
    if (semDorCheckbox && semDorCheckbox.checked) {
        dorDependentes.forEach(el => el.style.display = 'none');
        dorCheckboxes.forEach(cb => {
            cb.checked = false;
            cb.disabled = true;
        });
    } else {
        dorDependentes.forEach(el => el.style.display = 'block');
        dorCheckboxes.forEach(cb => cb.disabled = false);
    }
}

function handleNenhumCheckbox(e) {
    const checkbox = e.target;
    const name = checkbox.name || checkbox.id.replace('nenhum', '').replace('Condicao', 'condicoes').replace('Tratamento', 'tratamentos').replace('RedFlag', 'redFlags').toLowerCase();
    
    // Map checkbox IDs to their corresponding group names
    const groupMap = {
        'nenhumRedFlag': 'redFlags',
        'nenhumaCondicao': 'condicoes',
        'nenhumTratamento': 'tratamentos'
    };
    
    const groupName = groupMap[checkbox.id];
    if (!groupName) return;
    
    const siblingCheckboxes = document.querySelectorAll(`input[name="${groupName}"]:not(#${checkbox.id})`);
    
    if (checkbox.checked) {
        siblingCheckboxes.forEach(cb => {
            cb.checked = false;
        });
    }
}

function handleMedicamentosChange() {
    const usaMedicamentos = document.getElementById('usaMedicamentos');
    const medicamentosDependente = document.querySelector('.medicamentos-dependente');
    
    if (usaMedicamentos.value === 'sim') {
        medicamentosDependente.style.display = 'block';
    } else {
        medicamentosDependente.style.display = 'none';
    }
}

// ============================================
// CONFIGURATION
// ============================================

// Backend API no VPS
// Tentar HTTPS primeiro, fallback para HTTP
const API_URL = 'https://api.felipebarretoneuro.com.br/api';

// ============================================
// FORM SUBMISSION
// ============================================

async function handleSubmit(e) {
    e.preventDefault();
    
    if (!validateCurrentStep()) return;
    
    // Collect all form data
    collectFormData();
    
    // Show loading state
    elements.btnEnviar.disabled = true;
    elements.btnEnviar.textContent = '⏳ Enviando...';
    
    try {
        // Send to backend
        const response = await fetch(API_URL + '/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show success
            elements.form.style.display = 'none';
            document.querySelector('.progress-container').style.display = 'none';
            elements.successContainer.style.display = 'block';
            
            // Update success message based on email status
            const successMessage = document.querySelector('.success-message');
            if (successMessage) {
                if (result.email_sent) {
                    successMessage.innerHTML = `
                        <h2>✅ Anamnese enviada com sucesso!</h2>
                        <p>Suas respostas foram salvas e enviadas para o Dr. Felipe.</p>
                        <p>Ele irá revisar antes da sua consulta.</p>
                    `;
                } else {
                    successMessage.innerHTML = `
                        <h2>✅ Anamnese salva!</h2>
                        <p>Suas respostas foram salvas no sistema.</p>
                        <p class="warning">⚠️ Houve um problema ao enviar o email, mas não se preocupe - suas informações estão seguras.</p>
                    `;
                }
            }
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Also generate local PDF for user
            setTimeout(() => {
                generatePDF();
            }, 1000);
        } else {
            throw new Error(result.error || 'Erro ao enviar');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        
        // Fallback: save locally if backend fails
        alert('Houve um problema ao enviar para o servidor. Gerando PDF local...');
        
        elements.form.style.display = 'none';
        document.querySelector('.progress-container').style.display = 'none';
        elements.successContainer.style.display = 'block';
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        setTimeout(() => {
            generatePDF();
        }, 500);
    } finally {
        elements.btnEnviar.disabled = false;
        elements.btnEnviar.textContent = '📤 Enviar Anamnese';
    }
}

function collectFormData() {
    const form = elements.form;
    
    // Text inputs, selects, textareas
    const inputs = form.querySelectorAll('input:not([type="checkbox"]), select, textarea');
    inputs.forEach(input => {
        if (input.name && input.value) {
            formData[input.name] = input.value;
        }
    });
    
    // Checkboxes - group by name
    const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach(cb => {
        if (cb.name) {
            if (!formData[cb.name]) {
                formData[cb.name] = [];
            }
            if (Array.isArray(formData[cb.name])) {
                formData[cb.name].push(cb.value);
            }
        }
    });
    
    // Add timestamp
    formData.dataPreenchimento = new Date().toLocaleString('pt-BR');
    
    console.log('Form data collected:', formData);
}

// ============================================
// PDF GENERATION
// ============================================

function generatePDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);
    let y = 20;
    
    // Helper functions
    function addTitle(text) {
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(37, 99, 235);
        doc.text(text, margin, y);
        y += 10;
    }
    
    function addSection(title) {
        checkPageBreak(20);
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(30, 41, 59);
        doc.text(title, margin, y);
        y += 7;
    }
    
    function addField(label, value) {
        if (!value || value === '') return;
        checkPageBreak(15);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(100, 116, 139);
        doc.text(label + ':', margin, y);
        
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(30, 41, 59);
        
        const valueStr = Array.isArray(value) ? value.join(', ') : String(value);
        const lines = doc.splitTextToSize(valueStr, contentWidth - 40);
        doc.text(lines, margin + 50, y);
        y += 6 * Math.max(1, lines.length);
    }
    
    function addLine() {
        doc.setDrawColor(226, 232, 240);
        doc.line(margin, y, pageWidth - margin, y);
        y += 5;
    }
    
    function checkPageBreak(needed) {
        if (y + needed > doc.internal.pageSize.getHeight() - 20) {
            doc.addPage();
            y = 20;
        }
    }
    
    // === HEADER ===
    doc.setFillColor(37, 99, 235);
    doc.rect(0, 0, pageWidth, 40, 'F');
    
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('ANAMNESE PRÉ-CONSULTA', margin, 18);
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Dr. Felipe Barreto - Neurocirurgia de Coluna | Medicina Funcional', margin, 28);
    
    doc.setFontSize(10);
    doc.text('Data: ' + formData.dataPreenchimento, margin, 36);
    
    y = 55;
    
    // === IDENTIFICAÇÃO ===
    addSection('📋 IDENTIFICAÇÃO');
    addField('Nome', formData.nome);
    addField('Data Nasc.', formData.dataNascimento);
    addField('Sexo', formData.sexo);
    addField('Profissão', formData.profissao);
    addField('Telefone', formData.telefone);
    addLine();
    
    // === QUEIXA PRINCIPAL ===
    addSection('🎯 QUEIXA PRINCIPAL');
    addField('Queixa', formData.queixaPrincipal);
    addField('Tempo', translateValue('tempoProblema', formData.tempoProblema));
    addField('Evento', formData.eventoDesencadeante);
    addLine();
    
    // === DOR ===
    addSection('💢 INVESTIGAÇÃO DA DOR');
    addField('Localização', translateArray(formData.dorLocal));
    if (!formData.dorLocal?.includes('sem_dor')) {
        addField('Intensidade', formData.dorIntensidade + '/10');
        addField('Tipo', translateArray(formData.dorTipo));
        addField('Duração', translateValue('dorDuracao', formData.dorDuracao));
        addField('Irradiação', translateValue('dorIrradiacao', formData.dorIrradiacao));
    }
    addLine();
    
    // === SINAIS DE ALERTA ===
    addSection('⚠️ SINAIS DE ALERTA');
    const redFlags = formData.redFlags || [];
    if (redFlags.includes('nenhum') || redFlags.length === 0) {
        addField('Status', '✅ Nenhum sinal de alerta');
    } else {
        doc.setTextColor(239, 68, 68);
        addField('ATENÇÃO', translateArray(redFlags));
        doc.setTextColor(30, 41, 59);
    }
    addLine();
    
    // === SONO E ESTRESSE ===
    addSection('😴 SONO E ESTRESSE');
    addField('Qualidade sono', translateValue('sonoQualidade', formData.sonoQualidade));
    addField('Despertares', translateValue('sonoDespertares', formData.sonoDespertares));
    addField('Horário', (formData.horaDeitar || '-') + ' às ' + (formData.horaAcordar || '-'));
    addField('Estresse', formData.estresseNivel + '/10');
    addField('Fator', formData.estresseFator);
    addLine();
    
    // === HISTÓRICO ===
    checkPageBreak(40);
    addSection('🏥 HISTÓRICO MÉDICO');
    addField('Condições', translateArray(formData.condicoes));
    addField('Outras', formData.outrasCondicoes);
    addField('Medicamentos', formData.usaMedicamentos === 'sim' ? formData.medicamentosLista : 'Não usa');
    addField('Alergias', formData.alergias || 'Não informado');
    addField('Cirurgias', formData.cirurgiasAnteriores || 'Nenhuma');
    addLine();
    
    // === TRATAMENTOS ===
    addSection('💪 TRATAMENTOS E HÁBITOS');
    addField('Tratamentos', translateArray(formData.tratamentos));
    addField('Resultado', translateValue('resultadoTratamentos', formData.resultadoTratamentos));
    addField('Atividade', translateValue('atividadeFisica', formData.atividadeFisica));
    addField('Tipo', formData.tipoAtividade);
    addField('Tabagismo', translateValue('tabagismo', formData.tabagismo));
    addField('Álcool', translateValue('alcool', formData.alcool));
    addLine();
    
    // === EXPECTATIVAS ===
    checkPageBreak(30);
    addSection('🎯 EXPECTATIVAS');
    addField('Expectativas', formData.expectativas);
    addField('Objetivo', formData.objetivoSaude);
    addField('Observações', formData.observacoes);
    
    // === FOOTER ===
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text(
            'Documento gerado automaticamente - Dr. Felipe Barreto',
            pageWidth / 2,
            doc.internal.pageSize.getHeight() - 10,
            { align: 'center' }
        );
    }
    
    // Save
    const fileName = `Anamnese_${formData.nome?.replace(/\s+/g, '_') || 'Paciente'}_${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(fileName);
}

// ============================================
// TRANSLATION HELPERS
// ============================================

const translations = {
    tempoProblema: {
        'menos_1_semana': 'Menos de 1 semana',
        '1_4_semanas': '1 a 4 semanas',
        '1_3_meses': '1 a 3 meses',
        '3_6_meses': '3 a 6 meses',
        '6_12_meses': '6 a 12 meses',
        'mais_1_ano': 'Mais de 1 ano'
    },
    dorDuracao: {
        'aguda': 'Menos de 6 semanas (aguda)',
        'subaguda': '6 a 12 semanas (subaguda)',
        'cronica': 'Mais de 3 meses (crônica)'
    },
    dorIrradiacao: {
        'nao': 'Não irradia',
        'perna': 'Irradia para perna',
        'braco': 'Irradia para braço',
        'outro': 'Outro local'
    },
    sonoQualidade: {
        'descansado': 'Descansado e com energia',
        'pouco_cansado': 'Um pouco cansado, mas ok',
        'cansado': 'Cansado como se não tivesse dormido',
        'exausto': 'Exausto'
    },
    sonoDespertares: {
        'nenhuma': 'Nenhuma vez',
        '1_2': '1 a 2 vezes',
        '3_4': '3 a 4 vezes',
        'mais_4': 'Mais de 4 vezes'
    },
    resultadoTratamentos: {
        'nao_fiz': 'Não fez tratamentos',
        'melhorou_total': 'Melhorou completamente',
        'melhorou_parcial': 'Melhorou parcialmente',
        'nao_mudou': 'Não mudou nada',
        'piorou': 'Piorou'
    },
    atividadeFisica: {
        'nao': 'Não pratica',
        '1_2x': '1-2x por semana',
        '3_4x': '3-4x por semana',
        '5_mais': '5+ vezes por semana'
    },
    tabagismo: {
        'nunca': 'Nunca fumou',
        'ex_fumante': 'Ex-fumante',
        'fumante': 'Fumante atual'
    },
    alcool: {
        'nao': 'Não bebe',
        'ocasional': 'Ocasionalmente',
        'semanal': 'Semanalmente',
        'diario': 'Diariamente'
    }
};

const arrayTranslations = {
    'sem_dor': 'Sem dor',
    'cervical': 'Cervical',
    'toracica': 'Torácica',
    'lombar': 'Lombar',
    'gluteo': 'Glúteo/Quadril',
    'perna': 'Perna',
    'braco': 'Braço',
    'queimacao': 'Queimação',
    'pontada': 'Pontada',
    'peso': 'Peso/Pressão',
    'choque': 'Choque',
    'formigamento': 'Formigamento',
    'latejante': 'Latejante',
    'nenhum': 'Nenhum',
    'fraqueza_pernas': '🔴 Fraqueza pernas',
    'fraqueza_bracos': '🔴 Fraqueza braços',
    'dificuldade_urina': '🚨 Alteração urinária',
    'dificuldade_fezes': '🚨 Alteração intestinal',
    'anestesia_sela': '🚨 Anestesia sela',
    'perda_equilibrio': '🔴 Perda equilíbrio',
    'dor_noturna': '🔴 Dor noturna',
    'febre': '🔴 Febre',
    'perda_peso': '🔴 Perda peso',
    'nenhuma': 'Nenhuma',
    'diabetes': 'Diabetes',
    'hipertensao': 'Hipertensão',
    'colesterol': 'Colesterol alto',
    'cardiopatia': 'Cardiopatia',
    'depressao_ansiedade': 'Depressão/Ansiedade',
    'tireoide': 'Tireoide',
    'hernia': 'Hérnia de disco',
    'osteoporose': 'Osteoporose',
    'medicacoes': 'Medicações',
    'fisioterapia': 'Fisioterapia',
    'acupuntura': 'Acupuntura',
    'infiltracao': 'Infiltração',
    'cirurgia': 'Cirurgia',
    'pilates_rpg': 'Pilates/RPG'
};

function translateValue(field, value) {
    if (!value) return '-';
    return translations[field]?.[value] || value;
}

function translateArray(arr) {
    if (!arr || arr.length === 0) return '-';
    if (!Array.isArray(arr)) return arr;
    return arr.map(v => arrayTranslations[v] || v).join(', ');
}

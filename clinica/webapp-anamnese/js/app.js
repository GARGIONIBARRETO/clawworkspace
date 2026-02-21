/**
 * ANAMNESE WEBAPP - Dr. Felipe Barreto
 * Form handling and PDF generation
 */

// ============================================
// STATE & ELEMENTS
// ============================================

let currentStep = 1;
let activeSteps = [1, 2, 3, 4, 5, 6, 7, 8, 11]; // Default steps (without NDI/ODI)
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
    updateActiveSteps();
    updateProgress();
    setupEventListeners();
    setupConditionalFields();
    setupNDIODIListeners();
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

function setupNDIODIListeners() {
    // Listen for dor location changes to show/hide NDI/ODI
    const dorCheckboxes = document.querySelectorAll('input[name="dorLocal"]');
    dorCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            updateActiveSteps();
            // Also handle "outro" field visibility
            const outroCheckbox = document.querySelector('input[name="dorLocal"][value="outro"]');
            const outroContainer = document.getElementById('dorOutroContainer');
            if (outroContainer && outroCheckbox) {
                outroContainer.style.display = outroCheckbox.checked ? 'block' : 'none';
            }
        });
    });
    
    // NDI score calculation
    document.querySelectorAll('.ndi-question').forEach(select => {
        select.addEventListener('change', calculateNDIScore);
    });
    
    // ODI score calculation
    document.querySelectorAll('.odi-question').forEach(select => {
        select.addEventListener('change', calculateODIScore);
    });
    
    // GI "nenhum" exclusivity for multiple checkbox groups
    setupNenhumExclusivity('fezesNormal', 'fezesAnormais');
    setupNenhumExclusivity('nenhumPosPrandial', 'sintomasPosPrandiais');
    setupNenhumExclusivity('nenhumLeaky', 'leakyGut');
    
    // Show/hide intolerâncias field
    const intoleranciasRecentes = document.getElementById('intoleranciasRecentes');
    if (intoleranciasRecentes) {
        intoleranciasRecentes.addEventListener('change', () => {
            const container = document.getElementById('intoleranciasQuaisContainer');
            if (container) {
                container.style.display = intoleranciasRecentes.value === 'sim' ? 'block' : 'none';
            }
        });
    }
}

function setupNenhumExclusivity(nenhumId, groupName) {
    const nenhumCheckbox = document.getElementById(nenhumId);
    if (nenhumCheckbox) {
        nenhumCheckbox.addEventListener('change', () => {
            if (nenhumCheckbox.checked) {
                document.querySelectorAll(`input[name="${groupName}"]`).forEach(cb => {
                    if (cb.id !== nenhumId) cb.checked = false;
                });
            }
        });
        document.querySelectorAll(`input[name="${groupName}"]`).forEach(cb => {
            if (cb.id !== nenhumId) {
                cb.addEventListener('change', () => {
                    if (cb.checked) nenhumCheckbox.checked = false;
                });
            }
        });
    }
}

function updateActiveSteps() {
    // Base steps: 1-8 + 11 (expectativas)
    activeSteps = [1, 2, 3, 4, 5, 6, 7, 8];
    
    // Check if cervical is selected -> add NDI (step 9)
    const cervicalChecked = document.querySelector('input[name="dorLocal"][value="cervical"]')?.checked;
    // Check if lombar is selected -> add ODI (step 10)
    const lombarChecked = document.querySelector('input[name="dorLocal"][value="lombar"]')?.checked;
    
    if (cervicalChecked) {
        activeSteps.push(9);
        document.querySelector('.form-step[data-step="9"]').style.display = '';
    } else {
        document.querySelector('.form-step[data-step="9"]').style.display = 'none';
    }
    
    if (lombarChecked) {
        activeSteps.push(10);
        document.querySelector('.form-step[data-step="10"]').style.display = '';
    } else {
        document.querySelector('.form-step[data-step="10"]').style.display = 'none';
    }
    
    // Always end with Expectativas (step 11)
    activeSteps.push(11);
    activeSteps.sort((a, b) => a - b);
    
    elements.totalStepsEl.textContent = activeSteps.length;
    updateProgress();
    updateButtons();
}

function calculateNDIScore() {
    let total = 0;
    let answered = 0;
    document.querySelectorAll('.ndi-question').forEach(select => {
        if (select.value !== '') {
            total += parseInt(select.value);
            answered++;
        }
    });
    
    if (answered > 0) {
        const scoreDiv = document.getElementById('ndiScore');
        const scoreValue = document.getElementById('ndiScoreValue');
        const interpretation = document.getElementById('ndiInterpretation');
        
        scoreValue.textContent = total;
        scoreDiv.style.display = 'block';
        
        // NDI interpretation
        const percentage = (total / 50) * 100;
        let text = '';
        if (percentage <= 8) text = 'Sem incapacidade';
        else if (percentage <= 28) text = 'Incapacidade leve';
        else if (percentage <= 48) text = 'Incapacidade moderada';
        else if (percentage <= 68) text = 'Incapacidade severa';
        else text = 'Incapacidade completa';
        interpretation.textContent = `(${percentage.toFixed(0)}%) - ${text}`;
    }
}

function calculateODIScore() {
    let total = 0;
    let answered = 0;
    document.querySelectorAll('.odi-question').forEach(select => {
        if (select.value !== '') {
            total += parseInt(select.value);
            answered++;
        }
    });
    
    if (answered > 0) {
        const scoreDiv = document.getElementById('odiScore');
        const scoreValue = document.getElementById('odiScoreValue');
        const interpretation = document.getElementById('odiInterpretation');
        
        scoreValue.textContent = total;
        scoreDiv.style.display = 'block';
        
        // ODI interpretation
        const percentage = (total / 50) * 100;
        let text = '';
        if (percentage <= 20) text = 'Incapacidade mínima';
        else if (percentage <= 40) text = 'Incapacidade moderada';
        else if (percentage <= 60) text = 'Incapacidade severa';
        else if (percentage <= 80) text = 'Incapacitado';
        else text = 'Restrito ao leito';
        interpretation.textContent = `(${percentage.toFixed(0)}%) - ${text}`;
    }
}

// ============================================
// NAVIGATION
// ============================================

function nextStep() {
    if (!validateCurrentStep()) return;
    
    const currentIndex = activeSteps.indexOf(currentStep);
    if (currentIndex < activeSteps.length - 1) {
        goToStep(activeSteps[currentIndex + 1]);
    }
}

function prevStep() {
    const currentIndex = activeSteps.indexOf(currentStep);
    if (currentIndex > 0) {
        goToStep(activeSteps[currentIndex - 1]);
    }
}

function goToStep(step) {
    // Hide current step
    document.querySelector(`.form-step[data-step="${currentStep}"]`)?.classList.remove('active');
    
    // Show new step
    currentStep = step;
    document.querySelector(`.form-step[data-step="${currentStep}"]`)?.classList.add('active');
    
    updateProgress();
    updateButtons();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgress() {
    const currentIndex = activeSteps.indexOf(currentStep);
    const progress = ((currentIndex + 1) / activeSteps.length) * 100;
    elements.progressFill.style.width = `${progress}%`;
    elements.currentStepEl.textContent = currentIndex + 1;
}

function updateButtons() {
    const currentIndex = activeSteps.indexOf(currentStep);
    const isFirst = currentIndex === 0;
    const isLast = currentIndex === activeSteps.length - 1;
    
    elements.btnAnterior.style.display = isFirst ? 'none' : 'block';
    elements.btnProximo.style.display = isLast ? 'none' : 'block';
    elements.btnEnviar.style.display = isLast ? 'block' : 'none';
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
    addSection('IDENTIFICAÇÃO');
    addField('Nome', formData.nome);
    addField('Data Nasc.', formData.dataNascimento);
    addField('Sexo', formData.sexo);
    addField('Profissão', formData.profissao);
    addField('Telefone', formData.telefone);
    addLine();
    
    // === QUEIXA PRINCIPAL ===
    addSection('QUEIXA PRINCIPAL');
    addField('Queixa', formData.queixaPrincipal);
    addField('Tempo', translateValue('tempoProblema', formData.tempoProblema));
    addField('Evento', formData.eventoDesencadeante);
    addLine();
    
    // === DOR ===
    addSection('INVESTIGAÇÃO DA DOR');
    addField('Localização', translateArray(formData.dorLocal));
    if (formData.dorLocal?.includes('outro') && formData.dorOutroLocal) {
        addField('Outro local', formData.dorOutroLocal);
    }
    if (!formData.dorLocal?.includes('sem_dor')) {
        addField('Intensidade', formData.dorIntensidade + '/10');
        addField('Tipo', translateArray(formData.dorTipo));
        addField('Duração', translateValue('dorDuracao', formData.dorDuracao));
        addField('Irradiação', translateValue('dorIrradiacao', formData.dorIrradiacao));
    }
    addLine();
    
    // === SINAIS DE ALERTA ===
    addSection('SINAIS DE ALERTA');
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
    addSection('SONO E ESTRESSE');
    addField('Qualidade sono', translateValue('sonoQualidade', formData.sonoQualidade));
    addField('Despertares', translateValue('sonoDespertares', formData.sonoDespertares));
    addField('Horas de sono', translateValue('horasDormidas', formData.horasDormidas));
    addField('Estresse', formData.estresseNivel + '/10');
    addField('Fator', formData.estresseFator);
    addLine();
    
    // === FUNÇÃO GASTROINTESTINAL ===
    checkPageBreak(60);
    addSection('FUNCAO GASTROINTESTINAL');
    
    // Hábito Intestinal
    addField('Frequência evacuação', translateValue('frequenciaEvacuacao', formData.frequenciaEvacuacao));
    addField('Bristol', translateValue('escalaBristol', formData.escalaBristol));
    addField('Esforço p/ evacuar', translateValue('esforcoEvacuar', formData.esforcoEvacuar));
    addField('Evacuação incompleta', translateValue('evacuacaoIncompleta', formData.evacuacaoIncompleta));
    addField('Fezes anormais', translateArray(formData.fezesAnormais));
    
    // SIBO/Fermentação
    addField('Distensão abdominal', translateValue('distensaoAbdominal', formData.distensaoAbdominal));
    addField('Piora ao longo do dia', translateValue('distensaoPiora', formData.distensaoPiora));
    addField('Flatulência', translateValue('flatulencia', formData.flatulencia));
    addField('Gases mal odor', translateValue('gasesOdor', formData.gasesOdor));
    addField('Triggers SIBO', translateArray(formData.siboTriggers));
    
    // Pós-prandial
    addField('Fadiga pós-refeição', translateValue('fadigaPosPrandial', formData.fadigaPosPrandial));
    addField('Névoa mental', translateValue('nevoaMentalAlimento', formData.nevoaMentalAlimento));
    addField('Sintomas pós-prandiais', translateArray(formData.sintomasPosPrandiais));
    
    // Permeabilidade/Leaky Gut
    addField('Intolerâncias recentes', translateValue('intoleranciasRecentes', formData.intoleranciasRecentes));
    if (formData.intoleranciasQuais) addField('Quais', formData.intoleranciasQuais);
    addField('Sinais leaky gut', translateArray(formData.leakyGut));
    
    // Histórico GI
    addField('Antibióticos recentes', translateValue('usoAntibiotico', formData.usoAntibiotico));
    addField('Probióticos', translateValue('usoProbiotico', formData.usoProbiotico));
    addField('Uso IBP', translateValue('usoIBP', formData.usoIBP));
    addLine();
    
    // === HISTÓRICO ===
    checkPageBreak(40);
    addSection('HISTÓRICO MÉDICO');
    addField('Condições', translateArray(formData.condicoes));
    addField('Outras', formData.outrasCondicoes);
    addField('Medicamentos', formData.usaMedicamentos === 'sim' ? formData.medicamentosLista : 'Não usa');
    addField('Alergias', formData.alergias || 'Não informado');
    addField('Cirurgias', formData.cirurgiasAnteriores || 'Nenhuma');
    addLine();
    
    // === TRATAMENTOS ===
    addSection('TRATAMENTOS E HÁBITOS');
    addField('Tratamentos', translateArray(formData.tratamentos));
    addField('Resultado', translateValue('resultadoTratamentos', formData.resultadoTratamentos));
    addField('Atividade', translateValue('atividadeFisica', formData.atividadeFisica));
    addField('Tipo', formData.tipoAtividade);
    addField('Tabagismo', translateValue('tabagismo', formData.tabagismo));
    addField('Álcool', translateValue('alcool', formData.alcool));
    addLine();
    
    // === NDI (se cervical) ===
    if (formData.dorLocal && formData.dorLocal.includes('cervical')) {
        checkPageBreak(50);
        addSection('NDI - INDICE INCAPACIDADE CERVICAL');
        let ndiTotal = 0;
        let ndiAnswered = 0;
        for (let i = 1; i <= 10; i++) {
            const val = formData['ndi_' + i];
            if (val !== undefined && val !== '') {
                ndiTotal += parseInt(val);
                ndiAnswered++;
            }
        }
        if (ndiAnswered > 0) {
            const ndiPercent = (ndiTotal / 50) * 100;
            let ndiClass = '';
            if (ndiPercent <= 8) ndiClass = 'Sem incapacidade';
            else if (ndiPercent <= 28) ndiClass = 'Incapacidade leve';
            else if (ndiPercent <= 48) ndiClass = 'Incapacidade moderada';
            else if (ndiPercent <= 68) ndiClass = 'Incapacidade severa';
            else ndiClass = 'Incapacidade completa';
            addField('Pontuação', ndiTotal + '/50 (' + ndiPercent.toFixed(0) + '%)');
            addField('Classificação', ndiClass);
        } else {
            addField('Status', 'Não respondido');
        }
        addLine();
    }
    
    // === ODI (se lombar) ===
    if (formData.dorLocal && formData.dorLocal.includes('lombar')) {
        checkPageBreak(50);
        addSection('ODI - INDICE INCAPACIDADE LOMBAR');
        let odiTotal = 0;
        let odiAnswered = 0;
        for (let i = 1; i <= 10; i++) {
            const val = formData['odi_' + i];
            if (val !== undefined && val !== '') {
                odiTotal += parseInt(val);
                odiAnswered++;
            }
        }
        if (odiAnswered > 0) {
            const odiPercent = (odiTotal / 50) * 100;
            let odiClass = '';
            if (odiPercent <= 20) odiClass = 'Incapacidade mínima';
            else if (odiPercent <= 40) odiClass = 'Incapacidade moderada';
            else if (odiPercent <= 60) odiClass = 'Incapacidade severa';
            else if (odiPercent <= 80) odiClass = 'Incapacitado';
            else odiClass = 'Restrito ao leito';
            addField('Pontuação', odiTotal + '/50 (' + odiPercent.toFixed(0) + '%)');
            addField('Classificação', odiClass);
        } else {
            addField('Status', 'Não respondido');
        }
        addLine();
    }
    
    // === EXPECTATIVAS ===
    checkPageBreak(30);
    addSection('EXPECTATIVAS');
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
    horasDormidas: {
        'menos_4': 'Menos de 4 horas',
        '4_5': '4 a 5 horas',
        '5_6': '5 a 6 horas',
        '6_7': '6 a 7 horas',
        '7_8': '7 a 8 horas',
        'mais_8': 'Mais de 8 horas'
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
    },
    sintomasGIFrequencia: {
        'nao_tenho': 'Não tenho sintomas',
        'raramente': 'Raramente (1-2x/mês)',
        'semanal': 'Semanalmente',
        'varios_semana': 'Várias vezes por semana',
        'diario': 'Diariamente'
    },
    usoAntibiotico: {
        'nao': 'Não',
        '1_vez': '1 vez',
        '2_3_vezes': '2-3 vezes',
        'mais_3': 'Mais de 3 vezes'
    },
    usoProbiotico: {
        'nunca': 'Nunca usou',
        'uso_atual': 'Uso atual',
        'ja_usei': 'Já usou, parou'
    },
    // Novos campos GI
    frequenciaEvacuacao: {
        'menos_3': 'Menos de 3x/semana',
        '3_7': '3-7x/semana (até 1x/dia)',
        '7_14': '7-14x/semana (1-2x/dia)',
        'mais_14': 'Mais de 14x/semana'
    },
    escalaBristol: {
        'tipo_1_2': 'Tipo 1-2 (duras)',
        'tipo_3_4': 'Tipo 3-4 (ideal)',
        'tipo_5_6': 'Tipo 5-6 (moles)',
        'tipo_7': 'Tipo 7 (líquidas)'
    },
    esforcoEvacuar: {
        'nao': 'Não',
        'as_vezes': 'Às vezes',
        'sempre': 'Sempre'
    },
    evacuacaoIncompleta: {
        'nao': 'Não',
        'as_vezes': 'Às vezes',
        'frequente': 'Frequentemente'
    },
    distensaoAbdominal: {
        'nao': 'Não',
        'as_vezes': 'Às vezes',
        'frequente': 'Frequentemente',
        'sempre': 'Sempre'
    },
    distensaoPiora: {
        'nao': 'Não',
        'sim': 'Sim'
    },
    flatulencia: {
        'normal': 'Normal',
        'aumentado': 'Aumentado',
        'muito_aumentado': 'Muito aumentado'
    },
    gasesOdor: {
        'nao': 'Não',
        'sim': 'Sim'
    },
    fadigaPosPrandial: {
        'nao': 'Não',
        'as_vezes': 'Às vezes',
        'frequente': 'Frequentemente'
    },
    nevoaMentalAlimento: {
        'nao': 'Não',
        'as_vezes': 'Às vezes',
        'frequente': 'Frequentemente'
    },
    intoleranciasRecentes: {
        'nao': 'Não',
        'sim': 'Sim'
    },
    usoIBP: {
        'nao': 'Não',
        'eventual': 'Eventualmente',
        'continuo': 'Uso contínuo'
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
    'cabeca': 'Cabeça/Cefaleia',
    'outro': 'Outro local',
    // Sintomas GI
    'distensao': 'Distensão abdominal',
    'gases': 'Excesso de gases',
    'diarreia': 'Diarreia frequente',
    'constipacao': 'Constipação',
    'alternante': 'Alternância diarreia/constipação',
    'dor_abdominal': 'Dor/desconforto abdominal',
    'refluxo': 'Refluxo/azia',
    'nausea': 'Náusea frequente',
    'saciedade': 'Saciedade precoce',
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
    'pilates_rpg': 'Pilates/RPG',
    // Fezes anormais
    'muco': 'Muco',
    'sangue': '🔴 Sangue',
    'alimentos': 'Alimentos não digeridos',
    // Triggers SIBO
    'carbo_piora': 'Carboidratos pioram',
    'fibra_piora': 'Fibras pioram',
    'jejum_melhora': 'Jejum melhora',
    'lactose_piora': 'Lactose piora',
    'fodmap_piora': 'FODMAPs pioram',
    // Sintomas pós-prandiais
    'dor_articular': 'Dor articular',
    'alteracao_humor': 'Alteração de humor',
    'palpitacao': 'Palpitações',
    // Leaky gut
    'alimentos_antes_ok': 'Alimentos antes tolerados agora causam sintomas',
    'multiplas_reacoes': 'Múltiplas sensibilidades alimentares',
    'infeccoes_recorrentes': 'Infecções recorrentes'
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

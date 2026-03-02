-- SQL para criar tabela de episódios clínicos
CREATE TABLE IF NOT EXISTS episodios_clinicos (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    consulta_id INTEGER REFERENCES consultas(id),
    data_episodio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Anamnese
    queixa_principal TEXT,
    historia_doenca_atual TEXT,
    revisao_sistemas TEXT,
    
    -- Exame Físico
    sinais_vitais JSONB,
    exame_geral TEXT,
    exame_neurologico TEXT,
    exame_coluna TEXT,
    
    -- Diagnóstico
    hipoteses_diagnosticas TEXT,
    cid10 VARCHAR(10),
    
    -- Conduta
    condutas TEXT,
    prescricoes TEXT,
    exames_solicitados TEXT,
    
    -- Follow-up
    orientacoes TEXT,
    retorno VARCHAR(100),
    
    -- Metadados
    medico VARCHAR(255) DEFAULT 'Dr. Felipe',
    tipo_atendimento VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_episodios_paciente ON episodios_clinicos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_episodios_data ON episodios_clinicos(data_episodio);

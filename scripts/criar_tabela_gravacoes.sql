-- Tabela para armazenar gravações de consultas
CREATE TABLE IF NOT EXISTS gravacoes_consultas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    data_gravacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    arquivo_audio VARCHAR(500) NOT NULL,
    duracao VARCHAR(20),
    transcricao TEXT,
    analise_ia JSONB,
    transcrito BOOLEAN DEFAULT FALSE,
    episodio_criado BOOLEAN DEFAULT FALSE,
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gravacoes_paciente ON gravacoes_consultas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_gravacoes_data ON gravacoes_consultas(data_gravacao);
-- Schema para logistica.db
-- Responsável por: Monitoramento, rotas, entregas, veículos operacionais

-- Tabela de monitoramento em tempo real
CREATE TABLE IF NOT EXISTS logistica_monitoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    data TEXT, -- JSON com dados da planilha
    status TEXT,
    registros_processados INTEGER,
    erros TEXT -- JSON com erros encontrados
);

-- Tabela de veículos operacionais (separada dos de suporte)
CREATE TABLE IF NOT EXISTS veiculos_operacionais (
    placa TEXT PRIMARY KEY,
    tipologia TEXT,
    perfil TEXT, -- SPOT, DEDICATED, etc.
    status_operacional TEXT DEFAULT 'ativo',
    ultima_viagem DATETIME,
    km_atual INTEGER,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de rotas/viagens
CREATE TABLE IF NOT EXISTS viagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    motorista TEXT,
    origem TEXT,
    destino TEXT,
    distancia_km REAL,
    data_inicio DATETIME,
    data_fim DATETIME,
    status_viagem TEXT, -- Planejada, Em Andamento, Finalizada, Cancelada
    observacoes TEXT,
    FOREIGN KEY (placa) REFERENCES veiculos_operacionais (placa)
);

-- Tabela de entregas
CREATE TABLE IF NOT EXISTS entregas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    viagem_id INTEGER,
    nf TEXT,
    cliente TEXT,
    embarcador TEXT,
    peso_bruto REAL,
    valor_frete REAL,
    status_entrega TEXT, -- Agendada, Retirada, Em Trânsito, Entregue, Problema
    data_agendada DATETIME,
    data_entrega DATETIME,
    cidade_destino TEXT,
    observacoes TEXT,
    FOREIGN KEY (viagem_id) REFERENCES viagens (id)
);

-- Tabela de performance por embarcador
CREATE TABLE IF NOT EXISTS performance_embarcadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    embarcador TEXT NOT NULL,
    periodo_inicio DATE,
    periodo_fim DATE,
    peso_total REAL,
    peso_entregue REAL,
    percentual_eficiencia REAL,
    numero_entregas INTEGER,
    valor_total_frete REAL,
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de alertas operacionais
CREATE TABLE IF NOT EXISTS alertas_operacionais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_alerta TEXT NOT NULL, -- atraso, problema_entrega, veiculo_parado, etc.
    titulo TEXT NOT NULL,
    descricao TEXT,
    severidade TEXT DEFAULT 'media', -- baixa, media, alta, critica
    placa TEXT,
    viagem_id INTEGER,
    entrega_id INTEGER,
    status_alerta TEXT DEFAULT 'ativo', -- ativo, resolvido, ignorado
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_resolucao DATETIME,
    resolvido_por TEXT,
    FOREIGN KEY (placa) REFERENCES veiculos_operacionais (placa),
    FOREIGN KEY (viagem_id) REFERENCES viagens (id),
    FOREIGN KEY (entrega_id) REFERENCES entregas (id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_monitoring_timestamp ON logistica_monitoring(timestamp);
CREATE INDEX IF NOT EXISTS idx_veiculos_status ON veiculos_operacionais(status_operacional);
CREATE INDEX IF NOT EXISTS idx_viagens_placa ON viagens(placa);
CREATE INDEX IF NOT EXISTS idx_viagens_status ON viagens(status_viagem);
CREATE INDEX IF NOT EXISTS idx_viagens_data ON viagens(data_inicio);
CREATE INDEX IF NOT EXISTS idx_entregas_viagem ON entregas(viagem_id);
CREATE INDEX IF NOT EXISTS idx_entregas_status ON entregas(status_entrega);
CREATE INDEX IF NOT EXISTS idx_entregas_cliente ON entregas(cliente);
CREATE INDEX IF NOT EXISTS idx_entregas_embarcador ON entregas(embarcador);
CREATE INDEX IF NOT EXISTS idx_performance_embarcador ON performance_embarcadores(embarcador);
CREATE INDEX IF NOT EXISTS idx_performance_periodo ON performance_embarcadores(periodo_inicio, periodo_fim);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas_operacionais(tipo_alerta);
CREATE INDEX IF NOT EXISTS idx_alertas_status ON alertas_operacionais(status_alerta);
CREATE INDEX IF NOT EXISTS idx_alertas_severidade ON alertas_operacionais(severidade);
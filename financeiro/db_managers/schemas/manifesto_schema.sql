-- Schema para manifesto.db
-- Responsável por: Dados de manifesto, cargas, fretes, importações

-- Tabela principal de manifesto acumulado
CREATE TABLE IF NOT EXISTS manifesto_acumulado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nf TEXT,
    cliente TEXT,
    cliente_real TEXT,
    embarcador TEXT,
    cidade TEXT,
    estado TEXT,
    peso_bruto REAL,
    peso_liquido REAL,
    volume_m3 REAL,
    valor_mercadoria REAL,
    valor_frete REAL,
    placa TEXT,
    motorista TEXT,
    data_coleta DATE,
    data_entrega DATE,
    status_nf TEXT,
    status_viagem TEXT,
    observacoes TEXT,
    data_importacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    arquivo_origem TEXT
);

-- Tabela de histórico de importações
CREATE TABLE IF NOT EXISTS historico_importacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_arquivo TEXT NOT NULL,
    tamanho_arquivo INTEGER,
    tipo_importacao TEXT, -- manifesto, pamplona, etc.
    registros_importados INTEGER,
    registros_erro INTEGER,
    data_importacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_importacao TEXT,
    status_importacao TEXT, -- sucesso, erro, parcial
    log_erros TEXT, -- JSON com detalhes dos erros
    tempo_processamento REAL, -- em segundos
    hash_arquivo TEXT -- para evitar reimportações
);

-- Tabela de processamento Pamplona
CREATE TABLE IF NOT EXISTS pamplona_processamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo_path TEXT NOT NULL,
    data_processamento DATETIME DEFAULT CURRENT_TIMESTAMP,
    blocos_processados INTEGER,
    linhas_processadas INTEGER,
    arquivo_backup TEXT,
    status_processamento TEXT, -- sucesso, erro, em_progresso
    detalhes_processamento TEXT, -- JSON com detalhes
    tempo_processamento REAL
);

-- Tabela de cargas consolidadas
CREATE TABLE IF NOT EXISTS cargas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_carga TEXT UNIQUE,
    placa TEXT,
    motorista TEXT,
    origem TEXT,
    destino TEXT,
    data_carregamento DATETIME,
    data_descarregamento DATETIME,
    peso_total REAL,
    volume_total REAL,
    valor_frete_total REAL,
    numero_nfs INTEGER,
    status_carga TEXT, -- planejada, carregada, transito, entregue
    observacoes TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de itens da carga (relacionamento com NFs)
CREATE TABLE IF NOT EXISTS itens_carga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carga_id INTEGER,
    manifesto_id INTEGER,
    sequencia_entrega INTEGER,
    status_item TEXT, -- pendente, entregue, problema
    data_entrega_item DATETIME,
    observacoes_item TEXT,
    FOREIGN KEY (carga_id) REFERENCES cargas (id),
    FOREIGN KEY (manifesto_id) REFERENCES manifesto_acumulado (id)
);

-- Tabela de eventos de rastreamento
CREATE TABLE IF NOT EXISTS eventos_rastreamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carga_id INTEGER,
    manifesto_id INTEGER,
    evento TEXT NOT NULL, -- carregamento, saida, chegada, entrega, etc.
    data_evento DATETIME DEFAULT CURRENT_TIMESTAMP,
    localizacao TEXT,
    observacoes TEXT,
    usuario_evento TEXT,
    FOREIGN KEY (carga_id) REFERENCES cargas (id),
    FOREIGN KEY (manifesto_id) REFERENCES manifesto_acumulado (id)
);

-- Tabela de rotas otimizadas
CREATE TABLE IF NOT EXISTS rotas_otimizadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carga_id INTEGER,
    sequencia_paradas TEXT, -- JSON com ordem otimizada das paradas
    distancia_total_km REAL,
    tempo_estimado_horas REAL,
    combustivel_estimado_litros REAL,
    custo_estimado REAL,
    algoritmo_usado TEXT,
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (carga_id) REFERENCES cargas (id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_manifesto_nf ON manifesto_acumulado(nf);
CREATE INDEX IF NOT EXISTS idx_manifesto_cliente ON manifesto_acumulado(cliente);
CREATE INDEX IF NOT EXISTS idx_manifesto_embarcador ON manifesto_acumulado(embarcador);
CREATE INDEX IF NOT EXISTS idx_manifesto_placa ON manifesto_acumulado(placa);
CREATE INDEX IF NOT EXISTS idx_manifesto_data_coleta ON manifesto_acumulado(data_coleta);
CREATE INDEX IF NOT EXISTS idx_manifesto_status ON manifesto_acumulado(status_nf, status_viagem);
CREATE INDEX IF NOT EXISTS idx_historico_data ON historico_importacoes(data_importacao);
CREATE INDEX IF NOT EXISTS idx_historico_tipo ON historico_importacoes(tipo_importacao);
CREATE INDEX IF NOT EXISTS idx_historico_hash ON historico_importacoes(hash_arquivo);
CREATE INDEX IF NOT EXISTS idx_pamplona_data ON pamplona_processamentos(data_processamento);
CREATE INDEX IF NOT EXISTS idx_cargas_numero ON cargas(numero_carga);
CREATE INDEX IF NOT EXISTS idx_cargas_placa ON cargas(placa);
CREATE INDEX IF NOT EXISTS idx_cargas_status ON cargas(status_carga);
CREATE INDEX IF NOT EXISTS idx_cargas_data ON cargas(data_carregamento);
CREATE INDEX IF NOT EXISTS idx_itens_carga ON itens_carga(carga_id);
CREATE INDEX IF NOT EXISTS idx_itens_manifesto ON itens_carga(manifesto_id);
CREATE INDEX IF NOT EXISTS idx_eventos_carga ON eventos_rastreamento(carga_id);
CREATE INDEX IF NOT EXISTS idx_eventos_data ON eventos_rastreamento(data_evento);
CREATE INDEX IF NOT EXISTS idx_rotas_carga ON rotas_otimizadas(carga_id);
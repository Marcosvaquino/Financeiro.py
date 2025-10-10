-- Schema para suporte.db
-- Responsável por: Clientes, veículos de suporte, configurações de apoio

-- Tabela de clientes de suporte
CREATE TABLE IF NOT EXISTS clientes_suporte (
    nome_real TEXT PRIMARY KEY,
    nome_ajustado TEXT NOT NULL,
    data_cadastro DATETIME NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    observacoes TEXT,
    categoria TEXT, -- A, B, C (classificação de cliente)
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de veículos de suporte/configuração
CREATE TABLE IF NOT EXISTS veiculos_suporte (
    placa TEXT PRIMARY KEY,
    status TEXT,
    tipologia TEXT,
    marca TEXT,
    modelo TEXT,
    ano INTEGER,
    capacidade_kg REAL,
    capacidade_m3 REAL,
    categoria_cnh TEXT,
    combustivel TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT 1,
    observacoes TEXT
);

-- Tabela de configurações de fretes
CREATE TABLE IF NOT EXISTS configuracoes_frete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_veiculo TEXT NOT NULL,
    categoria TEXT, -- urbano, rodoviario, etc.
    valor_km REAL,
    valor_hora REAL,
    valor_parada REAL,
    taxa_combustivel REAL,
    taxa_pedagio REAL,
    margem_sugerida REAL, -- percentual
    data_vigencia_inicio DATE,
    data_vigencia_fim DATE,
    ativo BOOLEAN DEFAULT 1,
    criado_por TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de custos da frota (movida do financeiro)
CREATE TABLE IF NOT EXISTS custo_frota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_veiculo TEXT NOT NULL,
    custo_fixo REAL NOT NULL,
    custo_variavel REAL NOT NULL,
    km INTEGER,
    dias INTEGER,
    custo_mensal REAL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT 1,
    observacoes TEXT
);

-- Tabela de fornecedores/terceiros
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cnpj TEXT UNIQUE,
    categoria TEXT, -- transportadora, posto, oficina, etc.
    contato_nome TEXT,
    contato_telefone TEXT,
    contato_email TEXT,
    endereco TEXT,
    cidade TEXT,
    estado TEXT,
    cep TEXT,
    ativo BOOLEAN DEFAULT 1,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT
);

-- Tabela de parâmetros operacionais
CREATE TABLE IF NOT EXISTS parametros_operacionais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL, -- combustivel, pedagio, manutencao, etc.
    parametro TEXT NOT NULL,
    valor REAL,
    unidade TEXT, -- R$/km, R$/litro, etc.
    data_vigencia_inicio DATE,
    data_vigencia_fim DATE,
    ativo BOOLEAN DEFAULT 1,
    fonte TEXT, -- de onde veio o dado
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_clientes_ativo ON clientes_suporte(ativo);
CREATE INDEX IF NOT EXISTS idx_clientes_categoria ON clientes_suporte(categoria);
CREATE INDEX IF NOT EXISTS idx_veiculos_tipologia ON veiculos_suporte(tipologia);
CREATE INDEX IF NOT EXISTS idx_veiculos_ativo ON veiculos_suporte(ativo);
CREATE INDEX IF NOT EXISTS idx_config_frete_tipo ON configuracoes_frete(tipo_veiculo);
CREATE INDEX IF NOT EXISTS idx_config_frete_ativo ON configuracoes_frete(ativo);
CREATE INDEX IF NOT EXISTS idx_config_frete_vigencia ON configuracoes_frete(data_vigencia_inicio, data_vigencia_fim);
CREATE INDEX IF NOT EXISTS idx_custo_frota_tipo ON custo_frota(tipo_veiculo);
CREATE INDEX IF NOT EXISTS idx_custo_frota_ativo ON custo_frota(ativo);
CREATE INDEX IF NOT EXISTS idx_fornecedores_categoria ON fornecedores(categoria);
CREATE INDEX IF NOT EXISTS idx_fornecedores_ativo ON fornecedores(ativo);
CREATE INDEX IF NOT EXISTS idx_parametros_categoria ON parametros_operacionais(categoria);
CREATE INDEX IF NOT EXISTS idx_parametros_ativo ON parametros_operacionais(ativo);
CREATE INDEX IF NOT EXISTS idx_parametros_vigencia ON parametros_operacionais(data_vigencia_inicio, data_vigencia_fim);
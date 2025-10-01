-- SCHEMA AJUSTADO

-- DROP TABLE IF EXISTS contas_receber;
-- DROP TABLE IF EXISTS contas_pagar;

CREATE TABLE IF NOT EXISTS contas_receber (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj_filial TEXT,
    filial TEXT,
    cnpj_cliente TEXT,
    cliente TEXT,
    sequencia TEXT,
    documento TEXT,
    cheque TEXT,
    emissao TEXT,
    vencimento TEXT,
    vencimento_original TEXT,
    competencia TEXT,
    valor_principal REAL,
    juros_desc REAL,
    valor_titulo REAL,
    data_baixa TEXT,
    data_liquidacao TEXT,
    banco_recebimento TEXT,
    conta_recebimento TEXT,
    forma_recebimento TEXT,
    observacoes TEXT,
    conta_contabil TEXT,
    centro_custo TEXT,
    status TEXT,
    descricao_receita TEXT
);

-- Tabela de suporte para veículos do frete
CREATE TABLE IF NOT EXISTS veiculos_suporte (
    placa TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('FIXO', 'SPOT')),
    tipologia TEXT NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela para custos da frota (baseada na imagem fornecida)
CREATE TABLE IF NOT EXISTS custo_frota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_veiculo TEXT NOT NULL,
    custo_fixo REAL NOT NULL,
    custo_variavel REAL NOT NULL,
    km INTEGER NOT NULL,
    dias INTEGER NOT NULL,
    custo_mensal REAL NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS contas_pagar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj_filial TEXT,
    filial TEXT,
    cnpj_fornecedor TEXT,
    fornecedor TEXT,
    sequencia TEXT,
    documento TEXT,
    cheque TEXT,
    emissao TEXT,
    vencimento TEXT,
    vencimento_original TEXT,
    competencia TEXT,
    valor_principal REAL,
    juros_desc REAL,
    valor_titulo REAL,
    data_baixa TEXT,
    data_liquidacao TEXT,
    banco_pagto TEXT,
    conta_pagto TEXT,
    forma_pagto TEXT,
    observacoes TEXT,
    conta_contabil TEXT,
    centro_custo TEXT,
    status TEXT,
    descricao_despesa TEXT
);

CREATE TABLE IF NOT EXISTS projecao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    mes INTEGER NOT NULL CHECK(mes BETWEEN 1 AND 12),
    ano INTEGER NOT NULL,
    dia INTEGER NOT NULL CHECK(dia BETWEEN 1 AND 31),
    valor REAL NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    perfil TEXT CHECK(perfil IN ('admin','user')) DEFAULT 'user',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS clientes_padrao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

-- Insere os clientes padrão
INSERT OR IGNORE INTO clientes_padrao (nome) VALUES
('ADORO'),
('ADORO S.A.'),
('ADORO SAO CARLOS'),
('AGRA FOODS'),
('ALIBEM'),
('FRIBOI'),
('GOLDPAO CD SAO JOSE DOS CAMPOS'),
('GTFOODS BARUERI'),
('JK DISTRIBUIDORA'),
('LATICINIO CARMONA'),
('MARFRIG - ITUPEVA CD'),
('MARFRIG - PROMISSAO'),
('MARFRIG GLOBAL FOODS S A'),
('MINERVA S A'),
('PAMPLONA JANDIRA'),
('PEIXES MEGGS PESCADOS LTDA - SJBV'),
('SANTA LUCIA'),
('SAUDALI'),
('VALENCIO JATAÍ');

-- Schema para margem.db  
-- Responsável por: Análises financeiras, rentabilidade, custos, relatórios

-- Tabela de contas a receber
CREATE TABLE IF NOT EXISTS contas_receber (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nf TEXT NOT NULL,
    cliente TEXT NOT NULL,
    valor REAL NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status TEXT DEFAULT 'pendente', -- pendente, pago, vencido, cancelado
    observacoes TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de contas a pagar
CREATE TABLE IF NOT EXISTS contas_pagar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT, -- combustivel, manutencao, seguro, etc.
    valor REAL NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status TEXT DEFAULT 'pendente', -- pendente, pago, vencido, cancelado
    numero_documento TEXT,
    observacoes TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de análise de margem
CREATE TABLE IF NOT EXISTS analise_margem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    cliente TEXT,
    embarcador TEXT,
    placa TEXT,
    receita_total REAL NOT NULL,
    custo_combustivel REAL,
    custo_pedagio REAL,
    custo_manutencao REAL,
    custo_motorista REAL,
    custo_fixo_veiculo REAL,
    outros_custos REAL,
    custo_total REAL NOT NULL,
    margem_bruta REAL NOT NULL,
    margem_percentual REAL NOT NULL,
    km_rodados REAL,
    litros_combustivel REAL,
    numero_viagens INTEGER,
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT
);

-- Tabela de projeções financeiras
CREATE TABLE IF NOT EXISTS projecoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    categoria TEXT NOT NULL, -- receita, custo_fixo, custo_variavel
    subcategoria TEXT, -- frete, combustivel, manutencao, etc.
    valor_orcado REAL NOT NULL,
    valor_realizado REAL,
    variacao_absoluta REAL,
    variacao_percentual REAL,
    observacoes TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de indicadores de performance (KPIs)
CREATE TABLE IF NOT EXISTS kpis_financeiros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_referencia DATE NOT NULL,
    periodo_tipo TEXT NOT NULL, -- diario, semanal, mensal, anual
    receita_total REAL,
    custo_total REAL,
    margem_liquida REAL,
    margem_percentual REAL,
    ticket_medio REAL,
    custo_por_km REAL,
    receita_por_km REAL,
    numero_clientes_ativos INTEGER,
    numero_viagens INTEGER,
    km_total REAL,
    eficiencia_operacional REAL, -- %
    inadimplencia_percentual REAL,
    giro_estoque_dias REAL,
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de budget/orçamento
CREATE TABLE IF NOT EXISTS orcamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    subcategoria TEXT,
    valor_orcado REAL NOT NULL,
    justificativa TEXT,
    aprovado_por TEXT,
    data_aprovacao DATE,
    status TEXT DEFAULT 'planejado', -- planejado, aprovado, rejeitado, revisado
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de análise de rentabilidade por cliente
CREATE TABLE IF NOT EXISTS rentabilidade_clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    receita_total REAL NOT NULL,
    custo_operacional REAL NOT NULL,
    margem_liquida REAL NOT NULL,
    margem_percentual REAL NOT NULL,
    numero_viagens INTEGER,
    peso_total REAL,
    km_total REAL,
    ticket_medio REAL,
    custo_medio_viagem REAL,
    classificacao_cliente TEXT, -- A, B, C, D
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de custos por rota
CREATE TABLE IF NOT EXISTS custos_rotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem TEXT NOT NULL,
    destino TEXT NOT NULL,
    distancia_km REAL NOT NULL,
    custo_combustivel_medio REAL,
    custo_pedagio REAL,
    tempo_medio_horas REAL,
    custo_por_km REAL,
    custo_total_medio REAL,
    numero_viagens_base INTEGER, -- quantas viagens usadas para calcular a média
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_contas_receber_cliente ON contas_receber(cliente);
CREATE INDEX IF NOT EXISTS idx_contas_receber_vencimento ON contas_receber(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_contas_receber_status ON contas_receber(status);
CREATE INDEX IF NOT EXISTS idx_contas_pagar_fornecedor ON contas_pagar(fornecedor);
CREATE INDEX IF NOT EXISTS idx_contas_pagar_categoria ON contas_pagar(categoria);
CREATE INDEX IF NOT EXISTS idx_contas_pagar_vencimento ON contas_pagar(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_contas_pagar_status ON contas_pagar(status);
CREATE INDEX IF NOT EXISTS idx_margem_periodo ON analise_margem(periodo_inicio, periodo_fim);
CREATE INDEX IF NOT EXISTS idx_margem_cliente ON analise_margem(cliente);
CREATE INDEX IF NOT EXISTS idx_margem_embarcador ON analise_margem(embarcador);
CREATE INDEX IF NOT EXISTS idx_margem_placa ON analise_margem(placa);
CREATE INDEX IF NOT EXISTS idx_projecoes_periodo ON projecoes(ano, mes);
CREATE INDEX IF NOT EXISTS idx_projecoes_categoria ON projecoes(categoria);
CREATE INDEX IF NOT EXISTS idx_kpis_data ON kpis_financeiros(data_referencia);
CREATE INDEX IF NOT EXISTS idx_kpis_periodo ON kpis_financeiros(periodo_tipo);
CREATE INDEX IF NOT EXISTS idx_orcamento_periodo ON orcamento(ano, mes);
CREATE INDEX IF NOT EXISTS idx_orcamento_categoria ON orcamento(categoria);
CREATE INDEX IF NOT EXISTS idx_rentabilidade_cliente ON rentabilidade_clientes(cliente);
CREATE INDEX IF NOT EXISTS idx_rentabilidade_periodo ON rentabilidade_clientes(periodo_inicio, periodo_fim);
CREATE INDEX IF NOT EXISTS idx_custos_rotas_origem ON custos_rotas(origem);
CREATE INDEX IF NOT EXISTS idx_custos_rotas_destino ON custos_rotas(destino);
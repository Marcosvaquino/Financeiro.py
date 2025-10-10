-- Schema para core.db
-- Responsável por: Usuários, autenticação, sessões, configurações gerais

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL DEFAULT 'user',
    ativo BOOLEAN DEFAULT 1,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME,
    configuracoes TEXT -- JSON com preferências do usuário
);

-- Tabela de sessões
CREATE TABLE IF NOT EXISTS sessoes (
    id TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATETIME NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

-- Tabela de logs do sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    nivel TEXT NOT NULL, -- INFO, WARNING, ERROR, DEBUG
    modulo TEXT NOT NULL,
    usuario_id INTEGER,
    acao TEXT NOT NULL,
    detalhes TEXT,
    ip_address TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

-- Tabela de configurações globais
CREATE TABLE IF NOT EXISTS configuracoes_sistema (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    descricao TEXT,
    tipo TEXT DEFAULT 'string', -- string, number, boolean, json
    data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    modificado_por INTEGER,
    FOREIGN KEY (modificado_por) REFERENCES usuarios (id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_sessoes_usuario ON sessoes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_ativo ON sessoes(ativo);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_sistema(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_modulo ON logs_sistema(modulo);
CREATE INDEX IF NOT EXISTS idx_logs_usuario ON logs_sistema(usuario_id);
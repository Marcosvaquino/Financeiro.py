import sqlite3
import os
import bcrypt

# Caminho para o banco na raiz do projeto (um nível acima)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

def get_connection():
    """Cria conexão com o banco SQLite"""
    # Aumenta timeout para reduzir chances de 'database is locked' em operações concorrentes
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        # Ativa WAL (write-ahead logging) para melhorar concorrência entre leitura/escrita
        conn.execute('PRAGMA journal_mode=WAL;')
        # Seta busy timeout em ms (para SQLite aguardar locks por até 30s)
        conn.execute('PRAGMA busy_timeout = 30000;')
    except Exception:
        # Se a execução das PRAGMAs falhar (por exemplo, em bancos remotos), seguimos com a conexão
        pass
    return conn

def init_db():
    """Inicializa o banco de dados criando tabelas a partir do schema.sql"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

    conn = get_connection()
    cursor = conn.cursor()

    # Executa o schema.sql para criar tabelas
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        script_sql = f.read()

    cursor.executescript(script_sql)
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

    # Garante que exista usuário admin
    criar_usuario_admin()

def criar_usuario_admin():
    """Cria um usuário admin padrão se não existir"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = ?", ("admin@frz.com",))
    if cursor.fetchone() is None:
        senha = "1234"
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin@frz.com", senha_hash, "admin")
        )
        conn.commit()
        print("Usuário admin criado: admin@frz.com / senha: 1234")

    conn.close()

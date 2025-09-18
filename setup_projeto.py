import os

# Estrutura de pastas
folders = [
    "financeiro",
    "financeiro/static",
    "financeiro/templates"
]

# Arquivos e seus conteúdos iniciais
files = {
    "financeiro/main.py": """from flask import Flask, render_template, redirect, url_for
from database import init_db

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/planejamento")
def planejamento():
    return render_template("planejamento.html")

if __name__ == "__main__":
    app.run(debug=True)
""",

    "financeiro/database.py": """import sqlite3

DB_NAME = "financeiro.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    script_sql = open("financeiro/schema.sql", "r", encoding="utf-8").read()
    cursor.executescript(script_sql)
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")
""",

    "financeiro/schema.sql": """-- SCHEMA INICIAL

CREATE TABLE IF NOT EXISTS contas_receber (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    valor REAL NOT NULL,
    vencimento DATE NOT NULL,
    status TEXT CHECK(status IN ('Pendente','Recebido')) NOT NULL,
    data_baixa DATE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contas_pagar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT NOT NULL,
    valor REAL NOT NULL,
    vencimento DATE NOT NULL,
    status TEXT CHECK(status IN ('Em aberto','Pago')) NOT NULL,
    data_baixa DATE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
""",

    "financeiro/templates/base.html": """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Financeiro - FRZ</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="sidebar">
        <h2>Menu</h2>
        <ul>
            <li><a href="{{ url_for('planejamento') }}">Painel</a></li>
            <li><a href="#">Projeção</a></li>
            <li><a href="#">Dashboard</a></li>
            <li><a href="#">Resumo</a></li>
            <li><a href="#">Consolidação</a></li>
        </ul>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
""",

    "financeiro/templates/login.html": """{% extends "base.html" %}
{% block content %}
<h1>Login</h1>
<form method="post" action="/login">
    <label>Email:</label><br>
    <input type="text" name="email"><br><br>
    <label>Senha:</label><br>
    <input type="password" name="senha"><br><br>
    <button type="submit">Entrar</button>
</form>
{% endblock %}
""",

    "financeiro/templates/planejamento.html": """{% extends "base.html" %}
{% block content %}
<h1>Painel de Planejamento</h1>
<p>Aqui vamos carregar os dados de projeção, realizado e despesas gerais.</p>
{% endblock %}
""",

    "financeiro/static/style.css": """body {
    font-family: Arial, sans-serif;
    margin: 0;
    display: flex;
}
.sidebar {
    width: 200px;
    background: #434343;
    color: white;
    min-height: 100vh;
    padding: 20px;
}
.sidebar h2 { color: #ff6600; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar ul li { margin: 15px 0; }
.sidebar ul li a { color: white; text-decoration: none; }
.content {
    flex: 1;
    padding: 20px;
    background: #e3e3e3;
}
""",

    "financeiro/requirements.txt": """flask
dash
pandas
plotly
bcrypt
"""
}

# Criar pastas
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Criar arquivos
for filepath, content in files.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Estrutura do projeto criada com sucesso!")

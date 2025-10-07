#!/usr/bin/env python3
"""
Servidor simplificado apenas para testar o módulo de Análise de Margem
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from financeiro.database import init_db

# Criar app Flask simples
app = Flask(__name__)
app.secret_key = "frz-secret"

# Registrar apenas o blueprint de margem
try:
    from financeiro.margem_analise import margem_bp
    app.register_blueprint(margem_bp)
    print("✅ Módulo de margem carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar módulo de margem: {e}")
    sys.exit(1)

# Rota de teste da API
@app.route("/teste-api")
def teste_api():
    with open('teste_api.html', 'r', encoding='utf-8') as f:
        return f.read()

# Rota de teste
@app.route("/")
def index():
    return '''
    <h1>🚛 Teste do Módulo de Análise de Margem</h1>
    <p>Módulo carregado com sucesso!</p>
    <a href="/frete/margem" style="
        display: inline-block;
        background: #2c3e50;
        color: white;
        padding: 15px 30px;
        text-decoration: none;
        border-radius: 8px;
        font-size: 18px;
        margin-top: 20px;
    ">🔗 Acessar Análise de Margem</a>
    <br><br>
    <a href="/teste-api" style="
        display: inline-block;
        background: #27ae60;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 8px;
        font-size: 16px;
    ">🧪 Testar APIs</a>
    '''

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste...")
    print("📊 Análise de Margem - FRZ Log")
    print("🌐 Acesse: http://127.0.0.1:5000")
    print("🔗 Dashboard: http://127.0.0.1:5000/frete/margem")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
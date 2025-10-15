"""
Script para testar apenas o módulo de armazém
"""

from flask import Flask
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Criar app Flask simples
app = Flask(__name__, 
            template_folder='financeiro/templates',
            static_folder='financeiro/static')

app.config['SECRET_KEY'] = 'dev'

# Registrar apenas o blueprint do armazém
from financeiro.armazem import bp as armazem_bp
app.register_blueprint(armazem_bp)

# Rota raiz
@app.route('/')
def index():
    return '<h1>Teste Armazém</h1><p><a href="/armazem">Ir para Dashboard Armazém</a></p>'

if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask - TESTE ARMAZÉM...")
    print("🌐 Acesse: http://localhost:5000/armazem")
    print()
    
    app.run(debug=True, host="0.0.0.0", port=5000)

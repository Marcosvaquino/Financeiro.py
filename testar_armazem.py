#!/usr/bin/env python3
"""
Script para testar o módulo de armazém
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from financeiro.armazem import bp

app = Flask(__name__, template_folder='financeiro/templates', static_folder='financeiro/static')
app.secret_key = 'dev-key-armazem-test'

# Registrar apenas o blueprint do armazém
app.register_blueprint(bp)

if __name__ == "__main__":
    print("🚀 Servidor de Teste - Dashboard de Armazém")
    print("🌐 Acesse: http://localhost:5001/armazem")
    print("=" * 50)
    
    app.run(debug=True, host="0.0.0.0", port=5001)

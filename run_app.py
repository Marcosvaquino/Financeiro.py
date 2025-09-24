#!/usr/bin/env python3
"""
Arquivo para rodar a aplicação Flask do sistema financeiro.
"""

import sys
import os

# Adicionar o diretório atual ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar e rodar a aplicação
from financeiro.main import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask...")
    print("📊 Sistema Financeiro FRZ")
    print("🌐 Acesse: http://IP_DO_SERVIDOR:5000")
    print("⭐ Para testar semanas estáticas: http://IP_DO_SERVIDOR:5000/planejamento_frz?mes=3&ano=2025")
    print()
    
    app.run(debug=True, host="0.0.0.0", port=5000)
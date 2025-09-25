"""
Script para testar o processamento Pamplona
"""

import os
import sys

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financeiro.pamplona import processar_pamplona

def testar_pamplona():
    """Teste básico do módulo Pamplona."""
    print("🏢 TESTANDO MÓDULO PAMPLONA...")
    
    # Testar com um arquivo inexistente para ver se a estrutura está OK
    arquivo_teste = "arquivo_inexistente.xlsx"
    
    try:
        resultado = processar_pamplona(arquivo_teste)
        print(f"✅ Resultado: {resultado}")
        print("🏢 Estrutura do módulo Pamplona OK!")
        return True
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    testar_pamplona()
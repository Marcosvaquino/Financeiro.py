import requests
import json

# Testar API de dados executivos
base_url = "http://127.0.0.1:5000/api/dados_executivo"

# Testar receitas
print("=== Testando API Receitas ===")
try:
    response = requests.get(f"{base_url}?tipo=receita&mes=9&ano=2025")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro: {e}")

print("\n=== Testando API Despesas ===")
try:
    response = requests.get(f"{base_url}?tipo=despesa&mes=9&ano=2025")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro: {e}")

print("\n=== Testando API Resultado ===")
try:
    response = requests.get(f"{base_url}?tipo=resultado&mes=9&ano=2025")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro: {e}")
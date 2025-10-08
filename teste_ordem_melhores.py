import sys
sys.path.append('.')
import requests
import json

# Testar API dos melhores
url = 'http://127.0.0.1:5000/api/margem/ranking-melhores?tipo=tipologia'
try:
    response = requests.get(url)
    data = response.json()
    print('=== TOP 5 MELHORES (ordem que vem do backend) ===')
    for i, item in enumerate(data[:5]):
        print(f'{i+1}. {item["nome"]} - {item["percentual"]}')
except Exception as e:
    print(f'Erro: {e}')
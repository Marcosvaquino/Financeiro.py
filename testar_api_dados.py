import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados', timeout=10)
    data = response.json()
    
    print(f"Status: {data.get('status')}")
    print(f"Count: {data.get('count')}")
    
    if data.get('data'):
        primeiro_item = data['data'][0]
        print("\nPrimeiro item:")
        for key, value in primeiro_item.items():
            print(f"  {key}: {value}")
        
        # Verificar se tem campos Tipologia e Perfil
        print(f"\nCampos importantes:")
        print(f"  Placa: {primeiro_item.get('Placa', 'AUSENTE')}")
        print(f"  Tipologia: {primeiro_item.get('Tipologia', 'AUSENTE')}")
        print(f"  Perfil: {primeiro_item.get('Perfil', 'AUSENTE')}")
        
        # Verificar quantos itens têm tipologia válida
        tipologias_validas = [item.get('Tipologia') for item in data['data'] if item.get('Tipologia') and item.get('Tipologia') not in ['Não cadastrado', 'Sem placa']]
        print(f"\nTipologias válidas encontradas: {len(tipologias_validas)}")
        print(f"Exemplos: {list(set(tipologias_validas))[:10]}")
        
except Exception as e:
    print(f"Erro: {e}")
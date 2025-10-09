import requests

try:
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados', timeout=5)
    data = response.json()
    
    if data.get('data'):
        primeiro = data['data'][0]
        print(f"Placa: '{primeiro.get('Placa')}'")
        print(f"Tipologia: '{primeiro.get('Tipologia')}'") 
        print(f"Perfil: '{primeiro.get('Perfil')}'")
        
        # Contar válidos
        validos = sum(1 for item in data['data'] if item.get('Tipologia') and item.get('Tipologia') not in ['Não cadastrado', 'Sem placa'])
        print(f"Tipologias válidas: {validos}/{len(data['data'])}")
        
        # Mostrar exemplos únicos
        tipologias = set(item.get('Tipologia') for item in data['data'] if item.get('Tipologia'))
        perfis = set(item.get('Perfil') for item in data['data'] if item.get('Perfil'))
        print(f"Tipologias: {list(tipologias)}")
        print(f"Perfis: {list(perfis)}")
        
except Exception as e:
    print(f"Erro: {e}")
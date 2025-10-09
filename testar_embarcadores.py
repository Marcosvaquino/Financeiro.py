#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados', timeout=10)
    if response.status_code == 200:
        data = response.json()
        
        if 'data' in data and data['data']:
            # Obter embarcadores únicos
            embarcadores = set()
            for item in data['data']:
                if 'Embarcador' in item and item['Embarcador']:
                    embarcadores.add(item['Embarcador'])
            
            print(f"Embarcadores únicos encontrados ({len(embarcadores)}):")
            for embarcador in sorted(embarcadores):
                print(f"  - {embarcador}")
                
            # Contar por embarcador
            print("\nContagem por embarcador:")
            embarcador_count = {}
            for item in data['data']:
                embarcador = item.get('Embarcador', 'Não informado')
                embarcador_count[embarcador] = embarcador_count.get(embarcador, 0) + 1
                
            for embarcador, count in sorted(embarcador_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  {embarcador}: {count} registros")
            
        else:
            print("Nenhum dado encontrado na resposta")
    else:
        print(f"Erro na requisição: {response.status_code}")
        
except Exception as e:
    print(f"Erro: {e}")
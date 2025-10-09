import requests
import csv
from io import StringIO

try:
    # Buscar dados diretamente da planilha
    GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16XYzthDIaF5oNaPSq-UO4cs09Kw_rIUR8r47rbKCV0A/export?format=csv&gid=0"
    
    response = requests.get(GOOGLE_SHEET_URL, timeout=30)
    response.raise_for_status()
    
    print("Primeiras 5 linhas brutas:")
    lines = response.text.strip().split('\n')
    for i, line in enumerate(lines[:5]):
        print(f"Linha {i}: {line}")
    
    print("\n" + "="*50)
    
    # Tentar usar CSV reader em vez de split manual
    csv_data = StringIO(response.text)
    reader = csv.DictReader(csv_data)
    
    print("Cabeçalhos usando csv.DictReader:")
    print(reader.fieldnames)
    
    first_row = next(reader)
    print(f"\nPrimeiro registro:")
    for key, value in first_row.items():
        if 'placa' in key.lower() or 'veic' in key.lower():
            print(f"  ** {key}: '{value}' **")
        elif key in ['Documento', 'Cliente', 'Identificador']:
            print(f"  {key}: '{value}'")
    
    # Verificar mais algumas linhas para encontrar placas reais
    print(f"\nVerificando algumas placas:")
    csv_data.seek(0)
    reader = csv.DictReader(csv_data)
    count = 0
    for row in reader:
        placa = row.get('Placa', '').strip()
        if placa and placa != '' and len(placa) > 2:
            print(f"  Placa encontrada: '{placa}'")
            count += 1
            if count >= 10:
                break
                
except Exception as e:
    print(f"Erro: {e}")
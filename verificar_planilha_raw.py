import requests

try:
    # Buscar dados diretamente da planilha
    GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16XYzthDIaF5oNaPSq-UO4cs09Kw_rIUR8r47rbKCV0A/export?format=csv&gid=0"
    
    response = requests.get(GOOGLE_SHEET_URL, timeout=30)
    response.raise_for_status()
    
    # Processa os dados CSV
    lines = response.text.strip().split('\n')
    if len(lines) < 2:
        print("Dados insuficientes")
    else:
        headers = lines[0].split(',')
        print("Cabeçalhos da planilha:")
        for i, header in enumerate(headers):
            print(f"  {i}: {header}")
        
        print(f"\nPrimeira linha de dados:")
        first_row = lines[1].split(',')
        for i, value in enumerate(first_row):
            if i < len(headers):
                print(f"  {headers[i]}: {value}")
        
        # Procurar colunas que podem conter placas
        print(f"\nProcurando por colunas de placa:")
        placa_headers = [h for h in headers if 'placa' in h.lower() or 'veic' in h.lower()]
        print(f"Cabeçalhos relacionados a veículo/placa: {placa_headers}")
        
except Exception as e:
    print(f"Erro: {e}")
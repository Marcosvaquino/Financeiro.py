"""
Script para gerar arquivo Excel de exemplo para o Mapa de Calor
"""
import pandas as pd

# Dados de exemplo com cidades brasileiras
dados_exemplo = [
    {'Cidade': 'SÃO PAULO', 'Latitude': -23.5505, 'Longitude': -46.6333, 'Valor': 150},
    {'Cidade': 'RIO DE JANEIRO', 'Latitude': -22.9068, 'Longitude': -43.1729, 'Valor': 120},
    {'Cidade': 'BELO HORIZONTE', 'Latitude': -19.9167, 'Longitude': -43.9345, 'Valor': 80},
    {'Cidade': 'BRASÍLIA', 'Latitude': -15.7939, 'Longitude': -47.8828, 'Valor': 95},
    {'Cidade': 'CURITIBA', 'Latitude': -25.4284, 'Longitude': -49.2733, 'Valor': 70},
    {'Cidade': 'RECIFE', 'Latitude': -8.0476, 'Longitude': -34.8770, 'Valor': 65},
    {'Cidade': 'PORTO ALEGRE', 'Latitude': -30.0346, 'Longitude': -51.2177, 'Valor': 85},
    {'Cidade': 'SALVADOR', 'Latitude': -12.9714, 'Longitude': -38.5014, 'Valor': 75},
    {'Cidade': 'FORTALEZA', 'Latitude': -3.7172, 'Longitude': -38.5433, 'Valor': 60},
    {'Cidade': 'MANAUS', 'Latitude': -3.1190, 'Longitude': -60.0217, 'Valor': 45},
    {'Cidade': 'CAMPINAS', 'Latitude': -22.9056, 'Longitude': -47.0608, 'Valor': 110},
    {'Cidade': 'SANTOS', 'Latitude': -23.9618, 'Longitude': -46.3322, 'Valor': 55},
    {'Cidade': 'SÃO JOSÉ DOS CAMPOS', 'Latitude': -23.2237, 'Longitude': -45.9009, 'Valor': 68},
    {'Cidade': 'SOROCABA', 'Latitude': -23.5015, 'Longitude': -47.4526, 'Valor': 52},
    {'Cidade': 'RIBEIRÃO PRETO', 'Latitude': -21.1775, 'Longitude': -47.8208, 'Valor': 72},
    {'Cidade': 'GUARULHOS', 'Latitude': -23.4538, 'Longitude': -46.5333, 'Valor': 88},
]

# Criar DataFrame
df = pd.DataFrame(dados_exemplo)

# Salvar em Excel
nome_arquivo = 'exemplo_mapa_calor.xlsx'
df.to_excel(nome_arquivo, index=False, engine='openpyxl')

print(f"✅ Arquivo '{nome_arquivo}' criado com sucesso!")
print(f"📊 Total de {len(df)} cidades")
print(f"\n📋 Preview dos dados:")
print(df.head(10))

# Criar também versão sem coordenadas (apenas com cidade e valor)
df_simples = df[['Cidade', 'Valor']]
nome_arquivo_simples = 'exemplo_mapa_calor_simples.xlsx'
df_simples.to_excel(nome_arquivo_simples, index=False, engine='openpyxl')
print(f"\n✅ Arquivo simplificado '{nome_arquivo_simples}' criado!")
print("   (Use este se não tiver coordenadas - o sistema vai geocodificar automaticamente)")

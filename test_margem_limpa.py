import pandas as pd
import numpy as np
import os

# Carregar arquivo Excel
file_path = os.path.join('financeiro', 'uploads', 'Manifesto_Acumulado.xlsx')
df = pd.read_excel(file_path)

# Aplicar limpeza como no código corrigido
colunas_necessarias = [
    'Data', 'Tipologia', 'Veículo', 'Destino', 'Cliente_Real',
    'Frete Correto', 'Despesas Gerais'
]

# Preparar dados
df['frete_receber'] = pd.to_numeric(df['Frete Correto'], errors='coerce').fillna(0)
df['frete_pagar'] = pd.to_numeric(df['Despesas Gerais'], errors='coerce').fillna(0)
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

# Cálculos derivados
df['margem_liquida'] = df['frete_receber'] - df['frete_pagar']
df['margem_percentual'] = np.where(df['frete_receber'] > 0, 
                                 (df['margem_liquida'] / df['frete_receber']) * 100, 0)

# Limpeza rigorosa
df = df.dropna(subset=['Data'])
df = df[df['frete_receber'] > 10]  # Remove receitas < R$ 10
df = df[(df['margem_percentual'] >= -200) & (df['margem_percentual'] <= 300)]

print('=== DADOS APÓS LIMPEZA RIGOROSA ===')
print(f'Registros restantes: {len(df)}')
print(f'Margem percentual média: {df["margem_percentual"].mean():.2f}%')
print(f'Margem percentual mínima: {df["margem_percentual"].min():.2f}%')
print(f'Margem percentual máxima: {df["margem_percentual"].max():.2f}%')
print()

# Análise por tipologia limpa
tipologia_limpa = df.groupby('Tipologia').agg({
    'frete_receber': 'sum',
    'frete_pagar': 'sum', 
    'margem_liquida': 'sum',
    'margem_percentual': 'mean'
}).round(2)

print('=== MARGEM POR TIPOLOGIA (DADOS LIMPOS) ===')
print(tipologia_limpa)
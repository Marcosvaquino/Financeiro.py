import pandas as pd
import numpy as np
import os

# Carregar arquivo Excel
file_path = os.path.join('financeiro', 'uploads', 'Manifesto_Acumulado.xlsx')
df = pd.read_excel(file_path)

print('=== REGISTROS PROBLEMÁTICOS ===')
print(f'Total de registros: {len(df)}')
print(f'Registros com receita = 0: {len(df[df["Frete Correto"] == 0])}')
print(f'Registros com receita < 10: {len(df[df["Frete Correto"] < 10])}')
print()

# Filtrar apenas registros válidos (receita > 0)
df_valido = df[df['Frete Correto'] > 0].copy()
print(f'Registros válidos (receita > 0): {len(df_valido)}')

# Recalcular margens com dados válidos
receita_valida = df_valido['Frete Correto']
despesa_valida = df_valido['Despesas Gerais']
margem_valida = receita_valida - despesa_valida
margem_percentual_valida = (margem_valida / receita_valida) * 100

print()
print('=== MARGEM COM DADOS VÁLIDOS ===')
print(f'Margem percentual média: {margem_percentual_valida.mean():.2f}%')
print(f'Margem percentual mínima: {margem_percentual_valida.min():.2f}%')
print(f'Margem percentual máxima: {margem_percentual_valida.max():.2f}%')
print()

# Análise por tipologia com dados válidos
df_valido['margem_liquida'] = margem_valida
df_valido['margem_percentual'] = margem_percentual_valida

tipologia_valida = df_valido.groupby('Tipologia').agg({
    'Frete Correto': 'sum',
    'Despesas Gerais': 'sum', 
    'margem_liquida': 'sum',
    'margem_percentual': 'mean'
}).round(2)

print('=== MARGEM POR TIPOLOGIA (DADOS VÁLIDOS) ===')
print(tipologia_valida)
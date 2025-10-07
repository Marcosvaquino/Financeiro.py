#!/usr/bin/env python3
import pandas as pd

df = pd.read_excel('financeiro/uploads/Manifesto_Acumulado.xlsx')
problematicos = df[df['Cliente_Real'] == '0']

print('=== NOMES PROBLEMÁTICOS (EXATOS) ===')
nomes = problematicos['Cliente'].value_counts()
for nome, count in nomes.items():
    print(f'["{nome}"] = {count} registros')
    print(f'  Normalizado: "{str(nome).upper().replace(" ", "").replace("(", "").replace(")", "").replace("-", "")}"')
    print(f'  Tipo: {type(nome)}')
    print()
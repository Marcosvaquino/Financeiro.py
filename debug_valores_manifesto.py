#!/usr/bin/env python3
"""
Script para analisar valores do manifesto
"""

import pandas as pd

def analisar_valores():
    df = pd.read_excel('financeiro/uploads/Manifesto_Acumulado.xlsx')
    
    print("ANÁLISE DE VALORES:")
    print(f"Frete Correto - Min: {df['Frete Correto'].min():.2f}, Max: {df['Frete Correto'].max():.2f}, Média: {df['Frete Correto'].mean():.2f}")
    print(f"Despesas Gerais - Min: {df['Despesas Gerais'].min():.2f}, Max: {df['Despesas Gerais'].max():.2f}, Média: {df['Despesas Gerais'].mean():.2f}")
    
    # Amostra
    df_sample = df[['Frete Correto', 'Despesas Gerais']].head(10).copy()
    df_sample['Margem'] = df_sample['Frete Correto'] - df_sample['Despesas Gerais']
    df_sample['Margem%'] = (df_sample['Margem'] / df_sample['Frete Correto']) * 100
    
    print("\nAMOSTRA:")
    print(df_sample.to_string())
    
    # Verificar valores zero ou negativos
    print(f"\nVALORES ZERO OU NEGATIVOS:")
    print(f"Frete Correto <= 0: {(df['Frete Correto'] <= 0).sum()}")
    print(f"Despesas Gerais < 0: {(df['Despesas Gerais'] < 0).sum()}")
    
    # Margem geral
    margem_total = (df['Frete Correto'] - df['Despesas Gerais']).sum()
    receita_total = df['Frete Correto'].sum()
    margem_percentual = (margem_total / receita_total) * 100
    
    print(f"\nRESUMO GERAL:")
    print(f"Receita Total: R$ {receita_total:,.2f}")
    print(f"Despesa Total: R$ {df['Despesas Gerais'].sum():,.2f}")
    print(f"Margem Total: R$ {margem_total:,.2f}")
    print(f"Margem %: {margem_percentual:.1f}%")

if __name__ == "__main__":
    analisar_valores()
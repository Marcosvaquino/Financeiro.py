"""
Debug: Identificar diferença entre valores do Painel Frete vs Análise de Margem
"""

import pandas as pd
import numpy as np
import os

def debug_diferenca_valores():
    manifesto_path = os.path.join('financeiro', 'uploads', 'Manifesto_Acumulado.xlsx')
    
    if not os.path.exists(manifesto_path):
        print("❌ Arquivo não encontrado")
        return
    
    # 1. DADOS ORIGINAIS (como no Painel Frete)
    print("=" * 60)
    print("🔍 ANÁLISE DA DIFERENÇA DE VALORES")
    print("=" * 60)
    
    df_original = pd.read_excel(manifesto_path)
    print(f"\n📊 DADOS ORIGINAIS (Painel Frete):")
    print(f"Registros: {len(df_original):,}")
    receita_original = df_original['Frete Correto'].sum()
    despesa_original = df_original['Despesas Gerais'].sum()
    margem_original = receita_original - despesa_original
    margem_pct_original = (margem_original / receita_original * 100) if receita_original > 0 else 0
    
    print(f"Receita: R$ {receita_original:,.2f}")
    print(f"Despesa: R$ {despesa_original:,.2f}")
    print(f"Margem: R$ {margem_original:,.2f}")
    print(f"Margem %: {margem_pct_original:.2f}%")
    
    # 2. DADOS COM FILTROS (como na Análise de Margem)
    print(f"\n📊 DADOS COM FILTROS (Análise de Margem):")
    
    # Carregar só as colunas necessárias
    colunas_necessarias = [
        'Data', 'Tipologia', 'Veículo', 'Destino', 'Cliente_Real',
        'Frete Correto', 'Despesas Gerais', 'Status_Veiculo'
    ]
    
    df = pd.read_excel(manifesto_path, usecols=colunas_necessarias)
    print(f"Registros após seleção de colunas: {len(df):,}")
    
    # Conversões numéricas
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['frete_receber'] = pd.to_numeric(df['Frete Correto'], errors='coerce').fillna(0)
    df['frete_pagar'] = pd.to_numeric(df['Despesas Gerais'], errors='coerce').fillna(0)
    
    # Filtro 1: Remove dados sem data
    antes = len(df)
    df = df.dropna(subset=['Data'])
    removidos_data = antes - len(df)
    print(f"Removidos por data inválida: {removidos_data:,}")
    
    # Filtro 2: Remove receita muito baixa (< R$ 10)
    antes = len(df)
    df = df[df['frete_receber'] > 10]
    removidos_receita = antes - len(df)
    print(f"Removidos por receita < R$ 10: {removidos_receita:,}")
    
    # Cálculos de margem
    df['margem_liquida'] = df['frete_receber'] - df['frete_pagar']
    df['margem_percentual'] = np.where(df['frete_receber'] > 0, 
                                     (df['margem_liquida'] / df['frete_receber']) * 100, 0)
    
    # Filtro 3: Remove margens extremas
    antes = len(df)
    df = df[df['margem_percentual'] >= -200]
    df = df[df['margem_percentual'] <= 300]
    removidos_margem = antes - len(df)
    print(f"Removidos por margem extrema: {removidos_margem:,}")
    
    # Resultados finais
    receita_filtrada = df['frete_receber'].sum()
    despesa_filtrada = df['frete_pagar'].sum()
    margem_filtrada = receita_filtrada - despesa_filtrada
    margem_pct_filtrada = (margem_filtrada / receita_filtrada * 100) if receita_filtrada > 0 else 0
    
    print(f"\nRegistros finais: {len(df):,}")
    print(f"Receita: R$ {receita_filtrada:,.2f}")
    print(f"Despesa: R$ {despesa_filtrada:,.2f}")
    print(f"Margem: R$ {margem_filtrada:,.2f}")
    print(f"Margem %: {margem_pct_filtrada:.2f}%")
    
    # 3. COMPARAÇÃO FINAL
    print(f"\n" + "=" * 60)
    print("📊 COMPARAÇÃO FINAL")
    print("=" * 60)
    
    diff_receita = receita_original - receita_filtrada
    diff_despesa = despesa_original - despesa_filtrada
    diff_margem = margem_original - margem_filtrada
    diff_pct = margem_pct_original - margem_pct_filtrada
    
    print(f"Diferença na Receita: R$ {diff_receita:,.2f}")
    print(f"Diferença na Despesa: R$ {diff_despesa:,.2f}")
    print(f"Diferença na Margem: R$ {diff_margem:,.2f}")
    print(f"Diferença na Margem %: {diff_pct:.2f}%")
    
    # 4. ANÁLISE DOS REGISTROS REMOVIDOS
    print(f"\n📋 RESUMO DOS FILTROS:")
    print(f"Total removido por data inválida: {removidos_data:,}")
    print(f"Total removido por receita baixa: {removidos_receita:,}")
    print(f"Total removido por margem extrema: {removidos_margem:,}")
    total_removidos = removidos_data + removidos_receita + removidos_margem
    print(f"Total geral removido: {total_removidos:,}")
    print(f"% de dados removidos: {(total_removidos / len(df_original) * 100):.1f}%")
    
    print(f"\n✅ PROBLEMA IDENTIFICADO!")
    print(f"🔍 A Análise de Margem está aplicando filtros que removem dados")
    print(f"🔍 O Painel Frete usa todos os dados sem filtros")
    print(f"🔍 Esta é a causa da diferença nos valores!")

if __name__ == "__main__":
    debug_diferenca_valores()
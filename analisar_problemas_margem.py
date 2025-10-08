"""
Análise dos registros problemáticos nos cálculos de margem
"""
import sys
sys.path.append('.')
from financeiro.margem_analise import margem_service
import pandas as pd

def analisar_problemas_margem():
    df = margem_service.carregar_dados_manifesto()

    print('📊 ANÁLISE DE REGISTROS PROBLEMÁTICOS')
    print('=' * 50)

    # Calcular estatísticas por placa
    stats_placa = df.groupby(['Placa', 'Tipologia']).agg({
        'frete_receber': 'sum',
        'frete_pagar': 'sum'
    }).reset_index()

    stats_placa['margem'] = stats_placa['frete_receber'] - stats_placa['frete_pagar']
    stats_placa['margem_pct'] = (stats_placa['margem'] / stats_placa['frete_receber'] * 100)

    print(f'Total de placas: {len(stats_placa)}')

    # Problemas identificados
    receita_baixa = stats_placa[stats_placa['frete_receber'] < 50]
    margem_extrema = stats_placa[(stats_placa['margem_pct'] < -200) | (stats_placa['margem_pct'] > 200)]
    prejuizo_alto = stats_placa[stats_placa['margem_pct'] < -100]

    print(f'\nProblemas encontrados:')
    print(f'- Receita < R$ 50: {len(receita_baixa)} placas')
    print(f'- Margem extrema (< -200% ou > 200%): {len(margem_extrema)} placas') 
    print(f'- Prejuízo alto (< -100%): {len(prejuizo_alto)} placas')

    print(f'\nExemplos de margens extremas (melhores):')
    extremas = stats_placa.nlargest(5, 'margem_pct')
    for _, row in extremas.iterrows():
        placa = row['Placa']
        margem = row['margem_pct']
        receita = row['frete_receber']
        print(f'{placa}: {margem:.1f}% (R$ {receita:.2f} receita)')

    print(f'\nExemplos de margens extremas (piores):')
    piores = stats_placa.nsmallest(5, 'margem_pct')
    for _, row in piores.iterrows():
        placa = row['Placa']
        margem = row['margem_pct']
        receita = row['frete_receber']
        print(f'{placa}: {margem:.1f}% (R$ {receita:.2f} receita)')
    
    print(f'\n🎯 RECOMENDAÇÃO:')
    print(f'Filtrar placas com receita < R$ 100 e margens entre -100% e +100%')
    print(f'Isso eliminaria {len(receita_baixa) + len(margem_extrema)} placas problemáticas')
    
    # Calcular margem sem os problemas
    dados_limpos = stats_placa[
        (stats_placa['frete_receber'] >= 100) & 
        (stats_placa['margem_pct'] >= -100) & 
        (stats_placa['margem_pct'] <= 100)
    ]
    
    print(f'\nCom dados limpos:')
    print(f'- Placas restantes: {len(dados_limpos)}')
    if len(dados_limpos) > 0:
        print(f'- Margem média: {dados_limpos["margem_pct"].mean():.1f}%')
        print(f'- Melhor placa: {dados_limpos.loc[dados_limpos["margem_pct"].idxmax(), "Placa"]} ({dados_limpos["margem_pct"].max():.1f}%)')
        print(f'- Pior placa: {dados_limpos.loc[dados_limpos["margem_pct"].idxmin(), "Placa"]} ({dados_limpos["margem_pct"].min():.1f}%)')

if __name__ == "__main__":
    analisar_problemas_margem()
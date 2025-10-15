"""
Teste do painel consolidado de armazém
"""
import sys
sys.path.insert(0, r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py')

from financeiro.armazem import carregar_dados_armazem
import pandas as pd

# Carrega os dados
print("📦 Carregando dados do armazém...")
df = carregar_dados_armazem()

if df is None or df.empty:
    print("❌ Erro: Nenhum dado disponível")
    sys.exit(1)

print(f"✅ Dados carregados: {len(df)} linhas")
print(f"\nColunas disponíveis: {list(df.columns)}\n")

# Pega última data disponível
ultima_data = df['Data'].max()
mes_filtro = ultima_data.month
ano_filtro = ultima_data.year

print(f"📅 Processando dados de: {mes_filtro}/{ano_filtro}")

# Filtra por mês/ano
df_filtrado = df[(df['Mes_Num'] == mes_filtro) & (df['Ano'] == ano_filtro)].copy()

print(f"Registros do mês: {len(df_filtrado)}")

# Agrupa por dia (soma SJC + JAC)
consolidado_dia = df_filtrado.groupby('Dia').agg({
    'Geral_Peso': 'sum',
    'Geral_Carros': 'sum'
}).reset_index()

consolidado_dia = consolidado_dia.sort_values('Dia')

print(f"\n📊 Dados consolidados por dia:")
print(consolidado_dia.to_string())

# Calcula métricas
peso_acumulado = consolidado_dia['Geral_Peso'].sum()
carros_acumulado = consolidado_dia['Geral_Carros'].sum()
dias_operacao = len(consolidado_dia[consolidado_dia['Geral_Peso'] > 0])
media_peso_carro = peso_acumulado / carros_acumulado if carros_acumulado > 0 else 0
media_peso_dia = peso_acumulado / dias_operacao if dias_operacao > 0 else 0
media_carros_dia = carros_acumulado / dias_operacao if dias_operacao > 0 else 0

print(f"\n📈 MÉTRICAS:")
print(f"  • Peso Acumulado: {peso_acumulado:,.0f}")
print(f"  • Carros Acumulado: {carros_acumulado:,.0f}")
print(f"  • Média Peso/Carro: {media_peso_carro:,.0f}")
print(f"  • Média Peso/Dia: {media_peso_dia:,.0f}")
print(f"  • Média Carros/Dia: {media_carros_dia:,.0f}")

print("\n✅ Teste concluído com sucesso!")

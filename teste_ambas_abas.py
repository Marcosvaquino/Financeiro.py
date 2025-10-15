import sys
sys.path.insert(0, r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py')

from financeiro.armazem import carregar_dados_armazem

df = carregar_dados_armazem()

print('=' * 80)
print('✅ DADOS CARREGADOS COM SUCESSO!')
print('=' * 80)
print(f'\n📊 Total de registros: {len(df)}')
print(f'\n🏢 Distribuição por Filial:')
print(df['Filial'].value_counts())

print(f'\n📅 Período: {df["Data"].min()} até {df["Data"].max()}')
print(f'\n🚚 Total Geral de Carros: {int(df["Geral_Carros"].sum())}')

print('\n' + '=' * 80)
print('PRIMEIROS 3 REGISTROS - SJC')
print('=' * 80)
print(df[df["Filial"]=="SJC"].head(3)[["Data","Filial","Geral_Carros","Mafrig_Foods_Carros","Friboi_Carros", "Valencio"]])

print('\n' + '=' * 80)
print('PRIMEIROS 3 REGISTROS - JAC')
print('=' * 80)
print(df[df["Filial"]=="JAC"].head(3)[["Data","Filial","Geral_Carros","Adoro_Carros","Mieggs_Carros","Minerva_JAC_Carros"]])

print('\n' + '=' * 80)
print('VERIFICAÇÃO SETEMBRO 2025')
print('=' * 80)
df_set = df[(df['Mes_Num'] == 9) & (df['Ano'] == 2025)]
print(f'\nTotal de registros em Setembro: {len(df_set)}')
print(f'SJC: {len(df_set[df_set["Filial"]=="SJC"])} registros - {int(df_set[df_set["Filial"]=="SJC"]["Geral_Carros"].sum())} carros')
print(f'JAC: {len(df_set[df_set["Filial"]=="JAC"])} registros - {int(df_set[df_set["Filial"]=="JAC"]["Geral_Carros"].sum())} carros')

import sys
sys.path.insert(0, r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py')

from financeiro.armazem import carregar_dados_armazem

df = carregar_dados_armazem()

# Filtra setembro de 2025
df_set = df[(df['Mes_Num'] == 9) & (df['Ano'] == 2025)]

print('=' * 80)
print('ANÁLISE SETEMBRO 2025 - EMBARCADORES')
print('=' * 80)

print(f'\nTotal de registros: {len(df_set)}')
print(f'SJC: {len(df_set[df_set["Filial"]=="SJC"])} dias')
print(f'JAC: {len(df_set[df_set["Filial"]=="JAC"])} dias')

print('\n' + '=' * 80)
print('CARROS POR EMBARCADOR - SETEMBRO 2025')
print('=' * 80)

# SJC
print('\n🏢 SJC:')
df_sjc = df_set[df_set['Filial'] == 'SJC']
print(f"  MIEGGS (Mafrig Foods): {int(df_sjc['Mafrig_Foods_Carros'].sum())} carros")
print(f"  FRIBOI: {int(df_sjc['Friboi_Carros'].sum())} carros")
print(f"  MINERVA (Mafrig Atacado): {int(df_sjc['Mafrig_Atacado_Carros'].sum())} carros")
print(f"  GOLD PÃO: {int(df_sjc['Gold_Pao_Carros'].sum())} carros")
print(f"  COMPARTILHADO (FRZ LOG): {int(df_sjc['Compartilhado_Carros'].sum())} carros")
print(f"    - VALENCIO (peso): {df_sjc['Valencio_Peso'].sum() / 1000:.2f}t")
print(f"    - ALIBEM (peso): {df_sjc['Alibem_Agra_Peso'].sum() / 1000:.2f}t")
print(f"    - SAUDALI (peso): {df_sjc['Saudali_Peso'].sum() / 1000:.2f}t")
print(f"    - PAMPLONA (peso): {df_sjc['Pamplona_Peso'].sum() / 1000:.2f}t")
print(f"    - GT FOODS (peso): {df_sjc['GT_Foods_Peso'].sum() / 1000:.2f}t")
print(f"    - SANTA LUCIA (peso): {df_sjc['Santa_Lucia_Peso'].sum() / 1000:.2f}t")
print(f"  MAFRIG (soma pesos compart): {(df_sjc['Valencio_Peso'].sum() + df_sjc['Alibem_Agra_Peso'].sum() + df_sjc['Saudali_Peso'].sum() + df_sjc['Pamplona_Peso'].sum() + df_sjc['GT_Foods_Peso'].sum() + df_sjc['Santa_Lucia_Peso'].sum()) / 1000:.2f}t")

# JAC
print('\n🏢 JAC:')
df_jac = df_set[df_set['Filial'] == 'JAC']
print(f"  ADORO: {int(df_jac['Adoro_Carros'].sum())} carros")
print(f"  VISTA FOODS: {int(df_jac['Vista_Foods_Carros'].sum())} carros")
print(f"  MIEGGS: {int(df_jac['Mieggs_Carros'].sum())} carros")
print(f"  MINERVA: {int(df_jac['Minerva_JAC_Carros'].sum())} carros")

print('\n' + '=' * 80)
print('PESO POR EMBARCADOR - SETEMBRO 2025 (em toneladas)')
print('=' * 80)

# SJC
print('\n🏢 SJC:')
print(f"  MIEGGS (Mafrig Foods): {df_sjc['Mafrig_Foods_Peso'].sum() / 1000:.2f}t")
print(f"  FRIBOI: {df_sjc['Friboi_Peso'].sum() / 1000:.2f}t")
print(f"  MINERVA (Mafrig Atacado): {df_sjc['Mafrig_Atacado_Peso'].sum() / 1000:.2f}t")
print(f"  GOLD PÃO: {df_sjc['Gold_Pao_Peso'].sum() / 1000:.2f}t")
print(f"  MAFRIG (Compartilhado): {df_sjc['Compartilhado_Peso'].sum() / 1000:.2f}t")

# JAC
print('\n🏢 JAC:')
print(f"  ADORO: {df_jac['Adoro_Peso'].sum() / 1000:.2f}t")
print(f"  VISTA FOODS: {df_jac['Vista_Foods_Peso'].sum() / 1000:.2f}t")
print(f"  MIEGGS: {df_jac['Mieggs_Peso'].sum() / 1000:.2f}t")
print(f"  MINERVA: {df_jac['Minerva_JAC_Peso'].sum() / 1000:.2f}t")

print('\n' + '=' * 80)
print('COMPARAÇÃO COM SEU PRINT (SETEMBRO):')
print('=' * 80)
print('\nSeu Print mostra:')
print('  MIEGGS: 79 carros / 38.881t')
print('  FRIBOI: 144 carros / 252.792t')
print('  GOLD PÃO: 345 carros / 541.724t')
print('  MINERVA: 419 carros / 554.552t')
print('  MAFRIG: 381 carros / 780.933t')
print('  FRZ LOG: 662 carros / 1.686.310t')
print('  ADORO: 484 carros / 1.516.597t')

print('\nVerificando se bate...')
print(f"  Total carros SJC: {int(df_sjc['Geral_Carros'].sum())}")
print(f"  Total carros JAC: {int(df_jac['Geral_Carros'].sum())}")
print(f"  Total geral: {int(df_set['Geral_Carros'].sum())}")

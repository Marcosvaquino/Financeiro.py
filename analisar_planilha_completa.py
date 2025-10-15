import pandas as pd

# Arquivo da planilha
arquivo = r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro\uploads\ARMAZEM.xlsx'

# Lista as abas
xl = pd.ExcelFile(arquivo)
print('=' * 80)
print('ABAS DISPONÍVEIS NA PLANILHA:')
print('=' * 80)
for i, sheet in enumerate(xl.sheet_names):
    print(f"{i+1}. {sheet}")

print('\n\n')

# Analisa cada aba
for sheet_name in xl.sheet_names:
    print('=' * 80)
    print(f'ABA: {sheet_name}')
    print('=' * 80)
    
    # Lê as primeiras 5 linhas sem cabeçalho
    df = pd.read_excel(arquivo, sheet_name=sheet_name, header=None, nrows=5)
    
    print(f"\nDimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print("\nPrimeiras 5 linhas:")
    print(df.to_string())
    
    # Mostra as colunas 0-10
    print("\n\nColunas 0-10 (primeiras 10 linhas):")
    df_full = pd.read_excel(arquivo, sheet_name=sheet_name, header=None, nrows=10)
    print(df_full.iloc[:, 0:11].to_string())
    
    # Total de linhas
    df_total = pd.read_excel(arquivo, sheet_name=sheet_name, header=None)
    print(f"\n\nTotal de linhas na aba: {len(df_total)}")
    
    print('\n\n')

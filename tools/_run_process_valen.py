import sys
sys.path.append(r'D:\OneDrive\PROJETOFINANCEIRO.PY')
from financeiro.frete import process_frete_file
print('Processing...')
out = process_frete_file(r'D:\valen.csv')
print('Done ->', out)

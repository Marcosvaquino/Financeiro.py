import sys
sys.path.append(r'D:\OneDrive\PROJETOFINANCEIRO.PY')
from financeiro.frete import process_frete_file
path = r'D:\OneDrive\PROJETOFINANCEIRO.PY\financeiro\uploads\frete\manifestos_22-09-2025_01-32 VALENCIO ATE 15-09.xlsx'
print('Processing', path)
out = process_frete_file(path)
print('Processed ->', out)

import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from financeiro import importacao

path = os.path.join(ROOT, 'financeiro', 'uploads', 'contas-a-receber.csv')
print('Arquivo:', path)
if not os.path.exists(path):
    print('Arquivo nao existe:', path)
    sys.exit(1)
print('Reimportando contas-a-receber...')
importacao.salvar_contas_receber(path)
print('Concluido')

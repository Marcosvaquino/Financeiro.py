import os
import sys
# ajusta path para importar o pacote financeiro
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from financeiro import importacao, main

uploads_path = os.path.join(ROOT, 'financeiro', 'uploads', 'contas-a-pagar.csv')
print('Arquivo a reimportar:', uploads_path)

if not os.path.exists(uploads_path):
    print('Arquivo não encontrado. Certifique-se que existe em financeiro/uploads/contas-a-pagar.csv')
    sys.exit(1)

# Reimporta contas a pagar
try:
    print('Reimportando contas a pagar...')
    importacao.salvar_contas_pagar(uploads_path)
    print('Reimportação concluída.')
except Exception as e:
    print('Erro ao reimportar:', e)
    raise

# Chama a função de build para validar
try:
    print('\nExecutando build_dashboard_data_with_filters(\'07\', \'2025\')')
    data = main.build_dashboard_data_with_filters('07', '2025')
    print('Chaves retornadas:', sorted(list(data.keys())))
    print('total_receber_raw type:', type(data.get('total_receber_raw')) , 'value:', data.get('total_receber_raw'))
    print('total_pagar_raw type:', type(data.get('total_pagar_raw')) , 'value:', data.get('total_pagar_raw'))
    print('recebido_receber_raw type:', type(data.get('recebido_receber_raw')) , 'value:', data.get('recebido_receber_raw'))
    lanc = data.get('lancamentos') or []
    print('\nPrimeiros 5 lançamentos (nome, valor, vencimento, status, tipo):')
    for i, row in enumerate(lanc[:5]):
        print(i+1, row)
except Exception as e:
    print('Erro ao executar build:', e)
    raise

print('\nValidação finalizada.')

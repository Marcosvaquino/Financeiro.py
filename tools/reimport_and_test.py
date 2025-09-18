import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from financeiro import importacao, main

uploads_dir = os.path.join(os.path.dirname(importacao.__file__), 'uploads')
filepath = os.path.join(uploads_dir, 'contas-a-pagar.csv')

print('Arquivo alvo:', filepath)
print('Existe:', os.path.exists(filepath))

try:
    print('\n==> Iniciando reimport de contas-a-pagar.csv')
    importacao.salvar_contas_pagar(filepath)
    print('Reimport concluído com sucesso')
except Exception as e:
    print('Erro durante reimport:', repr(e))

print('\n==> Executando build_dashboard_data_with_filters("07","2025")')
try:
    data = main.build_dashboard_data_with_filters('07', '2025')
    keys = ['total_receber_raw', 'total_pagar_raw', 'projecao_receber_raw', 'recebido_receber_raw']
    for k in keys:
        print(k, '->', type(data.get(k)), data.get(k))

    lanc = data.get('lancamentos') or []
    print('\nAmostra de lançamentos (primeiras 10):')
    for i, l in enumerate(lanc[:10]):
        types = [type(x) for x in l]
        print(i+1, types, l)
except Exception as e:
    print('Erro ao executar build_dashboard_data_with_filters:', repr(e))

print('\nFim do teste')

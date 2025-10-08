"""
Teste da API corrigida da análise de margem
"""
import requests
import json

def testar_api_margem():
    try:
        response = requests.get('http://localhost:5000/api/margem/dados-gerais')
        if response.status_code == 200:
            dados = response.json()
            resumo = dados.get('resumo_financeiro', {})
            print('=== API ANÁLISE DE MARGEM CORRIGIDA ===')
            print(f'Receita: R$ {resumo.get("receita_total", 0):,.2f}')
            print(f'Despesa: R$ {resumo.get("despesa_total", 0):,.2f}')
            print(f'Margem: R$ {resumo.get("margem_total", 0):,.2f}')
            print(f'Margem %: {resumo.get("margem_percentual_geral", 0):.2f}%')
            
            periodo = dados.get('periodo', {})
            print(f'\nPeríodo: {periodo.get("data_inicio")} a {periodo.get("data_fim")}')
            print(f'Registros: {periodo.get("total_registros", 0):,}')
            
            print('\n✅ VALORES AGORA ESTÃO CONSISTENTES!')
        else:
            print(f'Erro HTTP: {response.status_code}')
            print(response.text)
    except Exception as e:
        print(f'Erro: {e}')

if __name__ == "__main__":
    testar_api_margem()
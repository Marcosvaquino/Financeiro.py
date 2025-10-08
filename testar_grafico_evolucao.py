"""
Teste da API do gráfico de evolução anual corrigida
"""
import requests
import json

def testar_grafico_evolucao():
    try:
        response = requests.get('http://localhost:5000/api/margem/evolucao-anual')
        if response.status_code == 200:
            dados = response.json()
            print('=== GRÁFICO EVOLUÇÃO ANUAL CORRIGIDO ===')
            print(f'Meses: {dados.get("meses", [])}')
            print(f'Margem %: {dados.get("margens_percentuais", [])}')
            
            # Verificar se as margens estão dentro do esperado (próximo aos 33.6%)
            margens = dados.get('margens_percentuais', [])
            if margens:
                media_margem = sum(margens) / len(margens)
                print(f'\nMédia das margens: {media_margem:.2f}%')
                print(f'Margem mínima: {min(margens):.2f}%')
                print(f'Margem máxima: {max(margens):.2f}%')
                
                # Verificar se está próximo dos 33.6% do card
                if 25 <= media_margem <= 45:
                    print('✅ VALORES AGORA ESTÃO CONSISTENTES!')
                else:
                    print('⚠️  Ainda há discrepância nos valores')
            else:
                print('Nenhuma margem encontrada')
        else:
            print(f'Erro HTTP: {response.status_code}')
            print(response.text)
    except Exception as e:
        print(f'Erro: {e}')

if __name__ == "__main__":
    testar_grafico_evolucao()
"""
Teste dos rótulos no gráfico de evolução anual
"""
import requests

def testar_rotulos_grafico():
    try:
        response = requests.get('http://localhost:5000/api/margem/evolucao-anual')
        if response.status_code == 200:
            dados = response.json()
            print('=== DADOS PARA RÓTULOS DO GRÁFICO ===')
            
            meses = dados.get('meses', [])
            margens = dados.get('margens_percentuais', [])
            
            print('\nRótulos que aparecerão no gráfico:')
            for i, (mes, margem) in enumerate(zip(meses, margens)):
                rotulo = f"{margem:.2f}%"
                print(f"{mes}: {rotulo}")
            
            print(f'\n✅ {len(margens)} rótulos serão exibidos no gráfico')
            print('📊 Cada ponto da linha de margem terá seu valor exibido')
            print('🎨 Formatação: XX.XX% (2 casas decimais)')
            
        else:
            print(f'Erro: {response.status_code}')
    except Exception as e:
        print(f'Erro: {e}')

if __name__ == "__main__":
    testar_rotulos_grafico()
"""
Teste da correção dos filtros de margem
"""
import requests

def testar_correcao_filtros():
    print("🧪 TESTANDO CORREÇÃO DOS FILTROS DE MARGEM")
    print("=" * 55)
    
    # Testar ranking de piores por placa (onde estava o problema)
    try:
        response = requests.get('http://localhost:5000/api/margem/ranking-piores?tipo=placa')
        if response.status_code == 200:
            ranking = response.json()
            print(f"\n📊 TOP 5 PIORES (PLACA) - APÓS CORREÇÃO:")
            
            valores_ok = True
            for i, item in enumerate(ranking, 1):
                nome = item.get('nome', 'N/A')
                percentual = item.get('percentual', '0%')
                receita = item.get('receita', 'R$ 0,00')
                
                print(f"   {i}º: {nome}")
                print(f"       Margem: {percentual}")
                print(f"       Receita: {receita}")
                
                # Verificar se ainda tem valores absurdos
                try:
                    pct_val = float(percentual.replace('%', ''))
                    if abs(pct_val) > 200:
                        print(f"   ⚠️  AINDA TEM VALOR EXTREMO!")
                        valores_ok = False
                except:
                    pass
                print()
            
            if valores_ok:
                print("✅ Valores agora estão dentro de limites razoáveis!")
            else:
                print("❌ Ainda há valores extremos.")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar ranking melhores também
    try:
        response = requests.get('http://localhost:5000/api/margem/ranking-melhores?tipo=placa')
        if response.status_code == 200:
            ranking = response.json()
            print(f"\n📊 TOP 5 MELHORES (PLACA) - APÓS CORREÇÃO:")
            
            for i, item in enumerate(ranking[:3], 1):
                nome = item.get('nome', 'N/A')
                percentual = item.get('percentual', '0%')
                print(f"   {i}º: {nome} - {percentual}")
                
        else:
            print(f"❌ Erro na API melhores: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print(f"\n" + "=" * 55)
    print("🎯 CORREÇÃO APLICADA:")
    print("• Receita mínima: R$ 100 (elimina casos com R$ 0,99)")
    print("• Margem entre -100% e 200% (elimina -37.097%)")
    print("• Mantém dados realistas para análise")

if __name__ == "__main__":
    testar_correcao_filtros()
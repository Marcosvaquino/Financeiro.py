"""
Teste da API com filtros de perfil funcionando
"""
import requests
import json

def testar_api_filtros():
    print("🧪 Testando APIs com filtros de perfil...")
    
    base_url = "http://127.0.0.1:5000"
    
    # Teste 1: API de filtros (verificar se perfis estão disponíveis)
    print("\n1️⃣ Testando /api/margem/filtros...")
    try:
        response = requests.get(f"{base_url}/api/margem/filtros")
        if response.status_code == 200:
            data = response.json()
            if 'perfis' in data:
                print(f"✅ Perfis disponíveis: {data['perfis']}")
            else:
                print("❌ Campo 'perfis' não encontrado na resposta")
        else:
            print(f"❌ Erro na API filtros: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao chamar API filtros: {e}")
    
    # Teste 2: API dados gerais sem filtro
    print("\n2️⃣ Testando /api/margem/dados-gerais (sem filtro)...")
    try:
        response = requests.get(f"{base_url}/api/margem/dados-gerais")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Receita total (todos): R$ {data['resumo_financeiro']['receita_total']:,.2f}")
            print(f"✅ Total operações (todos): {data['kpis']['total_operacoes']}")
        else:
            print(f"❌ Erro na API dados gerais: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao chamar API dados gerais: {e}")
    
    # Teste 3: API dados gerais com filtro FIXO
    print("\n3️⃣ Testando /api/margem/dados-gerais (perfil=FIXO)...")
    try:
        response = requests.get(f"{base_url}/api/margem/dados-gerais?perfil=FIXO")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Receita FIXO: R$ {data['resumo_financeiro']['receita_total']:,.2f}")
            print(f"✅ Operações FIXO: {data['kpis']['total_operacoes']}")
            print(f"✅ Margem % FIXO: {data['resumo_financeiro']['margem_percentual_geral']:.1f}%")
        else:
            print(f"❌ Erro na API dados gerais FIXO: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao chamar API dados gerais FIXO: {e}")
    
    # Teste 4: API dados gerais com filtro SPOT
    print("\n4️⃣ Testando /api/margem/dados-gerais (perfil=SPOT)...")
    try:
        response = requests.get(f"{base_url}/api/margem/dados-gerais?perfil=SPOT")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Receita SPOT: R$ {data['resumo_financeiro']['receita_total']:,.2f}")
            print(f"✅ Operações SPOT: {data['kpis']['total_operacoes']}")
            print(f"✅ Margem % SPOT: {data['resumo_financeiro']['margem_percentual_geral']:.1f}%")
        else:
            print(f"❌ Erro na API dados gerais SPOT: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao chamar API dados gerais SPOT: {e}")
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_api_filtros()
#!/usr/bin/env python3
"""
Teste da API de filtros
"""

import requests
import json

def testar_api():
    """Testa a API de filtros diretamente"""
    url = "http://127.0.0.1:5000/frete/painel/api/dados"
    
    # Teste 1: Filtro por cliente Friboi
    filtros = {
        "perfil": "TODOS",
        "mes": "AGO", 
        "ano": "2025",
        "clientes": ["Friboi"],
        "veiculos": []
    }
    
    print("🔍 TESTANDO API DE FILTROS")
    print("=" * 40)
    print(f"📡 URL: {url}")
    print(f"📋 Filtros: {filtros}")
    
    try:
        response = requests.post(url, json=filtros, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta recebida!")
            
            if 'frete_diario' in data:
                frete_data = data['frete_diario']
                if 'totais_mensais' in frete_data:
                    totais = frete_data['totais_mensais']
                    print(f"💰 Frete Correto: R$ {totais['frete_correto']:,.2f}")
                    print(f"💰 Despesas Gerais: R$ {totais['despesas_gerais']:,.2f}")
                else:
                    print("⚠️ Sem totais_mensais nos dados")
            else:
                print("⚠️ Sem frete_diario nos dados")
                
            print(f"🔑 Chaves na resposta: {list(data.keys())}")
            
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando")
        print("💡 Execute: python run_app.py")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    testar_api()
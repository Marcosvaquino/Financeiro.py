#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se o mapeamento de clientes está funcionando corretamente
nas futuras importações de manifesto.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from financeiro.cliente_helper import ClienteHelper

def testar_mapeamento_clientes():
    """Testa se o mapeamento de clientes está funcionando corretamente"""
    print("🧪 TESTE DE MAPEAMENTO DE CLIENTES")
    print("=" * 50)
    
    # Clientes comuns que aparecem nos manifestos
    clientes_teste = [
        "Adoro Varzea Paulista",
        "Marfrig ( BRF )",
        "Adoro Vista Foods", 
        "Transferência",
        "FRZ Log",
        "MINERVA",
        "Friboi",
        "GOLD PAO",
        "BRF ( SADIA )",
        "MEGGS"
    ]
    
    print(f"📋 Testando {len(clientes_teste)} clientes comuns do manifesto:")
    print()
    
    # Testar a nova função de busca inteligente
    resultados = ClienteHelper.buscar_multiplos_nomes_manifesto(clientes_teste)
    
    sucessos = 0
    falhas = 0
    
    for cliente_original, dados in resultados.items():
        if dados.get('encontrado', False):
            print(f"✅ '{cliente_original}' → '{dados['nome_real']}' (método: {dados.get('metodo', 'unknown')})")
            sucessos += 1
        else:
            print(f"❌ '{cliente_original}' → NÃO ENCONTRADO")
            falhas += 1
    
    print()
    print(f"📊 RESULTADO DO TESTE:")
    print(f"   ✅ Sucessos: {sucessos}/{len(clientes_teste)} ({sucessos/len(clientes_teste)*100:.1f}%)")
    print(f"   ❌ Falhas: {falhas}/{len(clientes_teste)} ({falhas/len(clientes_teste)*100:.1f}%)")
    
    if falhas == 0:
        print()
        print("🎉 TESTE PASSOU! Mapeamento funcionando 100% corretamente!")
        print("✅ Futuras importações de manifesto devem funcionar perfeitamente.")
    else:
        print()
        print("⚠️ ATENÇÃO: Alguns clientes não foram encontrados.")
        print("💡 Verifique se esses clientes estão cadastrados na tabela clientes_suporte.")
    
    return sucessos == len(clientes_teste)

if __name__ == "__main__":
    testar_mapeamento_clientes()
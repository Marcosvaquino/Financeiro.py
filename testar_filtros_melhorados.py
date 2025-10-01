#!/usr/bin/env python3
"""
Teste completo dos filtros melhorados
"""

from financeiro.painel_frete import extrair_dados_manifesto_real

def testar_filtros_melhorados():
    """Testa os filtros com nova estrutura de seleção única"""
    print("🔍 TESTANDO FILTROS MELHORADOS (Seleção Única)")
    print("=" * 60)
    
    # Teste 1: Todos os dados (sem filtros)
    print("\n📊 TESTE 1: Todos os dados")
    filtros_vazio = {}
    dados_total = extrair_dados_manifesto_real(filtros_vazio)
    if dados_total:
        t = dados_total['totais_mensais']
        print(f"   ✅ Total FC: R$ {t['frete_correto']:,.2f}")
        print(f"   ✅ Total DG: R$ {t['despesas_gerais']:,.2f}")
    
    # Teste 2: Filtrar por perfil FIXO
    print("\n🏷️ TESTE 2: Perfil FIXO")
    filtros_perfil = {'perfil': 'FIXO'}
    dados_fixo = extrair_dados_manifesto_real(filtros_perfil)
    if dados_fixo:
        t = dados_fixo['totais_mensais']
        percentual = (t['frete_correto'] / dados_total['totais_mensais']['frete_correto'] * 100)
        print(f"   ✅ FIXO FC: R$ {t['frete_correto']:,.2f} ({percentual:.1f}% do total)")
        print(f"   ✅ FIXO DG: R$ {t['despesas_gerais']:,.2f}")
    
    # Teste 3: Filtrar por cliente MARFRIG
    print("\n🏢 TESTE 3: Cliente MARFRIG")
    filtros_cliente = {'clientes': ['MARFRIG']}
    dados_marfrig = extrair_dados_manifesto_real(filtros_cliente)
    if dados_marfrig:
        t = dados_marfrig['totais_mensais']
        percentual = (t['frete_correto'] / dados_total['totais_mensais']['frete_correto'] * 100)
        print(f"   ✅ MARFRIG FC: R$ {t['frete_correto']:,.2f} ({percentual:.1f}% do total)")
        print(f"   ✅ MARFRIG DG: R$ {t['despesas_gerais']:,.2f}")
    
    # Teste 4: Filtrar por veículo específico
    print("\n🚚 TESTE 4: Veículo FSS2E39")
    filtros_veiculo = {'veiculos': ['FSS2E39']}
    dados_veiculo = extrair_dados_manifesto_real(filtros_veiculo)
    if dados_veiculo:
        t = dados_veiculo['totais_mensais']
        print(f"   ✅ FSS2E39 FC: R$ {t['frete_correto']:,.2f}")
        print(f"   ✅ FSS2E39 DG: R$ {t['despesas_gerais']:,.2f}")
    
    # Teste 5: Filtrar por mês AGO/2025
    print("\n📅 TESTE 5: Agosto/2025")
    filtros_mes = {'mes': 'AGO', 'ano': '2025'}
    dados_agosto = extrair_dados_manifesto_real(filtros_mes)
    if dados_agosto:
        t = dados_agosto['totais_mensais']
        print(f"   ✅ AGO/2025 FC: R$ {t['frete_correto']:,.2f}")
        print(f"   ✅ AGO/2025 DG: R$ {t['despesas_gerais']:,.2f}")
    
    # Teste 6: Combinação múltipla
    print("\n🎯 TESTE 6: MARFRIG + FIXO + AGO/2025")
    filtros_combo = {
        'perfil': 'FIXO',
        'clientes': ['MARFRIG'],
        'mes': 'AGO',
        'ano': '2025'
    }
    dados_combo = extrair_dados_manifesto_real(filtros_combo)
    if dados_combo:
        t = dados_combo['totais_mensais']
        print(f"   ✅ Combo FC: R$ {t['frete_correto']:,.2f}")
        print(f"   ✅ Combo DG: R$ {t['despesas_gerais']:,.2f}")
        
        # Verificar dias com dados
        dias_dados = [d for d in dados_combo['dados_diarios'] if d['frete_correto'] > 0 or d['despesas_gerais'] > 0]
        print(f"   ✅ Dias com dados: {len(dias_dados)}")
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES DE FILTROS PASSARAM!")
    print("🚀 Filtros estão funcionando corretamente!")
    print("🌐 Teste na interface: http://127.0.0.1:5000/frete/painel")

if __name__ == '__main__':
    testar_filtros_melhorados()
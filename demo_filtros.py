#!/usr/bin/env python3
"""
Demonstração prática dos filtros funcionando
"""

from financeiro.painel_frete import extrair_dados_manifesto_real

def demo_filtros():
    """Demonstra diferentes combinações de filtros"""
    
    print("🎯 DEMONSTRAÇÃO DOS FILTROS FUNCIONANDO")
    print("=" * 50)
    
    # Cenário 1: Todos os dados
    print("\n📊 CENÁRIO 1: Todos os dados (sem filtros)")
    dados_total = extrair_dados_manifesto_real()
    if dados_total:
        t = dados_total['totais_mensais']
        print(f"   Frete Correto Total: R$ {t['frete_correto']:,.2f}")
        print(f"   Despesas Gerais Total: R$ {t['despesas_gerais']:,.2f}")
        print(f"   Diferença: R$ {t['frete_correto'] - t['despesas_gerais']:,.2f}")
    
    # Cenário 2: Apenas cliente MARFRIG
    print("\n🏭 CENÁRIO 2: Apenas cliente MARFRIG")
    filtro_marfrig = {'clientes': ['MARFRIG']}
    dados_marfrig = extrair_dados_manifesto_real(filtro_marfrig)
    if dados_marfrig:
        t = dados_marfrig['totais_mensais']
        print(f"   Frete Correto MARFRIG: R$ {t['frete_correto']:,.2f}")
        print(f"   Despesas Gerais MARFRIG: R$ {t['despesas_gerais']:,.2f}")
        print(f"   % do total FC: {(t['frete_correto']/dados_total['totais_mensais']['frete_correto']*100):.1f}%")
    
    # Cenário 3: Apenas veículos FIXO
    print("\n🚚 CENÁRIO 3: Apenas perfil FIXO")
    filtro_fixo = {'perfil': 'FIXO'}
    dados_fixo = extrair_dados_manifesto_real(filtro_fixo)
    if dados_fixo:
        t = dados_fixo['totais_mensais']
        print(f"   Frete Correto FIXO: R$ {t['frete_correto']:,.2f}")
        print(f"   Despesas Gerais FIXO: R$ {t['despesas_gerais']:,.2f}")
        print(f"   % do total FC: {(t['frete_correto']/dados_total['totais_mensais']['frete_correto']*100):.1f}%")
    
    # Cenário 4: Combinação múltipla
    print("\n🎯 CENÁRIO 4: MARFRIG + FIXO + AGO/2025")
    filtro_combo = {
        'clientes': ['MARFRIG'],
        'perfil': 'FIXO', 
        'mes': 'AGO',
        'ano': '2025'
    }
    dados_combo = extrair_dados_manifesto_real(filtro_combo)
    if dados_combo:
        t = dados_combo['totais_mensais']
        print(f"   Frete Correto (filtrado): R$ {t['frete_correto']:,.2f}")
        print(f"   Despesas Gerais (filtrado): R$ {t['despesas_gerais']:,.2f}")
        
        # Mostrar alguns dias
        dias_dados = [d for d in dados_combo['dados_diarios'] if d['frete_correto'] > 0 or d['despesas_gerais'] > 0]
        print(f"   Dias com movimento: {len(dias_dados)}")
        if dias_dados:
            print("   Primeiros 3 dias:")
            for d in dias_dados[:3]:
                print(f"     Dia {d['dia']}: FC=R${d['frete_correto']:,.2f}, DG=R${d['despesas_gerais']:,.2f}")
    
    print("\n🎉 Demonstração concluída!")
    print("💡 Interface disponível em: http://127.0.0.1:5000/frete/painel")

if __name__ == '__main__':
    demo_filtros()
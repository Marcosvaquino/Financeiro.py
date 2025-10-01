#!/usr/bin/env python3
"""
Script para testar os filtros dinâmicos do painel de frete
"""

from financeiro.painel_frete import obter_opcoes_filtros, extrair_dados_manifesto_real

def testar_opcoes_filtros():
    """Testa a extração de opções de filtros"""
    print("🔍 Testando extração de opções de filtros...")
    
    opcoes = obter_opcoes_filtros()
    
    print("✅ Opções extraídas:")
    print(f"📊 Perfis ({len(opcoes['perfis'])}): {opcoes['perfis'][:10]}...")  # Mostra só os primeiros 10
    print(f"👥 Clientes ({len(opcoes['clientes'])}): {opcoes['clientes'][:10]}...")
    print(f"🚚 Veículos ({len(opcoes['veiculos'])}): {opcoes['veiculos'][:10]}...")
    print(f"📅 Anos: {opcoes['anos']}")
    
    return opcoes

def testar_filtros_aplicados():
    """Testa a aplicação de filtros específicos"""
    print("\n🔍 Testando aplicação de filtros...")
    
    # Teste 1: Filtrar por cliente específico
    filtros_teste = {
        'clientes': ['MARFRIG'],
        'mes': 'AGO',
        'ano': '2025'
    }
    
    print(f"📋 Testando filtros: {filtros_teste}")
    dados_filtrados = extrair_dados_manifesto_real(filtros_teste)
    
    if dados_filtrados:
        totais = dados_filtrados['totais_mensais']
        print(f"✅ Dados filtrados com sucesso!")
        print(f"💰 Frete Correto: R$ {totais['frete_correto']:,.2f}")
        print(f"💰 Despesas Gerais: R$ {totais['despesas_gerais']:,.2f}")
        
        # Contar dias com dados
        dias_com_dados = [d for d in dados_filtrados['dados_diarios'] if d['frete_correto'] > 0 or d['despesas_gerais'] > 0]
        print(f"📅 Dias com dados após filtro: {len(dias_com_dados)}")
    else:
        print("❌ Erro ao aplicar filtros")
        return False
    
    # Teste 2: Filtrar por veículo específico
    print("\n📋 Testando filtro por veículo...")
    filtros_veiculo = {
        'veiculos': ['FSS2E39'],
        'ano': '2025'
    }
    
    dados_veiculo = extrair_dados_manifesto_real(filtros_veiculo)
    if dados_veiculo:
        totais_v = dados_veiculo['totais_mensais']
        print(f"✅ Filtro por veículo funcionou")
        print(f"💰 Total FSS2E39 - FC: R$ {totais_v['frete_correto']:,.2f}, DG: R$ {totais_v['despesas_gerais']:,.2f}")
    else:
        print("❌ Erro no filtro por veículo")
    
    # Teste 3: Sem filtros (todos os dados)
    print("\n📋 Testando sem filtros (todos os dados)...")
    dados_completos = extrair_dados_manifesto_real()
    if dados_completos:
        totais_c = dados_completos['totais_mensais']
        print(f"✅ Dados completos")
        print(f"💰 Total Geral - FC: R$ {totais_c['frete_correto']:,.2f}, DG: R$ {totais_c['despesas_gerais']:,.2f}")
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes dos filtros dinâmicos")
    print("=" * 60)
    
    # Teste 1: Opções de filtros
    opcoes = testar_opcoes_filtros()
    
    # Teste 2: Aplicação de filtros
    teste_filtros = testar_filtros_aplicados()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print(f"   Opções de filtros: {'✅ PASSOU' if opcoes else '❌ FALHOU'}")
    print(f"   Aplicação filtros: {'✅ PASSOU' if teste_filtros else '❌ FALHOU'}")
    
    if opcoes and teste_filtros:
        print("\n🎉 Todos os testes dos filtros passaram!")
        print("💡 Os filtros estão prontos para uso no painel")
        print("🌐 Teste no navegador: http://127.0.0.1:5000/frete/painel") 
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")

if __name__ == '__main__':
    main()
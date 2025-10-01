#!/usr/bin/env python3
"""
Script para testar o novo gráfico Frete Correto vs Despesas Gerais
"""

from financeiro.painel_frete import extrair_dados_manifesto_real, gerar_dados_frete_diario

def testar_extracao_manifesto():
    """Testa a extração de dados do manifesto"""
    print("🔍 Testando extração de dados do manifesto...")
    
    dados = extrair_dados_manifesto_real()
    
    if not dados:
        print("❌ Erro ao extrair dados do manifesto")
        return False
    
    totais = dados['totais_mensais']
    dados_diarios = dados['dados_diarios']
    
    print("✅ Dados extraídos com sucesso!")
    print(f"📊 Total Frete Correto: R$ {totais['frete_correto']:,.2f}")
    print(f"📊 Total Despesas Gerais: R$ {totais['despesas_gerais']:,.2f}")
    print(f"📊 Diferença: R$ {totais['frete_correto'] - totais['despesas_gerais']:,.2f}")
    
    # Mostrar alguns dias como exemplo
    print("\n📅 Exemplos de dados por dia:")
    dias_com_dados = [d for d in dados_diarios if d['frete_correto'] > 0 or d['despesas_gerais'] > 0]
    
    for i, dia_dados in enumerate(dias_com_dados[:5]):
        dia = dia_dados['dia']
        fc = dia_dados['frete_correto']
        dg = dia_dados['despesas_gerais']
        print(f"   Dia {dia:2d}: FC=R$ {fc:10.2f} | DG=R$ {dg:10.2f} | Diff=R$ {fc-dg:10.2f}")
    
    print(f"\n📈 Total de dias com dados: {len(dias_com_dados)}")
    return True

def testar_funcao_principal():
    """Testa a função principal que será usada pela interface"""
    print("\n🔍 Testando função principal gerar_dados_frete_diario()...")
    
    dados = gerar_dados_frete_diario()
    
    if 'dados_diarios' in dados and 'totais_mensais' in dados:
        print("✅ Estrutura de dados correta!")
        
        totais = dados['totais_mensais']
        print(f"📊 Frete Correto Total: R$ {totais['frete_correto']:,.2f}")
        print(f"📊 Despesas Gerais Total: R$ {totais['despesas_gerais']:,.2f}")
        
        # Verificar se temos dados para pelo menos alguns dias
        dados_com_valor = [d for d in dados['dados_diarios'] if d['frete_correto'] > 0 or d['despesas_gerais'] > 0]
        print(f"📅 Dias com dados: {len(dados_com_valor)}")
        
        return True
    else:
        print("❌ Estrutura de dados incorreta")
        print("Estrutura recebida:", list(dados.keys()))
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do gráfico Frete Correto vs Despesas Gerais")
    print("=" * 60)
    
    # Teste 1: Extração de dados
    teste1 = testar_extracao_manifesto()
    
    # Teste 2: Função principal
    teste2 = testar_funcao_principal()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print(f"   Extração de dados: {'✅ PASSOU' if teste1 else '❌ FALHOU'}")
    print(f"   Função principal:  {'✅ PASSOU' if teste2 else '❌ FALHOU'}")
    
    if teste1 and teste2:
        print("\n🎉 Todos os testes passaram! O gráfico está pronto para uso.")
        print("💡 Acesse: http://127.0.0.1:5000/frete/painel")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")

if __name__ == '__main__':
    main()
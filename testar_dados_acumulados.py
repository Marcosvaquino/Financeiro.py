#!/usr/bin/env python3
"""
Teste para verificar se os dados acumulados estão funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from financeiro.painel_frete import extrair_dados_manifesto_real

def testar_dados_acumulados():
    print("🧪 TESTANDO DADOS ACUMULADOS")
    print("=" * 50)
    
    # Testar sem filtros (todos os dados)
    print("📊 Testando dados gerais (sem filtros)...")
    dados = extrair_dados_manifesto_real()
    
    if not dados:
        print("❌ Erro: Não foi possível extrair dados!")
        return
    
    print(f"✅ Dados extraídos com sucesso!")
    print(f"📈 Total de dias: {len(dados['dados_diarios'])}")
    print(f"💰 Total Frete Correto: R$ {dados['totais_mensais']['frete_correto']:,.2f}")
    print(f"💸 Total Despesas Gerais: R$ {dados['totais_mensais']['despesas_gerais']:,.2f}")
    
    # Verificar se os valores são acumulados (crescentes)
    print("\n🔍 VERIFICANDO SE OS DADOS SÃO ACUMULADOS:")
    print("-" * 40)
    
    dados_diarios = dados['dados_diarios']
    
    # Mostrar apenas os primeiros 10 dias para verificar se está acumulando
    print("📅 Primeiros 10 dias (deve ser crescente):")
    for i in range(10):
        dia_data = dados_diarios[i]
        print(f"   Dia {dia_data['dia']:2d}: FC = R$ {dia_data['frete_correto']:>10,.2f} | DG = R$ {dia_data['despesas_gerais']:>10,.2f}")
        
        # Verificar se está crescendo (exceto quando valor é 0)
        if i > 0 and dia_data['frete_correto'] > 0:
            anterior = dados_diarios[i-1]['frete_correto']
            if dia_data['frete_correto'] < anterior:
                print(f"   ⚠️  ATENÇÃO: Dia {dia_data['dia']} tem valor menor que dia {i}!")
    
    # Testar com filtro específico
    print(f"\n🔍 TESTANDO COM FILTRO (Cliente: Friboi):")
    print("-" * 40)
    
    filtros = {
        'clientes': ['FRIBOI'],
        'mes': 'SET',  # Setembro
        'ano': '2025'
    }
    
    dados_filtrados = extrair_dados_manifesto_real(filtros)
    
    if dados_filtrados:
        print(f"✅ Dados filtrados extraídos!")
        print(f"💰 Total FC (Friboi/Set): R$ {dados_filtrados['totais_mensais']['frete_correto']:,.2f}")
        print(f"💸 Total DG (Friboi/Set): R$ {dados_filtrados['totais_mensais']['despesas_gerais']:,.2f}")
        
        # Mostrar alguns dias com filtro
        print("\n📅 Primeiros 5 dias (Friboi - Setembro):")
        for i in range(5):
            dia_data = dados_filtrados['dados_diarios'][i]
            if dia_data['frete_correto'] > 0:  # Só mostrar dias com dados
                print(f"   Dia {dia_data['dia']:2d}: FC = R$ {dia_data['frete_correto']:>8,.2f} | DG = R$ {dia_data['despesas_gerais']:>8,.2f}")
    else:
        print("❌ Erro ao aplicar filtros!")
    
    print(f"\n✅ TESTE CONCLUÍDO")
    print("=" * 50)
    print("📋 RESULTADOS ESPERADOS:")
    print("- Os valores devem crescer dia a dia (acumulado)")
    print("- Dia 1 = valores do dia 1")
    print("- Dia 2 = valores do dia 1 + dia 2")
    print("- Dia 3 = valores do dia 1 + dia 2 + dia 3")
    print("- E assim por diante...")

if __name__ == "__main__":
    testar_dados_acumulados()
#!/usr/bin/env python3
"""
Script de teste para o módulo de Análise de Margem
Verifica se os dados estão sendo carregados corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from financeiro.margem_analise import margem_service

def testar_modulo_margem():
    print("🔍 TESTANDO MÓDULO DE ANÁLISE DE MARGEM")
    print("=" * 50)
    
    try:
        # 1. Testar carregamento de dados
        print("1️⃣ Carregando dados do manifesto...")
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            print("❌ ERRO: Nenhum dado encontrado no manifesto")
            return False
        
        print(f"✅ Dados carregados: {len(df)} registros")
        print(f"   📅 Período: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
        
        # 2. Verificar colunas essenciais
        colunas_essenciais = ['Tipologia', 'DESTINO', 'Placa', 'frete_receber', 'frete_pagar', 'margem_liquida']
        print("\n2️⃣ Verificando colunas essenciais...")
        
        for coluna in colunas_essenciais:
            if coluna in df.columns:
                valores_nao_nulos = df[coluna].notna().sum()
                print(f"   ✅ {coluna}: {valores_nao_nulos} valores válidos")
            else:
                print(f"   ❌ {coluna}: COLUNA AUSENTE")
                return False
        
        # 3. Testar análise por tipologia
        print("\n3️⃣ Testando análise por tipologia...")
        analise_tip = margem_service.analise_por_tipologia(df)
        
        if analise_tip and 'resumo_geral' in analise_tip:
            tipologias = list(analise_tip['resumo_geral'].keys())
            print(f"   ✅ Tipologias encontradas: {tipologias}")
            
            # Mostrar resumo de uma tipologia
            if tipologias:
                primeira_tip = tipologias[0]
                dados_tip = analise_tip['resumo_geral'][primeira_tip]
                print(f"   📊 {primeira_tip}:")
                print(f"      💰 Receita: R$ {dados_tip['receita_total']:,.2f}")
                print(f"      💸 Despesa: R$ {dados_tip['despesa_total']:,.2f}")
                print(f"      📈 Margem: {dados_tip['margem_percentual_media']:.1f}%")
        else:
            print("   ❌ Erro na análise por tipologia")
            return False
        
        # 4. Testar metas sugeridas
        print("\n4️⃣ Testando cálculo de metas...")
        metas = margem_service.calcular_metas_sugeridas(df)
        
        if metas:
            print(f"   ✅ Metas calculadas para {len(metas)} tipologias")
            for tip, meta in list(metas.items())[:3]:  # Mostrar apenas 3
                print(f"      🎯 {tip}: Meta {meta['meta_sugerida']}% (Atual: {meta['performance_atual']}%)")
        else:
            print("   ⚠️ Nenhuma meta calculada")
        
        # 5. Testar análise por destino
        print("\n5️⃣ Testando análise por destino...")
        analise_dest = margem_service.analise_por_destino(df, top_n=10)
        
        if analise_dest and 'top_destinos' in analise_dest:
            destinos = list(analise_dest['top_destinos'].keys())
            print(f"   ✅ Top destinos: {len(destinos)} encontrados")
            print(f"   📍 Exemplos: {destinos[:5]}")
        else:
            print("   ❌ Erro na análise por destino")
        
        # 6. Testar análise por placa
        print("\n6️⃣ Testando análise por placa...")
        analise_placa = margem_service.analise_por_placa(df, top_n=10)
        
        if analise_placa and 'top_placas' in analise_placa:
            placas = list(analise_placa['top_placas'].keys())
            print(f"   ✅ Top placas: {len(placas)} encontradas")
            print(f"   🚚 Exemplos: {placas[:5]}")
        else:
            print("   ❌ Erro na análise por placa")
        
        # 7. Resumo financeiro geral
        print("\n7️⃣ Resumo financeiro geral...")
        receita_total = df['frete_receber'].sum()
        despesa_total = df['frete_pagar'].sum()
        margem_total = df['margem_liquida'].sum()
        margem_percentual = (margem_total / receita_total * 100) if receita_total > 0 else 0
        
        print(f"   💰 Receita Total: R$ {receita_total:,.2f}")
        print(f"   💸 Despesa Total: R$ {despesa_total:,.2f}")
        print(f"   📊 Margem Total: R$ {margem_total:,.2f}")
        print(f"   📈 Margem %: {margem_percentual:.1f}%")
        
        # Status final
        print("\n" + "=" * 50)
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Módulo de Análise de Margem está funcionando corretamente")
        print(f"✅ {len(df)} registros processados")
        print(f"✅ {len(tipologias)} tipologias analisadas")
        print(f"✅ {len(destinos)} destinos processados")
        print("✅ Sistema pronto para uso!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_modulo_margem()
    
    if sucesso:
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Execute o servidor: python run_app.py")
        print("2. Acesse: http://localhost:5000")
        print("3. Vá em: Frete > Análise de Margem")
        print("4. Explore os dados por Tipologia, Destino e Placa!")
    else:
        print("\n🔧 CORREÇÕES NECESSÁRIAS:")
        print("1. Verifique se o banco financeiro.db existe")
        print("2. Confirme se há dados na tabela manifesto_acumulado")
        print("3. Execute o teste novamente")
    
    sys.exit(0 if sucesso else 1)
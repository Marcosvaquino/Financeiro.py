"""
Teste rápido das modificações no gráfico de clientes do painel de frete
"""
import sys
import os
sys.path.append('d:/OneDrive/PROJETOFINANCEIRO.PY')

from financeiro.painel_frete import PainelFreteService
import pandas as pd

def testar_grafico_clientes():
    print("🧪 Testando modificações no gráfico de clientes...")
    
    try:
        # Instanciar o serviço
        service = PainelFreteService()
        
        # Carregar dados
        print("📊 Carregando dados...")
        service.carregar_dados(forcar_recarga=True)
        
        if service.df_manifesto is None or service.df_manifesto.empty:
            print("❌ Nenhum dado encontrado")
            return
            
        print(f"✅ Dados carregados: {len(service.df_manifesto)} registros")
        
        # Filtrar dados (sem filtros específicos)
        df_filtrado = service.filtrar_dados()
        print(f"📋 Dados filtrados: {len(df_filtrado)} registros")
        
        # Testar cálculo do gráfico de clientes
        print("\n🎯 Testando cálculo do gráfico de clientes (menor para maior por receita)...")
        resultado = service.calcular_grafico_clientes(df_filtrado)
        
        print(f"👥 Clientes encontrados: {len(resultado['clientes'])}")
        print("\n📊 Resultado do gráfico:")
        
        for i, cliente in enumerate(resultado['clientes']):
            receita = resultado['receita'][i]
            despesa = resultado['despesa'][i] 
            rentabilidade = resultado['rentabilidade_pct'][i]
            print(f"{i+1:2d}. {cliente:<25} | Receita: R$ {receita:>10,.2f} | Despesa: R$ {despesa:>10,.2f} | Rentabilidade: {rentabilidade:>6.1f}%")
            
        print(f"\n✅ Teste concluído! Verificando ordenação (deve estar do menor para o maior por receita)...")
        receitas = resultado['receita']
        esta_ordenado = all(receitas[i] <= receitas[i+1] for i in range(len(receitas)-1))
        print(f"📈 Ordenação correta (menor para maior): {'✅ SIM' if esta_ordenado else '❌ NÃO'}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_grafico_clientes()
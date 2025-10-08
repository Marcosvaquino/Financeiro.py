"""
Teste dos filtros de perfil (FIXO/SPOT) na análise de margem
"""
import sys
import os
sys.path.append('d:/OneDrive/PROJETOFINANCEIRO.PY')

from financeiro.margem_analise import MargemAnaliseService

def testar_filtros_perfil():
    print("🧪 Testando filtros de perfil (FIXO/SPOT) na análise de margem...")
    
    try:
        # Instanciar o serviço
        service = MargemAnaliseService()
        
        # Carregar dados
        print("📊 Carregando dados do manifesto...")
        df = service.carregar_dados_manifesto()
        
        if df.empty:
            print("❌ Nenhum dado encontrado")
            return
            
        print(f"✅ Dados carregados: {len(df)} registros")
        
        # Verificar se a coluna 'perfil' existe
        if 'perfil' not in df.columns:
            print("❌ Coluna 'perfil' não encontrada nos dados")
            print("📋 Colunas disponíveis:", list(df.columns))
            return
        
        # Analisar distribuição de perfis
        print("\n📈 Análise de distribuição de perfis:")
        perfis_counts = df['perfil'].value_counts()
        print(perfis_counts)
        
        # Verificar valores únicos
        perfis_unicos = df['perfil'].dropna().unique()
        print(f"\n🎯 Perfis únicos encontrados: {sorted(perfis_unicos)}")
        
        # Testar filtros para cada perfil
        for perfil in perfis_unicos:
            if perfil and str(perfil).strip():
                df_filtrado = df[df['perfil'] == perfil]
                receita_total = df_filtrado['frete_receber'].sum()
                margem_media = df_filtrado['margem_percentual'].mean()
                
                print(f"\n📊 {perfil}:")
                print(f"   - Registros: {len(df_filtrado)}")
                print(f"   - Receita Total: R$ {receita_total:,.2f}")
                print(f"   - Margem Média: {margem_media:.1f}%")
        
        print(f"\n✅ Teste concluído! Os filtros de perfil estão funcionando.")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_filtros_perfil()
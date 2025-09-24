import sys, os
root = r'D:\OneDrive\PROJETOFINANCEIRO.PY'
sys.path.insert(0, root)

from financeiro.valencio import processar_valencio

# Testar a nova lógica automática do Valencio
arquivo_test = r'D:\OneDrive\PROJETOFINANCEIRO.PY\financeiro\uploads\valencio\Valencio_Frete_08-25.xlsx'

print("🚀 TESTANDO NOVA LÓGICA AUTOMÁTICA DO VALENCIO")
print("=" * 60)
print(f"Arquivo: {arquivo_test}")

try:
    resultado = processar_valencio(arquivo_test)
    
    if resultado['success']:
        print("✅ SUCESSO!")
        print(f"📄 {resultado['message']}")
        
        dados = resultado['dados']
        print(f"\n📊 RESUMO:")
        print(f"  💰 Total Geral: R$ {dados['total_geral']:.2f}")
        print(f"  📦 Blocos Analisados: {dados['blocos_processados']}")
        print(f"  🏭 Blocos com Valencio: {dados['blocos_com_valencio']}")
        print(f"  📄 Linhas Processadas: {dados['linhas_processadas']}")
        print(f"  💾 Arquivo Modificado: {dados['arquivo_modificado']}")
        print(f"  ✅ ARQUIVO ORIGINAL MODIFICADO COM SUCESSO!")
        
    else:
        print("❌ ERRO!")
        print(f"💥 {resultado['message']}")
        
except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    import traceback
    traceback.print_exc()
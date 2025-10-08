"""
Script para aplicar correção pontual nos cálculos de margem percentual
"""

def corrigir_arquivo_margem():
    arquivo_path = r'd:\OneDrive\PROJETOFINANCEIRO.PY\financeiro\margem_analise.py'
    
    # Ler o arquivo
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Substituição específica para melhorar os filtros
    filtro_antigo = "resultado = resultado[resultado['frete_receber'] > 0]"
    filtro_novo = """resultado = resultado[
                (resultado['frete_receber'] >= 100) &      # Receita mínima R$ 100
                (resultado['Percentual'] >= -100) &        # Margem não menor que -100%
                (resultado['Percentual'] <= 200)           # Margem não maior que 200%
            ]"""
    
    # Aplicar substituição
    conteudo_corrigido = conteudo.replace(filtro_antigo, filtro_novo)
    
    # Verificar se houve mudanças
    if conteudo != conteudo_corrigido:
        # Salvar o arquivo corrigido
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo_corrigido)
        
        mudancas = conteudo_corrigido.count(filtro_novo)
        print(f"✅ Arquivo corrigido! {mudancas} ocorrências substituídas.")
        print("🔧 Filtros melhorados para eliminar casos extremos.")
    else:
        print("ℹ️ Nenhuma mudança necessária.")

if __name__ == "__main__":
    corrigir_arquivo_margem()
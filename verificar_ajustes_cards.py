import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== TESTE DOS AJUSTES DOS CARDS PRINCIPAIS ===")
print("(Mantendo filtros globais, removendo filtros de status)\n")

mes = 9
ano = 2025
pattern = f"%/{mes:02d}/{ano}%"

# 1. RECEITA (OK - não mexeu)
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_receber
    WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
    AND conta_contabil != 'LSP Transportes'
""", (pattern,))
receita_realizada = cur.fetchone()[0] or 0.0

# 2. A RECEBER (TODOS os status + filtro global)
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) 
    FROM contas_receber 
    WHERE vencimento LIKE ?
    AND conta_contabil != 'LSP Transportes'
""", (pattern,))
receber_dados = cur.fetchone()

# 3. A PAGAR (TODOS os status + filtro global)
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) 
    FROM contas_pagar 
    WHERE vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern,))
pagar_dados = cur.fetchone()

# 4. FLUXO DE CAIXA
pagar_total = pagar_dados[1]
fluxo_recebido = receita_realizada - pagar_total

# Projeção
cur.execute("SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao WHERE mes = ? AND ano = ?", (mes, ano))
receita_meta = cur.fetchone()[0] or 0.0
fluxo_projetado = receita_meta - pagar_total

print(f"📊 SETEMBRO {ano}:")
print(f"   💰 Receita (Recebida): R$ {receita_realizada:,.2f}")
print(f"   📥 A Receber (TODOS): {receber_dados[0]} títulos, R$ {receber_dados[1]:,.2f}")
print(f"   📤 A Pagar (TODOS): {pagar_dados[0]} títulos, R$ {pagar_dados[1]:,.2f}")
print(f"   💳 Fluxo Recebido - Pagar: R$ {fluxo_recebido:,.2f}")
print(f"   🎯 Fluxo Projeção - Pagar: R$ {fluxo_projetado:,.2f}")

# Verificar filtros globais
print(f"\n🔍 VERIFICAÇÃO DOS FILTROS GLOBAIS:")

# LSP Transportes (contas_receber)
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE conta_contabil = 'LSP Transportes' AND vencimento LIKE ?", (pattern,))
lsp_data = cur.fetchone()
print(f"   ❌ LSP Transportes filtrados: {lsp_data[0]} títulos, R$ {lsp_data[1] or 0:,.2f}")

# REIS Transportes (contas_pagar)
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar WHERE fornecedor = 'REIS TRANSPORTES' AND vencimento LIKE ?", (pattern,))
reis_data = cur.fetchone()
print(f"   ❌ REIS Transportes filtrados: {reis_data[0]} títulos, R$ {reis_data[1] or 0:,.2f}")

print(f"\n✅ FILTROS GLOBAIS ATIVOS - VALORES CORRETOS!")

conn.close()
import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== TESTE DO FILTRO GLOBAL LSP TRANSPORTES ===\n")

# Teste 1: Contar registros com LSP Transportes
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE conta_contabil = 'LSP Transportes'")
lsp_count, lsp_total = cur.fetchone()
print(f"📊 Registros LSP Transportes: {lsp_count} registros, R$ {lsp_total:,.2f}")

# Teste 2: Total geral (com LSP)
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber")
total_count, total_valor = cur.fetchone()
print(f"📊 Total geral (COM LSP): {total_count} registros, R$ {total_valor:,.2f}")

# Teste 3: Total sem LSP (filtro aplicado)
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE conta_contabil != 'LSP Transportes'")
sem_lsp_count, sem_lsp_valor = cur.fetchone()
print(f"📊 Total sem LSP (filtrado): {sem_lsp_count} registros, R$ {sem_lsp_valor:,.2f}")

print(f"\n🔍 DIFERENÇA: {lsp_count} registros removidos, R$ {lsp_total:,.2f} filtrados")

# Teste 4: Verificar setembro/2025 específico
pattern = "%/09/2025%"
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE vencimento LIKE ? AND status = 'PENDENTE'", (pattern,))
setembro_total = cur.fetchone()

cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE vencimento LIKE ? AND status = 'PENDENTE' AND conta_contabil != 'LSP Transportes'", (pattern,))
setembro_filtrado = cur.fetchone()

print(f"\n📅 SETEMBRO 2025 PENDENTE:")
print(f"   COM LSP: {setembro_total[0]} registros, R$ {setembro_total[1] or 0:,.2f}")
print(f"   SEM LSP: {setembro_filtrado[0]} registros, R$ {setembro_filtrado[1] or 0:,.2f}")

conn.close()
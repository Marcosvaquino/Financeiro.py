import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== TESTE DO FILTRO GLOBAL REIS TRANSPORTES ===\n")

# Teste 1: Contar registros com REIS TRANSPORTES
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar WHERE fornecedor = 'REIS TRANSPORTES'")
reis_count, reis_total = cur.fetchone()
print(f"📊 Registros REIS TRANSPORTES: {reis_count} registros, R$ {reis_total:,.2f}")

# Teste 2: Total geral (com REIS)
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar")
total_count, total_valor = cur.fetchone()
print(f"📊 Total geral (COM REIS): {total_count} registros, R$ {total_valor:,.2f}")

# Teste 3: Total sem REIS (filtro aplicado)
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar WHERE fornecedor != 'REIS TRANSPORTES'")
sem_reis_count, sem_reis_valor = cur.fetchone()
print(f"📊 Total sem REIS (filtrado): {sem_reis_count} registros, R$ {sem_reis_valor:,.2f}")

print(f"\n🔍 DIFERENÇA: {reis_count} registros removidos, R$ {reis_total:,.2f} filtrados")

# Teste 4: Verificar setembro/2025 específico
pattern = "%/09/2025%"
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar WHERE vencimento LIKE ? AND status != 'Pago'", (pattern,))
setembro_total = cur.fetchone()

cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar WHERE vencimento LIKE ? AND status != 'Pago' AND fornecedor != 'REIS TRANSPORTES'", (pattern,))
setembro_filtrado = cur.fetchone()

print(f"\n📅 SETEMBRO 2025 (Status != Pago):")
print(f"   COM REIS: {setembro_total[0]} registros, R$ {setembro_total[1] or 0:,.2f}")
print(f"   SEM REIS: {setembro_filtrado[0]} registros, R$ {setembro_filtrado[1] or 0:,.2f}")
print(f"   FILTRADO: {setembro_total[0] - setembro_filtrado[0]} registros, R$ {(setembro_total[1] or 0) - (setembro_filtrado[1] or 0):,.2f}")

# Teste 5: Verificar especificamente registros REIS em setembro
print(f"\n🔍 REGISTROS REIS TRANSPORTES EM 09/2025:")
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0), status
    FROM contas_pagar
    WHERE fornecedor = 'REIS TRANSPORTES' AND vencimento LIKE ?
    GROUP BY status
""", (pattern,))
reis_setembro = cur.fetchall()

if reis_setembro:
    for status_data in reis_setembro:
        print(f"   Status {status_data[2]}: {status_data[0]} títulos, R$ {status_data[1]:,.2f}")
else:
    print("   ✅ Nenhum registro REIS encontrado em setembro/2025")

print(f"\n🎯 RESUMO DOS FILTROS GLOBAIS:")
print(f"   💰 LSP Transportes filtrado: R$ 6,609,900.02 (contas_receber)")
print(f"   💰 REIS Transportes filtrado: R$ {reis_total:,.2f} (contas_pagar)")
print(f"   💰 TOTAL FILTRADO: R$ {6609900.02 + reis_total:,.2f}")

conn.close()
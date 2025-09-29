import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== TESTE APÓS CORREÇÃO DO FLUXO DE CAIXA ===\n")

mes = 9
ano = 2025
pattern = f"%/{mes:02d}/{ano}%"

# 1. Receita Meta (Projeção)
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0)
    FROM projecao 
    WHERE mes = ? AND ano = ?
""", (mes, ano))
receita_meta = cur.fetchone()[0] or 0.0

# 2. Receita Realizada (Recebido)
cur.execute(f"""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_receber
    WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
    AND conta_contabil != 'LSP Transportes'
""", (pattern,))
receita_realizada = cur.fetchone()[0] or 0.0

# 3. Contas a Pagar PENDENTES (correto para fluxo de caixa)
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_pagar
    WHERE UPPER(status) = 'PENDENTE'
    AND vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern,))
pagar_pendente = cur.fetchone()[0] or 0.0

# 4. Contas a Pagar TOTAL (!= PAGO) - para comparação
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_pagar
    WHERE status != 'PAGO' AND status != 'Pago'
    AND vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern,))
pagar_total = cur.fetchone()[0] or 0.0

print(f"📅 SETEMBRO 2025 - VALORES CORRETOS:")
print(f"   💰 Receita Meta (Projeção): R$ {receita_meta:,.2f}")
print(f"   💰 Receita Realizada: R$ {receita_realizada:,.2f}")
print(f"   💸 A Pagar PENDENTE: R$ {pagar_pendente:,.2f}")
print(f"   💸 A Pagar TOTAL (!= Pago): R$ {pagar_total:,.2f}")

fluxo_realizado = receita_realizada - pagar_pendente
fluxo_projetado = receita_meta - pagar_pendente

print(f"\n🎯 FLUXO DE CAIXA CORRETO:")
print(f"   Recebido - Pagar: R$ {fluxo_realizado:,.2f}")
print(f"   Projeção - Pagar: R$ {fluxo_projetado:,.2f}")

print(f"\n🔍 COMPARAÇÃO COM VALORES ANTERIORES:")
print(f"   Fluxo ERRADO (usava total pagar): R$ {receita_realizada - pagar_total:,.2f}")
print(f"   Fluxo CORRETO (usa só pendente): R$ {fluxo_realizado:,.2f}")

conn.close()
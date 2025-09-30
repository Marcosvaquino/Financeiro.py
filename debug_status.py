import sqlite3

conn = sqlite3.connect('financeiro.db')
conn.row_factory = sqlite3.Row

print("=== Status únicos em contas_receber ===")
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT status, COUNT(*) as qtd FROM contas_receber GROUP BY status")
status_receitas = cursor.fetchall()
for row in status_receitas:
    print(f"  {row['status']}: {row['qtd']} registros")

print("\n=== Status únicos em contas_pagar ===")
cursor.execute("SELECT DISTINCT status, COUNT(*) as qtd FROM contas_pagar GROUP BY status")
status_despesas = cursor.fetchall()
for row in status_despesas:
    print(f"  {row['status']}: {row['qtd']} registros")

print("\n=== Amostra de receitas (primeiros 5) ===")
cursor.execute("SELECT cliente, valor_principal, status, data_liquidacao FROM contas_receber LIMIT 5")
receitas_sample = cursor.fetchall()
for row in receitas_sample:
    print(f"  Cliente: {row['cliente']}, Valor: {row['valor_principal']}, Status: {row['status']}, Data: {row['data_liquidacao']}")

print("\n=== Amostra de despesas (primeiros 5) ===")
cursor.execute("SELECT fornecedor, valor_principal, status, data_liquidacao FROM contas_pagar LIMIT 5")
despesas_sample = cursor.fetchall()
for row in despesas_sample:
    print(f"  Fornecedor: {row['fornecedor']}, Valor: {row['valor_principal']}, Status: {row['status']}, Data: {row['data_liquidacao']}")

conn.close()
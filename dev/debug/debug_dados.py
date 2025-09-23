import sqlite3

conn = sqlite3.connect('financeiro/financeiro.db')
cur = conn.cursor()

print("=== INVESTIGAÇÃO DOS DADOS ===\n")

# 1. Verificar projeção por mês/ano
print("1. DADOS DE PROJEÇÃO POR MÊS/ANO:")
cur.execute('SELECT mes, ano, COUNT(*), SUM(valor) FROM projecao GROUP BY mes, ano ORDER BY ano, mes')
rows = cur.fetchall()
for row in rows:
    print(f"   Mês: {row[0]}, Ano: {row[1]}, Quantidade: {row[2]}, Total: R$ {row[3]:,.2f}")

# 2. Verificar se há dados de projeção para agosto especificamente
print(f"\n2. PROJEÇÃO AGOSTO/2025:")
cur.execute('SELECT COUNT(*), SUM(valor) FROM projecao WHERE mes = 8 AND ano = 2025')
result = cur.fetchone()
print(f"   Quantidade: {result[0]}, Total: R$ {result[1] or 0:,.2f}")

# 3. Verificar contas a receber para agosto
print(f"\n3. CONTAS A RECEBER AGOSTO/2025:")
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE strftime('%m', vencimento) = '08' AND strftime('%Y', vencimento) = '2025'")
result = cur.fetchone()
print(f"   Quantidade: {result[0]}, Total: R$ {result[1] or 0:,.2f}")

# 4. Verificar status únicos
print(f"\n4. STATUS ÚNICOS EM CONTAS_RECEBER:")
cur.execute('SELECT DISTINCT status, COUNT(*) FROM contas_receber GROUP BY status')
status_list = cur.fetchall()
for status in status_list:
    print(f"   '{status[0]}': {status[1]} registros")

# 5. Verificar recebidos para agosto
print(f"\n5. JÁ RECEBIDOS EM AGOSTO/2025:")
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE status = 'Recebido' AND strftime('%m', vencimento) = '08' AND strftime('%Y', vencimento) = '2025'")
result = cur.fetchone()
print(f"   Quantidade: {result[0]}, Total: R$ {result[1] or 0:,.2f}")

# 6. Amostra dos dados de agosto
print(f"\n6. AMOSTRA DE CONTAS DE AGOSTO (5 primeiros):")
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber WHERE strftime('%m', vencimento) = '08' AND strftime('%Y', vencimento) = '2025' LIMIT 5")
sample = cur.fetchall()
for row in sample:
    print(f"   Cliente: {row[0]}, Valor: R$ {row[1]:,.2f}, Vencimento: {row[2]}, Status: '{row[3]}'")

conn.close()
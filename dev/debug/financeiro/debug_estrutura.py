import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Verificando estrutura exata dos dados ===")

# Ver todos os registros únicos de status
cur.execute("SELECT DISTINCT status FROM contas_receber")
status_list = [row[0] for row in cur.fetchall()]
print(f"Status encontrados: {status_list}")

# Ver alguns registros que contenham MINERVA
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber WHERE UPPER(cliente) LIKE '%MINERVA%' LIMIT 5")
print(f"\nPrimeiros registros com MINERVA:")
for row in cur.fetchall():
    print(f"  Cliente: '{row[0]}', Valor: '{row[1]}', Vencimento: '{row[2]}', Status: '{row[3]}'")

# Ver registros de agosto (qualquer ano)
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber WHERE vencimento LIKE '%/08/%' LIMIT 10")
print(f"\nRegistros de agosto (qualquer ano):")
for row in cur.fetchall():
    print(f"  Cliente: '{row[0]}', Valor: '{row[1]}', Vencimento: '{row[2]}', Status: '{row[3]}'")

# Ver registros de 2025
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber WHERE vencimento LIKE '%/2025' LIMIT 10")
print(f"\nRegistros de 2025:")
for row in cur.fetchall():
    print(f"  Cliente: '{row[0]}', Valor: '{row[1]}', Vencimento: '{row[2]}', Status: '{row[3]}'")

# Contar total de registros
cur.execute("SELECT COUNT(*) FROM contas_receber")
total = cur.fetchone()[0]
print(f"\nTotal de registros na tabela: {total}")

# Ver registros recentes (últimos 10)
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber ORDER BY rowid DESC LIMIT 10")
print(f"\nÚltimos 10 registros importados:")
for row in cur.fetchall():
    print(f"  Cliente: '{row[0]}', Valor: '{row[1]}', Vencimento: '{row[2]}', Status: '{row[3]}'")

conn.close()
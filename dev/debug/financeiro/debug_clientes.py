import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Verificando clientes únicos na projeção ===")
cur.execute('SELECT DISTINCT cliente FROM projecao ORDER BY cliente')
clientes_projecao = [row[0] for row in cur.fetchall()]
print(f"Total de clientes únicos na projeção: {len(clientes_projecao)}")
for cliente in clientes_projecao:
    print(f"  - {cliente}")

print("\n=== Verificando clientes únicos em contas_receber ===")
cur.execute('SELECT DISTINCT cliente FROM contas_receber ORDER BY cliente')
clientes_receber = [row[0] for row in cur.fetchall()]
print(f"Total de clientes únicos em contas_receber: {len(clientes_receber)}")
for cliente in clientes_receber:
    print(f"  - {cliente}")

print("\n=== Verificando contas_receber com status 'Recebido' ===")
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber WHERE status = 'Recebido' ORDER BY vencimento")
recebidos = cur.fetchall()
print(f"Total de registros recebidos: {len(recebidos)}")
for row in recebidos:
    print(f"  Cliente: {row[0]}, Valor: {row[1]}, Vencimento: {row[2]}, Status: {row[3]}")

print("\n=== Verificando todos os status em contas_receber ===")
cur.execute("SELECT DISTINCT status FROM contas_receber")
status_list = [row[0] for row in cur.fetchall()]
print(f"Status encontrados: {status_list}")

conn.close()
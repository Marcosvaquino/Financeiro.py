import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Verificando dados na tabela ===")
cur.execute('SELECT COUNT(*) FROM contas_receber')
print(f'Total registros em contas_receber: {cur.fetchone()[0]}')

cur.execute('SELECT * FROM contas_receber LIMIT 5')
registros = cur.fetchall()
if registros:
    print("\nPrimeiros registros:")
    for i, r in enumerate(registros):
        print(f"  {i+1}: ID={r[0]}, Cliente={r[4]}, Vencimento={r[9]}, Valor={r[12]}, Status={r[22]}")
else:
    print("Nenhum registro encontrado!")

conn.close()
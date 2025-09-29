import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

# Verificar registros com LSP na conta_contabil
cur.execute("SELECT conta_contabil, cliente, valor_principal FROM contas_receber WHERE conta_contabil LIKE '%LSP%' LIMIT 10")
results = cur.fetchall()
print('Registros com LSP na conta_contabil:')
for row in results:
    print(f'  Conta: {row[0]} | Cliente: {row[1]} | Valor: R$ {row[2]:,.2f}')

# Verificar valores únicos de conta_contabil
cur.execute("SELECT DISTINCT conta_contabil FROM contas_receber WHERE conta_contabil IS NOT NULL ORDER BY conta_contabil")
contas = cur.fetchall()
print(f'\nTodas as contas contábeis ({len(contas)}):')
for conta in contas:
    if conta[0] and 'LSP' in conta[0].upper():
        print(f'  *** {conta[0]} ***')
    else:
        print(f'  {conta[0]}')

conn.close()
import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

# Verificar estrutura da tabela contas_pagar
cur.execute('PRAGMA table_info(contas_pagar)')
columns = cur.fetchall()
print('Colunas da tabela contas_pagar:')
for col in columns:
    print(f'  {col[1]} - {col[2]}')

print('\n' + '='*50)

# Verificar registros com REIS TRANSPORTES
cur.execute("SELECT fornecedor, valor_principal, status FROM contas_pagar WHERE fornecedor LIKE '%REIS%' LIMIT 10")
results = cur.fetchall()
print('Registros com REIS no fornecedor:')
for row in results:
    print(f'  Fornecedor: {row[0]} | Valor: R$ {row[1]:,.2f} | Status: {row[2]}')

print('\n' + '='*50)

# Verificar valores únicos de fornecedor
cur.execute("SELECT DISTINCT fornecedor FROM contas_pagar WHERE fornecedor IS NOT NULL ORDER BY fornecedor")
fornecedores = cur.fetchall()
print(f'Todos os fornecedores ({len(fornecedores)}):')
for fornecedor in fornecedores:
    if fornecedor[0] and 'REIS' in fornecedor[0].upper():
        print(f'  *** {fornecedor[0]} ***')
    else:
        print(f'  {fornecedor[0]}')

# Estatísticas do REIS TRANSPORTES
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_pagar WHERE fornecedor = 'REIS TRANSPORTES'")
reis_stats = cur.fetchone()
print(f'\nEstatísticas REIS TRANSPORTES: {reis_stats[0]} registros, R$ {reis_stats[1] or 0:,.2f}')

conn.close()
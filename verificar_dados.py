import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print('🔍 VERIFICAÇÃO DETALHADA DA TABELA:')
print('=' * 50)

# Verificar estrutura da tabela
cur.execute('PRAGMA table_info(contas_receber)')
colunas = cur.fetchall()
print('Colunas da tabela contas_receber:')
for col in colunas:
    print(f'  - {col[1]} ({col[2]})')

# Verificar se há dados
cur.execute('SELECT COUNT(*) FROM contas_receber')
total = cur.fetchone()[0]
print(f'\nTotal de registros: {total:,}')

if total > 0:
    # Mostrar primeira linha como exemplo
    cur.execute('SELECT * FROM contas_receber LIMIT 1')
    primeira_linha = cur.fetchone()
    print(f'\nPrimeira linha (exemplo):')
    if primeira_linha:
        for i, valor in enumerate(primeira_linha):
            col_name = colunas[i][1] if i < len(colunas) else f'col_{i}'
            print(f'  {col_name}: {repr(valor)}')
    
    # Verificar especificamente a coluna cliente
    cur.execute('SELECT cliente FROM contas_receber WHERE cliente IS NOT NULL AND cliente != "" LIMIT 5')
    clientes_sample = cur.fetchall()
    print(f'\nAmostras da coluna cliente:')
    for i, (cliente,) in enumerate(clientes_sample, 1):
        print(f'  {i}. "{cliente}"')

    # Verificar clientes únicos
    cur.execute('SELECT DISTINCT cliente FROM contas_receber ORDER BY cliente LIMIT 10')
    clientes_unicos = cur.fetchall()
    print(f'\nPrimeiros 10 clientes únicos:')
    for i, (cliente,) in enumerate(clientes_unicos, 1):
        print(f'  {i}. "{cliente}"')

conn.close()
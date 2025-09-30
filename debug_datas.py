import sqlite3

conn = sqlite3.connect('financeiro.db')
conn.row_factory = sqlite3.Row

print("=== Anos/Meses com receitas ===")
cursor = conn.cursor()
cursor.execute("""
    SELECT strftime('%Y', data_liquidacao) as ano, 
           strftime('%m', data_liquidacao) as mes,
           COUNT(*) as qtd,
           SUM(valor_principal) as total
    FROM contas_receber 
    WHERE status = 'Recebido' AND data_liquidacao IS NOT NULL
    GROUP BY ano, mes 
    ORDER BY ano DESC, mes DESC
    LIMIT 12
""")
receitas_por_mes = cursor.fetchall()
print("Receitas por mês/ano:")
for row in receitas_por_mes:
    print(f"  {row['mes']}/{row['ano']}: {row['qtd']} registros, R$ {row['total']:,.2f}")

print("\n=== Anos/Meses com despesas ===")
cursor.execute("""
    SELECT strftime('%Y', data_liquidacao) as ano, 
           strftime('%m', data_liquidacao) as mes,
           COUNT(*) as qtd,
           SUM(valor_principal) as total
    FROM contas_pagar 
    WHERE status = 'Recebido' AND data_liquidacao IS NOT NULL
    GROUP BY ano, mes 
    ORDER BY ano DESC, mes DESC
    LIMIT 12
""")
despesas_por_mes = cursor.fetchall()
print("Despesas por mês/ano:")
for row in despesas_por_mes:
    print(f"  {row['mes']}/{row['ano']}: {row['qtd']} registros, R$ {row['total']:,.2f}")

conn.close()
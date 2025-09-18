import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Projeções para 08/2025 ===")
cur.execute('SELECT cliente, mes, ano, valor FROM projecao WHERE mes = 8 AND ano = 2025')
for row in cur.fetchall():
    print(f'Cliente: {row[0]}, Mes: {row[1]}, Ano: {row[2]}, Valor: {row[3]}')

print("\n=== Contas a Receber 08/2025 ===")
cur.execute("SELECT cliente, valor_principal, vencimento, status FROM contas_receber WHERE strftime('%m', vencimento) = '08' AND strftime('%Y', vencimento) = '2025'")
for row in cur.fetchall():
    print(f'Cliente: {row[0]}, Valor: {row[1]}, Vencimento: {row[2]}, Status: {row[3]}')

print("\n=== Teste da nova consulta ===")
cur.execute("""
    SELECT cr.cliente, cr.valor_principal, cr.vencimento, cr.status, p.valor as projecao_valor
    FROM contas_receber cr
    INNER JOIN projecao p ON cr.cliente = p.cliente
    WHERE cr.status = 'Recebido' 
    AND strftime('%m', cr.vencimento) = '08'
    AND strftime('%Y', cr.vencimento) = '2025'
    AND p.mes = 8 AND p.ano = 2025
""")
print("Recebidos que estão na projeção:")
for row in cur.fetchall():
    print(f'Cliente: {row[0]}, Valor Recebido: {row[1]}, Vencimento: {row[2]}, Status: {row[3]}, Valor Projeção: {row[4]}')

conn.close()
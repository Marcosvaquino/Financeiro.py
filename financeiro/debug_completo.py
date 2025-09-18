import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Status disponíveis ===")
cur.execute("SELECT DISTINCT status, COUNT(*) FROM contas_receber GROUP BY status")
status_dados = cur.fetchall()
for status, count in status_dados:
    print(f"  {status}: {count} registros")

print("\n=== Meses com dados (qualquer status) ===")
cur.execute("""
    SELECT 
        SUBSTR(vencimento, 4, 2) as mes,
        SUBSTR(vencimento, -4) as ano,
        status,
        COUNT(*) as total
    FROM contas_receber 
    WHERE vencimento LIKE '%/%/%'
    GROUP BY mes, ano, status
    ORDER BY ano, mes, status
    LIMIT 20
""")

meses_dados = cur.fetchall()
for mes, ano, status, count in meses_dados:
    print(f"  {mes}/{ano} - {status}: {count} registros")

print("\n=== Verificando especificamente agosto ===")
cur.execute("""
    SELECT 
        vencimento,
        cliente,
        valor_principal,
        status
    FROM contas_receber 
    WHERE vencimento LIKE '%/08/%'
    ORDER BY vencimento
    LIMIT 10
""")

agosto_dados = cur.fetchall()
print(f"Total registros em agosto (qualquer ano/status): {len(agosto_dados)}")
for row in agosto_dados:
    print(f"  {row[0]} - {row[1]} - R$ {float(row[2]):.2f} - {row[3]}")

# Vamos também verificar dados de clientes da projeção em qualquer mês com status Recebido
print("\n=== Clientes da projeção com status Recebido ===")
clientes_teste = ['MINERVA S A', 'ADORO S.A.', 'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI']

for cliente in clientes_teste:
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(valor_principal), 0)
        FROM contas_receber 
        WHERE TRIM(UPPER(cliente)) = TRIM(UPPER(?))
        AND status = 'Recebido'
    """, (cliente,))
    resultado = cur.fetchone()
    if resultado[0] > 0:
        print(f"  {cliente}: {resultado[0]} registros, R$ {float(resultado[1]):.2f}")

conn.close()
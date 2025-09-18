import sqlite3

# Conecta ao banco
conn = sqlite3.connect('financeiro/financeiro.db')
cur = conn.cursor()

print("=== VERIFICAÇÃO DO BANCO DE DADOS ===\n")

# 1. Verifica se há dados de MINERVA S A
print("1. Busca TODOS os registros de MINERVA S A:")
cur.execute("SELECT COUNT(*) FROM contas_receber WHERE UPPER(cliente) LIKE '%MINERVA S A%'")
total_minerva = cur.fetchone()[0]
print(f"   Total de registros MINERVA S A: {total_minerva}")

# 2. Verifica dados de agosto
print("\n2. Busca registros em agosto de 2025:")
cur.execute("SELECT COUNT(*) FROM contas_receber WHERE vencimento LIKE '%/08/2025%'")
total_agosto = cur.fetchone()[0]
print(f"   Total de registros em agosto/2025: {total_agosto}")

# 3. Busca MINERVA S A em agosto
print("\n3. Busca MINERVA S A em agosto 2025:")
cur.execute("""
    SELECT COUNT(*) 
    FROM contas_receber 
    WHERE UPPER(cliente) LIKE '%MINERVA S A%' 
    AND vencimento LIKE '%/08/2025%'
""")
minerva_agosto = cur.fetchone()[0]
print(f"   MINERVA S A em agosto/2025: {minerva_agosto}")

# 4. Busca MINERVA S A em agosto com status Recebido
print("\n4. Busca MINERVA S A em agosto 2025 - STATUS RECEBIDO:")
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(valor_principal), 0)
    FROM contas_receber 
    WHERE UPPER(cliente) LIKE '%MINERVA S A%' 
    AND vencimento LIKE '%/08/2025%'
    AND status = 'Recebido'
""")
resultado = cur.fetchone()
print(f"   Registros: {resultado[0]}")
print(f"   Valor total: R$ {resultado[1]:,.2f}")

# 5. Verifica diferentes variações do status
print("\n5. Verifica status disponíveis para MINERVA S A em agosto:")
cur.execute("""
    SELECT status, COUNT(*), COALESCE(SUM(valor_principal), 0)
    FROM contas_receber 
    WHERE UPPER(cliente) LIKE '%MINERVA S A%' 
    AND vencimento LIKE '%/08/2025%'
    GROUP BY status
""")
status_dados = cur.fetchall()
for status, count, valor in status_dados:
    print(f"   {status}: {count} registros, R$ {valor:,.2f}")

# 6. Verifica formatos de vencimento
print("\n6. Exemplos de formatos de vencimento para MINERVA S A:")
cur.execute("""
    SELECT vencimento, status, valor_principal
    FROM contas_receber 
    WHERE UPPER(cliente) LIKE '%MINERVA S A%' 
    LIMIT 10
""")
exemplos = cur.fetchall()
for venc, status, valor in exemplos:
    print(f"   {venc} - {status} - {valor}")

# 7. Verifica nomes exatos de clientes
print("\n7. Verifica variações do nome MINERVA:")
cur.execute("""
    SELECT DISTINCT cliente
    FROM contas_receber 
    WHERE UPPER(cliente) LIKE '%MINERVA%'
""")
nomes_minerva = cur.fetchall()
for nome in nomes_minerva:
    print(f"   '{nome[0]}'")

conn.close()
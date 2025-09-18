import sqlite3

# Conecta ao banco
conn = sqlite3.connect('financeiro/financeiro.db')
cur = conn.cursor()

print("=== VERIFICAÇÃO DETALHADA DO BANCO ===\n")

# 1. Total de registros
cur.execute("SELECT COUNT(*) FROM contas_receber")
total = cur.fetchone()[0]
print(f"1. Total de registros: {total}")

# 2. Primeiros registros
print("\n2. Primeiros 5 registros:")
cur.execute("SELECT cliente, vencimento, valor_principal, status FROM contas_receber LIMIT 5")
registros = cur.fetchall()
for cliente, venc, valor, status in registros:
    print(f"   {cliente[:30]:30} | {venc} | {valor} | {status}")

# 3. Busca registros que contenham "MINERVA"
print("\n3. Busca por 'MINERVA' (case insensitive):")
cur.execute("SELECT COUNT(*) FROM contas_receber WHERE UPPER(cliente) LIKE '%MINERVA%'")
minerva_count = cur.fetchone()[0]
print(f"   Registros com MINERVA: {minerva_count}")

if minerva_count > 0:
    cur.execute("SELECT DISTINCT cliente FROM contas_receber WHERE UPPER(cliente) LIKE '%MINERVA%'")
    nomes_minerva = cur.fetchall()
    print("   Variações do nome:")
    for nome in nomes_minerva:
        print(f"     '{nome[0]}'")

# 4. Busca registros de agosto
print("\n4. Busca por agosto:")
cur.execute("SELECT COUNT(*) FROM contas_receber WHERE vencimento LIKE '%/08/%'")
agosto_count = cur.fetchone()[0]
print(f"   Registros em agosto: {agosto_count}")

# 5. Formatos de vencimento
print("\n5. Formatos de vencimento (exemplos):")
cur.execute("SELECT DISTINCT vencimento FROM contas_receber ORDER BY vencimento LIMIT 10")
vencimentos = cur.fetchall()
for venc in vencimentos:
    print(f"   '{venc[0]}'")

# 6. Status disponíveis
print("\n6. Status disponíveis:")
cur.execute("SELECT DISTINCT status, COUNT(*) FROM contas_receber GROUP BY status")
status_list = cur.fetchall()
for status, count in status_list:
    print(f"   '{status}': {count} registros")

conn.close()
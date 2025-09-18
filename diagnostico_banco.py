import sqlite3

# Conecta ao banco
conn = sqlite3.connect('financeiro/financeiro.db')
cur = conn.cursor()

print("=== DIAGNÓSTICO COMPLETO DO BANCO ===\n")

# 1. Verifica se a tabela existe
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contas_receber'")
tabela_existe = cur.fetchone()
print(f"1. Tabela 'contas_receber' existe: {'Sim' if tabela_existe else 'Não'}")

if tabela_existe:
    # 2. Verifica total de registros
    cur.execute("SELECT COUNT(*) FROM contas_receber")
    total_registros = cur.fetchone()[0]
    print(f"2. Total de registros na tabela: {total_registros}")
    
    if total_registros > 0:
        # 3. Verifica últimos registros inseridos
        print("\n3. Últimos 5 registros da tabela:")
        cur.execute("SELECT cliente, vencimento, valor_principal, status FROM contas_receber ORDER BY rowid DESC LIMIT 5")
        ultimos = cur.fetchall()
        for cliente, venc, valor, status in ultimos:
            print(f"   {cliente[:30]:30} | {venc} | {valor} | {status}")
        
        # 4. Verifica anos disponíveis
        print("\n4. Anos disponíveis no banco:")
        cur.execute("""
            SELECT SUBSTR(vencimento, -4) as ano, COUNT(*) 
            FROM contas_receber 
            WHERE vencimento LIKE '%/%/%'
            GROUP BY ano 
            ORDER BY ano
        """)
        anos = cur.fetchall()
        for ano, count in anos:
            print(f"   {ano}: {count} registros")
            
        # 5. Verifica meses de 2025
        print("\n5. Meses de 2025 disponíveis:")
        cur.execute("""
            SELECT SUBSTR(vencimento, 4, 2) as mes, COUNT(*) 
            FROM contas_receber 
            WHERE vencimento LIKE '%/2025'
            GROUP BY mes 
            ORDER BY mes
        """)
        meses_2025 = cur.fetchall()
        for mes, count in meses_2025:
            print(f"   Mês {mes}: {count} registros")
    else:
        print("   A tabela está vazia!")

# 6. Verifica estrutura da tabela
print("\n6. Estrutura da tabela contas_receber:")
cur.execute("PRAGMA table_info(contas_receber)")
colunas = cur.fetchall()
for coluna in colunas:
    print(f"   {coluna[1]} ({coluna[2]})")

conn.close()
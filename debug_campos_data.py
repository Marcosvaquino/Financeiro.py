import sqlite3

conn = sqlite3.connect('financeiro.db')
conn.row_factory = sqlite3.Row

print("=== Campos de data em contas_receber ===")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(contas_receber)")
colunas_receitas = cursor.fetchall()
for col in colunas_receitas:
    if 'data' in col[1].lower() or 'vencimento' in col[1].lower() or 'emissao' in col[1].lower():
        print(f"  {col[1]} ({col[2]})")

print("\n=== Amostra de datas em receitas ===")
cursor.execute("""
    SELECT emissao, vencimento, data_baixa, data_liquidacao, competencia
    FROM contas_receber 
    WHERE status = 'Recebido'
    LIMIT 5
""")
datas_receitas = cursor.fetchall()
for row in datas_receitas:
    print(f"  Emissão: {row['emissao']}, Vencimento: {row['vencimento']}, Baixa: {row['data_baixa']}, Liquidação: {row['data_liquidacao']}, Competência: {row['competencia']}")

print("\n=== Distribuição por competência (receitas) ===")
cursor.execute("""
    SELECT competencia, COUNT(*) as qtd, SUM(valor_principal) as total
    FROM contas_receber 
    WHERE status = 'Recebido' AND competencia IS NOT NULL
    GROUP BY competencia 
    ORDER BY competencia DESC
    LIMIT 10
""")
competencia_receitas = cursor.fetchall()
for row in competencia_receitas:
    print(f"  {row['competencia']}: {row['qtd']} registros, R$ {row['total']:,.2f}")

conn.close()
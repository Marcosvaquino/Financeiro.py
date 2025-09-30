import sqlite3
from datetime import datetime

conn = sqlite3.connect('financeiro.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== Verificando dados de Receitas (contas_receber) ===")
cursor.execute("""
    SELECT COUNT(*) as total, 
           MIN(data_liquidacao) as primeira_data,
           MAX(data_liquidacao) as ultima_data
    FROM contas_receber 
    WHERE status = 'RECEBIDO' AND data_liquidacao IS NOT NULL
""")
receitas_info = cursor.fetchone()
print(f"Total receitas: {receitas_info['total']}")
print(f"Primeira data: {receitas_info['primeira_data']}")
print(f"Última data: {receitas_info['ultima_data']}")

print("\n=== Verificando dados de Despesas (contas_pagar) ===")
cursor.execute("""
    SELECT COUNT(*) as total,
           MIN(data_liquidacao) as primeira_data,
           MAX(data_liquidacao) as ultima_data
    FROM contas_pagar 
    WHERE status = 'PAGO' AND data_liquidacao IS NOT NULL
""")
despesas_info = cursor.fetchone()
print(f"Total despesas: {despesas_info['total']}")
print(f"Primeira data: {despesas_info['primeira_data']}")
print(f"Última data: {despesas_info['ultima_data']}")

print("\n=== Verificando dados específicos para Setembro/2025 ===")
cursor.execute("""
    SELECT COUNT(*) as total, SUM(valor_principal) as valor_total
    FROM contas_receber 
    WHERE strftime('%Y', data_liquidacao) = '2025' 
      AND strftime('%m', data_liquidacao) = '09'
      AND status = 'RECEBIDO'
""")
receitas_set = cursor.fetchone()
print(f"Receitas Set/2025: {receitas_set['total']} registros, Total: R$ {receitas_set['valor_total'] or 0}")

cursor.execute("""
    SELECT COUNT(*) as total, SUM(valor_principal) as valor_total
    FROM contas_pagar 
    WHERE strftime('%Y', data_liquidacao) = '2025' 
      AND strftime('%m', data_liquidacao) = '09'
      AND status = 'PAGO'
""")
despesas_set = cursor.fetchone()
print(f"Despesas Set/2025: {despesas_set['total']} registros, Total: R$ {despesas_set['valor_total'] or 0}")

print("\n=== Verificando clientes únicos em receitas ===")
cursor.execute("""
    SELECT DISTINCT cliente 
    FROM contas_receber 
    WHERE status = 'RECEBIDO' AND data_liquidacao IS NOT NULL
    LIMIT 10
""")
clientes_receitas = cursor.fetchall()
print("Primeiros 10 clientes em receitas:")
for cliente in clientes_receitas:
    print(f"  - {cliente['cliente']}")

print("\n=== Verificando fornecedores únicos em despesas ===")
cursor.execute("""
    SELECT DISTINCT fornecedor 
    FROM contas_pagar 
    WHERE status = 'PAGO' AND data_liquidacao IS NOT NULL
    LIMIT 10
""")
fornecedores_despesas = cursor.fetchall()
print("Primeiros 10 fornecedores em despesas:")
for fornecedor in fornecedores_despesas:
    print(f"  - {fornecedor['fornecedor']}")

conn.close()
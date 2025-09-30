import sqlite3

conn = sqlite3.connect('financeiro.db')
conn.row_factory = sqlite3.Row

print("=== DADOS REAIS - Despesas Setembro/2025 ===")

# Lista dos 19 clientes FRZ (para despesas usamos fornecedores)
clientes_frz = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

cursor = conn.cursor()

# Despesas por fornecedor FRZ em setembro de 2025
query = """
SELECT fornecedor as cliente, SUM(valor_principal) as total_despesa
FROM contas_pagar 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
  AND fornecedor IN ({})
GROUP BY fornecedor
ORDER BY total_despesa DESC
""".format(','.join(['?' for _ in clientes_frz]))

cursor.execute(query, clientes_frz)
despesas_reais = cursor.fetchall()

if despesas_reais:
    total_despesas = 0
    for row in despesas_reais:
        valor = float(row['total_despesa'])
        total_despesas += valor
        print(f"  {row['cliente']}: R$ {valor:,.2f}")
    
    print(f"\nTOTAL DESPESAS: R$ {total_despesas:,.2f}")
    
    # Mostrar percentuais
    print("\n=== PERCENTUAIS ===")
    for row in despesas_reais:
        valor = float(row['total_despesa'])
        percentual = (valor / total_despesas * 100) if total_despesas > 0 else 0
        print(f"  {row['cliente']}: {percentual:.1f}%")
else:
    print("❌ Nenhum dado encontrado para setembro/2025")
    
    # Verificar se existem dados para outros meses
    print("\n=== Despesas disponíveis por competência ===")
    cursor.execute("""
        SELECT competencia, COUNT(*) as qtd, SUM(valor_principal) as total
        FROM contas_pagar 
        WHERE status = 'Recebido' 
          AND fornecedor IN ({})
        GROUP BY competencia 
        ORDER BY competencia DESC
        LIMIT 5
    """.format(','.join(['?' for _ in clientes_frz])))
    
    outros_meses = cursor.fetchall()
    for row in outros_meses:
        print(f"  {row['competencia']}: {row['qtd']} registros, R$ {row['total']:,.2f}")

print("\n=== TODOS os fornecedores (não só FRZ) ===")
cursor.execute("""
    SELECT fornecedor, SUM(valor_principal) as total_despesa
    FROM contas_pagar 
    WHERE competencia = '9/2025'
      AND status = 'Recebido'
    GROUP BY fornecedor
    ORDER BY total_despesa DESC
    LIMIT 10
""")

todos_fornecedores = cursor.fetchall()
if todos_fornecedores:
    print("Top 10 fornecedores em setembro/2025:")
    for row in todos_fornecedores:
        valor = float(row['total_despesa'])
        print(f"  {row['fornecedor']}: R$ {valor:,.2f}")

conn.close()
import sqlite3

conn = sqlite3.connect('financeiro.db')
conn.row_factory = sqlite3.Row

print("=== DADOS REAIS - Receitas Setembro/2025 ===")

# Lista dos 19 clientes FRZ
clientes_frz = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

cursor = conn.cursor()

# Receitas por cliente FRZ em setembro de 2025
query = """
SELECT cliente, SUM(valor_principal) as total_receita
FROM contas_receber 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
  AND cliente IN ({})
GROUP BY cliente
ORDER BY total_receita DESC
""".format(','.join(['?' for _ in clientes_frz]))

cursor.execute(query, clientes_frz)
receitas_reais = cursor.fetchall()

if receitas_reais:
    total_receitas = 0
    for row in receitas_reais:
        valor = float(row['total_receita'])
        total_receitas += valor
        percentual = 0  # Será calculado depois
        print(f"  {row['cliente']}: R$ {valor:,.2f}")
    
    print(f"\nTOTAL RECEITAS: R$ {total_receitas:,.2f}")
    
    # Mostrar percentuais
    print("\n=== PERCENTUAIS ===")
    for row in receitas_reais:
        valor = float(row['total_receita'])
        percentual = (valor / total_receitas * 100) if total_receitas > 0 else 0
        print(f"  {row['cliente']}: {percentual:.1f}%")
else:
    print("❌ Nenhum dado encontrado para setembro/2025")
    
    # Verificar se existem dados para outros meses
    print("\n=== Dados disponíveis por competência ===")
    cursor.execute("""
        SELECT competencia, COUNT(*) as qtd, SUM(valor_principal) as total
        FROM contas_receber 
        WHERE status = 'Recebido' 
          AND cliente IN ({})
        GROUP BY competencia 
        ORDER BY competencia DESC
        LIMIT 5
    """.format(','.join(['?' for _ in clientes_frz])))
    
    outros_meses = cursor.fetchall()
    for row in outros_meses:
        print(f"  {row['competencia']}: {row['qtd']} registros, R$ {row['total']:,.2f}")

conn.close()
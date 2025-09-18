import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Verificando dados para agosto ===")

# Busca todos os registros recebidos em agosto de qualquer ano
cur.execute("""
    SELECT vencimento, cliente, valor_principal, status 
    FROM contas_receber 
    WHERE status = 'Recebido' 
    AND vencimento LIKE '%/08/%'
    LIMIT 20
""")

dados_agosto = cur.fetchall()
print(f"Registros recebidos em agosto: {len(dados_agosto)}")
for row in dados_agosto:
    print(f"  {row[0]} - {row[1]} - R$ {float(row[2]):.2f}")

# Verificar especificamente para 2025
print("\n=== Verificando especificamente para agosto/2025 ===")
cur.execute("""
    SELECT vencimento, cliente, valor_principal, status 
    FROM contas_receber 
    WHERE status = 'Recebido' 
    AND vencimento LIKE '%/08/2025'
    LIMIT 10
""")

dados_agosto_2025 = cur.fetchall()
print(f"Registros recebidos em agosto/2025: {len(dados_agosto_2025)}")
for row in dados_agosto_2025:
    print(f"  {row[0]} - {row[1]} - R$ {float(row[2]):.2f}")

# Verificar todos os anos disponíveis
print("\n=== Anos disponíveis nos dados ===")
cur.execute("""
    SELECT DISTINCT 
        SUBSTR(vencimento, -4) as ano,
        COUNT(*) as total
    FROM contas_receber 
    WHERE status = 'Recebido'
    AND vencimento LIKE '%/%/%'
    GROUP BY ano
    ORDER BY ano
""")

anos = cur.fetchall()
for ano, total in anos:
    print(f"  Ano {ano}: {total} registros recebidos")

# Se não há dados para 2025, vamos testar com o ano que tem mais dados
if anos:
    ano_principal = anos[-1][0]  # Pega o último ano (mais recente)
    print(f"\n=== Testando com ano {ano_principal} ===")
    
    correspondencias = {
        'MINERVA S A': ['MINERVA S A'],
        'ADORO FOODS': ['ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS'],
        'GOLDPAC CD SAO JOSE DOS CAMPOS': ['GOLDPAO CD SAO JOSE DOS CAMPOS'],
        'GFOODS BARUERI': ['GTFOODS BARUERI', 'GTFOODS BARUERI '],
    }
    
    total_encontrado = 0
    for cliente_proj, nomes_banco in correspondencias.items():
        for nome_banco in nomes_banco:
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0), COUNT(*) 
                FROM contas_receber 
                WHERE status = 'Recebido' 
                AND vencimento LIKE ?
                AND TRIM(UPPER(cliente)) = TRIM(UPPER(?))
            """, (f"%/08/{ano_principal}", nome_banco))
            resultado = cur.fetchone()
            if resultado[0] > 0:
                print(f"  {cliente_proj} ({nome_banco}): R$ {float(resultado[0]):.2f} ({resultado[1]} registros)")
                total_encontrado += float(resultado[0])
    
    print(f"\nTotal encontrado para 08/{ano_principal}: R$ {total_encontrado:.2f}")

conn.close()
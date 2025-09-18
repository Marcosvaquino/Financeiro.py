import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Verificando formato das datas ===")
cur.execute("SELECT vencimento, cliente, valor_principal, status FROM contas_receber LIMIT 10")
samples = cur.fetchall()

for row in samples:
    print(f"Vencimento: '{row[0]}', Cliente: '{row[1]}', Valor: {row[2]}, Status: '{row[3]}'")

print("\n=== Verificando clientes que coincidem com projeção ===")

# Lista de clientes da projeção
clientes_projecao = [
    'ADORO FOODS', 'MARFRIG GLOBAL FOODS', 'GOLDPAC CD SAO JOSE DOS CAMPOS', 
    'GFOODS BARUERI', 'LATICINIO CARMONA', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'SANTA LUCIA', 'SAUDALI', 'VALENCIA JATAI'
]

# Mapas de correspondência baseados no que vimos nos dados
correspondencias = {
    'GOLDPAC CD SAO JOSE DOS CAMPOS': 'GOLDPAO CD SAO JOSE DOS CAMPOS',
    'VALENCIA JATAI': 'Valencio Jataí',
    'GFOODS BARUERI': 'GTFOODS BARUERI',
    'ADORO FOODS': 'ADORO',
    'MARFRIG GLOBAL FOODS': 'MARFRIG GLOBAL FOODS S A',
    'SAUDALI': 'Saudali',
    'SANTA LUCIA': 'SANTA LUCIA',
    'LATICINIO CARMONA': 'LATICINIO CARMONA',
    'MINERVA S A': 'MINERVA S A',
    'PAMPLONA JANDIRA': 'PAMPLONA JANDIRA'
}

total_recebido = 0
count_recebido = 0

for cliente_proj, cliente_bd in correspondencias.items():
    cur.execute("""
        SELECT COALESCE(SUM(valor_principal), 0), COUNT(*) 
        FROM contas_receber 
        WHERE status = 'Recebido' 
        AND (UPPER(cliente) LIKE ? OR cliente = ?)
    """, (f"%{cliente_bd.upper()}%", cliente_bd))
    
    resultado = cur.fetchone()
    if resultado[0] > 0:
        print(f"  {cliente_proj} ({cliente_bd}): R$ {resultado[0]:.2f} ({resultado[1]} registros)")
        total_recebido += resultado[0]
        count_recebido += resultado[1]

print(f"\nTotal recebido de clientes da projeção: R$ {total_recebido:.2f} ({count_recebido} registros)")

# Vamos verificar especificamente valores que tenham datas válidas no formato DD/MM/YYYY
print("\n=== Verificando datas no formato brasileiro ===")
cur.execute("""
    SELECT vencimento, cliente, valor_principal, status 
    FROM contas_receber 
    WHERE vencimento LIKE '%/08/2025' AND status = 'Recebido'
    AND (UPPER(cliente) LIKE '%MINERVA%' OR UPPER(cliente) LIKE '%ADORO%' OR UPPER(cliente) LIKE '%MARFRIG%')
    LIMIT 10
""")

dados_agosto = cur.fetchall()
for row in dados_agosto:
    print(f"  {row[0]} - {row[1]} - R$ {row[2]:.2f} - {row[3]}")

# Calcular total para agosto 2025 usando formato brasileiro
print("\n=== Total para agosto 2025 dos clientes da projeção ===")
total_agosto = 0
count_agosto = 0

for cliente_proj, cliente_bd in correspondencias.items():
    cur.execute("""
        SELECT COALESCE(SUM(valor_principal), 0), COUNT(*) 
        FROM contas_receber 
        WHERE status = 'Recebido' 
        AND vencimento LIKE '%/08/2025'
        AND (UPPER(cliente) LIKE ? OR cliente = ?)
    """, (f"%{cliente_bd.upper()}%", cliente_bd))
    
    resultado = cur.fetchone()
    if resultado[0] > 0:
        print(f"  {cliente_proj}: R$ {resultado[0]:.2f} ({resultado[1]} registros)")
        total_agosto += resultado[0]
        count_agosto += resultado[1]

print(f"\nTotal recebido em 08/2025 dos clientes da projeção: R$ {total_agosto:.2f} ({count_agosto} registros)")

conn.close()
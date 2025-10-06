import sqlite3

# Conectar ao banco
conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()

print("=== VEÍCULOS SUPORTE ===")
cursor.execute("SELECT * FROM veiculos_suporte LIMIT 10")
veiculos = cursor.fetchall()
cursor.execute("PRAGMA table_info(veiculos_suporte)")
cols_veiculos = [col[1] for col in cursor.fetchall()]
print(f"Colunas: {cols_veiculos}")
print("Primeiros 10 registros:")
for v in veiculos:
    print(f"  {v}")

print(f"\n=== ESTATÍSTICAS DOS VEÍCULOS ===")
cursor.execute("SELECT status, COUNT(*) FROM veiculos_suporte GROUP BY status")
stats = cursor.fetchall()
for stat in stats:
    print(f"  {stat[0]}: {stat[1]} veículos")

print("\n=== CLIENTES SUPORTE ===")
cursor.execute("SELECT * FROM clientes_suporte LIMIT 10")
clientes = cursor.fetchall()
cursor.execute("PRAGMA table_info(clientes_suporte)")
cols_clientes = [col[1] for col in cursor.fetchall()]
print(f"Colunas: {cols_clientes}")
print("Primeiros 10 registros:")
for c in clientes:
    print(f"  {c}")

print("\n=== CUSTO FROTA ===")
cursor.execute("SELECT * FROM custo_frota LIMIT 5")
custos = cursor.fetchall()
cursor.execute("PRAGMA table_info(custo_frota)")
cols_custos = [col[1] for col in cursor.fetchall()]
print(f"Colunas: {cols_custos}")
print("Primeiros 5 registros:")
for c in custos:
    print(f"  {c}")

# Verificar se há outras tabelas que podem conter dados de frete
print("\n=== PROCURANDO POR DADOS DE FRETE ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('sqlite_sequence')")
all_tables = [t[0] for t in cursor.fetchall()]

for table in all_tables:
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        frete_keywords = ['frete', 'manifesto', 'viagem', 'placa', 'motorista', 'veiculo']
        if any(keyword in ' '.join(columns).lower() for keyword in frete_keywords):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table} ({count} registros): {columns}")
    except:
        pass

conn.close()
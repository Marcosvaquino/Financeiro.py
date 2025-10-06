import sqlite3

# Conectar ao banco
conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=== TABELAS DISPONÍVEIS ===")
for table in tables:
    print(f"- {table[0]}")

print("\n=== VERIFICANDO MANIFESTO ACUMULADO ===")
# Verificar se existe tabela de manifesto
manifesto_tables = [t[0] for t in tables if 'manifesto' in t[0].lower()]
if manifesto_tables:
    for table in manifesto_tables:
        print(f"\nTabela encontrada: {table}")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print("Colunas:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Registros: {count}")
        
        if count > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            print("Primeiros registros:")
            for row in rows:
                print(f"  {row}")
else:
    print("Nenhuma tabela de manifesto encontrada")

# Verificar tabelas relacionadas a frete
print("\n=== TABELAS RELACIONADAS A FRETE ===")
frete_tables = [t[0] for t in tables if any(word in t[0].lower() for word in ['frete', 'veiculo', 'cliente', 'motorista'])]
for table in frete_tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"- {table}: {count} registros")

conn.close()
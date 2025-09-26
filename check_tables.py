import sqlite3

conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()

# Ver todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tabelas disponíveis:")
for table in tables:
    print(f"- {table[0]}")
    
    # Ver estrutura de cada tabela
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"  Colunas:")
    for col in columns:
        print(f"    • {col[1]} ({col[2]})")
    print()

conn.close()
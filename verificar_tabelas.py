import sqlite3

conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()

# Verificar tabelas existentes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [row[0] for row in cursor.fetchall()]
print("Tabelas encontradas:", tabelas)

# Verificar se existe tabela relacionada a veículos
for tabela in tabelas:
    if 'veiculo' in tabela.lower() or 'vehicle' in tabela.lower():
        print(f"\nTabela relacionada a veículos: {tabela}")
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = cursor.fetchall()
        print(f"Colunas da tabela {tabela}:")
        for coluna in colunas:
            print(f"  - {coluna[1]} ({coluna[2]})")

conn.close()
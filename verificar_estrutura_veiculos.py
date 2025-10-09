import sqlite3

conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()

# Verificar estrutura completa da tabela veiculos_suporte
cursor.execute("PRAGMA table_info(veiculos_suporte)")
colunas = cursor.fetchall()
print("Estrutura da tabela veiculos_suporte:")
for coluna in colunas:
    print(f"  - {coluna[1]} ({coluna[2]})")

print("\n" + "="*50)

# Verificar dados únicos na coluna tipologia
cursor.execute("SELECT DISTINCT tipologia FROM veiculos_suporte ORDER BY tipologia")
tipologias = cursor.fetchall()
print("\nTipologias únicas encontradas:")
for tip in tipologias:
    print(f"  - {tip[0]}")

print("\n" + "="*50)

# Verificar se existe coluna perfil ou similar
cursor.execute("SELECT * FROM veiculos_suporte LIMIT 5")
dados = cursor.fetchall()
print("\nPrimeiros 5 registros completos:")
for i, registro in enumerate(dados):
    print(f"  Registro {i+1}: {registro}")

# Verificar se existe outras colunas que podem conter informação de perfil
cursor.execute("SELECT name FROM pragma_table_info('veiculos_suporte')")
todas_colunas = [row[0] for row in cursor.fetchall()]
print(f"\nTodas as colunas: {todas_colunas}")

conn.close()
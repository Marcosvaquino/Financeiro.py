import sqlite3
import os

# Verificar se o banco existe
db_path = 'financeiro.db'
if not os.path.exists(db_path):
    print(f"❌ Banco não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar se a tabela existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes_suporte'")
if not cursor.fetchone():
    print("❌ Tabela clientes_suporte não existe")
    conn.close()
    exit(1)

# Contar clientes ativos
cursor.execute('SELECT COUNT(*) FROM clientes_suporte WHERE ativo = 1')
total = cursor.fetchone()[0]
print(f'📊 Total clientes ativos: {total}')

if total > 0:
    print("\n🔍 Primeiros 10 clientes:")
    cursor.execute('SELECT nome_real, nome_ajustado FROM clientes_suporte WHERE ativo = 1 LIMIT 10')
    for i, (nome_real, nome_ajustado) in enumerate(cursor.fetchall(), 1):
        print(f"{i:2d}. '{nome_real}' -> '{nome_ajustado}'")
else:
    print("❌ Nenhum cliente ativo encontrado!")

conn.close()
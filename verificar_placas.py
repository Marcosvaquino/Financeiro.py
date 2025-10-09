import sqlite3

conn = sqlite3.connect('financeiro.db')
cursor = conn.cursor()

# Verificar algumas placas na tabela veiculos_suporte
cursor.execute("SELECT placa, tipologia FROM veiculos_suporte LIMIT 10")
resultado = cursor.fetchall()

print("Primeiras 10 placas na tabela veiculos_suporte:")
for placa, tipologia in resultado:
    print(f"Placa: {placa} | Tipologia: {tipologia}")

conn.close()
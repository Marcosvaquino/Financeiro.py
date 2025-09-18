#!/usr/bin/env python3
"""
Script para limpar e preparar banco para nova importação
"""
import sqlite3
import os

# Conectar ao banco da raiz
db_path = 'financeiro.db'
print(f"🔄 Limpando banco: {db_path}")

if not os.path.exists(db_path):
    print(f"❌ Banco não encontrado!")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Contar registros antes
cur.execute("SELECT COUNT(*) FROM contas_receber")
antes = cur.fetchone()[0]
print(f"📊 Registros antes da limpeza: {antes:,}")

# Limpar tabela contas_receber
cur.execute("DELETE FROM contas_receber")
conn.commit()

# Resetar sequência auto-increment
cur.execute("DELETE FROM sqlite_sequence WHERE name='contas_receber'")
conn.commit()

# Contar registros depois
cur.execute("SELECT COUNT(*) FROM contas_receber")
depois = cur.fetchone()[0]
print(f"📊 Registros após limpeza: {depois:,}")

conn.close()
print("✅ Banco limpo e pronto para nova importação!")
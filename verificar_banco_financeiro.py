#!/usr/bin/env python3
"""
Script para verificar dados no banco financeiro/financeiro.db
"""
import sqlite3
import os

# Conectar ao banco na pasta financeiro
db_path = os.path.join('financeiro', 'financeiro.db')
print(f"🔍 Verificando banco: {db_path}")

if not os.path.exists(db_path):
    print(f"❌ Banco não encontrado!")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verificar estrutura das tabelas
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cur.fetchall()
print(f"📊 Tabelas encontradas: {[t[0] for t in tabelas]}")

# Verificar dados em contas_receber
cur.execute("SELECT COUNT(*) FROM contas_receber")
total = cur.fetchone()[0]
print(f"📈 Total registros contas_receber: {total:,}")

if total > 0:
    # Verificar clientes
    cur.execute("SELECT DISTINCT cliente FROM contas_receber LIMIT 10")
    clientes = cur.fetchall()
    print(f"👥 Primeiros clientes: {[c[0] for c in clientes]}")
    
    # Verificar status
    cur.execute("SELECT DISTINCT status, COUNT(*) FROM contas_receber GROUP BY status")
    status = cur.fetchall()
    print(f"📊 Status encontrados: {dict(status)}")
    
    # Verificar MINERVA especificamente
    cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE cliente LIKE '%MINERVA%'")
    minerva = cur.fetchone()
    print(f"🔍 MINERVA S A: {minerva[0]:,} registros - R$ {minerva[1] or 0:,.2f}")

conn.close()
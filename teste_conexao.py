#!/usr/bin/env python3
import sqlite3
import os

print("TESTE BÁSICO DE CONEXÃO")
print("=" * 40)

# Testar banco da raiz
print("1. Banco da raiz:")
print(f"   Caminho: {os.path.abspath('financeiro.db')}")
print(f"   Existe: {os.path.exists('financeiro.db')}")
if os.path.exists('financeiro.db'):
    try:
        conn = sqlite3.connect('financeiro.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM contas_receber")
        count = cur.fetchone()[0]
        print(f"   Registros: {count:,}")
        
        # Testar uma consulta simples
        cur.execute("SELECT cliente FROM contas_receber LIMIT 1")
        resultado = cur.fetchone()
        print(f"   Primeiro cliente: {resultado}")
        
        conn.close()
    except Exception as e:
        print(f"   ERRO: {e}")

print()

# Testar banco da pasta financeiro
print("2. Banco financeiro/:")
caminho_financeiro = os.path.join('financeiro', 'financeiro.db')
print(f"   Caminho: {os.path.abspath(caminho_financeiro)}")
print(f"   Existe: {os.path.exists(caminho_financeiro)}")
if os.path.exists(caminho_financeiro):
    try:
        conn = sqlite3.connect(caminho_financeiro)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM contas_receber")
        count = cur.fetchone()[0]
        print(f"   Registros: {count:,}")
        
        # Testar uma consulta simples
        cur.execute("SELECT cliente FROM contas_receber LIMIT 1")
        resultado = cur.fetchone()
        print(f"   Primeiro cliente: {resultado}")
        
        conn.close()
    except Exception as e:
        print(f"   ERRO: {e}")
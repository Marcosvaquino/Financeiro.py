#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== ESTRUTURA DA TABELA CONTAS_PAGAR ===")

# Ver estrutura da tabela
cursor = conn.execute("PRAGMA table_info(contas_pagar)")
colunas = cursor.fetchall()
print("Colunas disponíveis:")
for col in colunas:
    print(f"  {col[1]} ({col[2]})")

print("\n=== SAMPLE DOS DADOS ===")
# Ver alguns exemplos de dados
query = """
SELECT fornecedor, conta_contabil, valor_principal, competencia, status
FROM contas_pagar 
WHERE competencia = '9/2025' AND status = 'Recebido'
ORDER BY valor_principal DESC
LIMIT 10
"""

result = conn.execute(query).fetchall()
for row in result:
    print(f"Fornecedor: {row['fornecedor']}")
    print(f"Conta Contábil: {row['conta_contabil']}")
    print(f"Valor: R$ {row['valor_principal']:,.2f}")
    print("-" * 50)

conn.close()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== DESPESAS CORRIGIDAS (SEM REIS TRANSPORTES) ===")

query = """
SELECT fornecedor, SUM(valor_principal) as total_despesa
FROM contas_pagar 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
  AND fornecedor != 'REIS TRANSPORTES'
GROUP BY fornecedor
ORDER BY total_despesa DESC
LIMIT 15
"""

resultado = conn.execute(query).fetchall()
total_geral = 0

print("Top 15 fornecedores (excluindo REIS TRANSPORTES):")
for i, row in enumerate(resultado, 1):
    valor = float(row['total_despesa'])
    total_geral += valor
    percentual = (valor / 626089.32) * 100  # Total que calculamos antes
    print(f"{i:2d}. {row['fornecedor']:<50} R$ {valor:>12,.2f} ({percentual:5.1f}%)")

print(f"\nTOTAL GERAL: R$ {total_geral:,.2f}")
print(f"Diferença para valor esperado: R$ {abs(total_geral - 626089.32):,.2f}")

conn.close()
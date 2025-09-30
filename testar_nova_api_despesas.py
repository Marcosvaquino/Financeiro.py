#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import json

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== TESTE DA NOVA API DE DESPESAS ===")

# Simular a consulta da API
query = """
SELECT fornecedor, conta_contabil, valor_principal
FROM contas_pagar 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
  AND fornecedor != 'REIS TRANSPORTES'
ORDER BY valor_principal DESC
"""

resultado = conn.execute(query).fetchall()

despesas_data = []
total_geral = 0

for row in resultado:
    valor = float(row['valor_principal'])
    despesas_data.append({
        'fornecedor': row['fornecedor'],
        'conta_contabil': row['conta_contabil'],
        'valor': valor
    })
    total_geral += valor

print(f"Total de registros: {len(despesas_data)}")
print(f"Total geral: R$ {total_geral:,.2f}")

print("\nPrimeiros 10 registros:")
for i, despesa in enumerate(despesas_data[:10], 1):
    print(f"{i:2d}. {despesa['fornecedor']:<30} | {despesa['conta_contabil']:<25} | R$ {despesa['valor']:>10,.2f}")

print("\nÚltimos 10 registros:")
for i, despesa in enumerate(despesas_data[-10:], len(despesas_data)-9):
    print(f"{i:2d}. {despesa['fornecedor']:<30} | {despesa['conta_contabil']:<25} | R$ {despesa['valor']:>10,.2f}")

# Teste de filtros
print("\n=== TESTE DE FILTROS ===")

# Filtro por fornecedor contendo "SODEXO"
filtradas_sodexo = [d for d in despesas_data if 'SODEXO' in d['fornecedor'].upper()]
print(f"\nRegistros com 'SODEXO': {len(filtradas_sodexo)}")
for despesa in filtradas_sodexo[:5]:
    print(f"  {despesa['fornecedor']} | {despesa['conta_contabil']} | R$ {despesa['valor']:,.2f}")

# Filtro por conta contábil contendo "FRETE"
filtradas_frete = [d for d in despesas_data if 'FRETE' in d['conta_contabil'].upper()]
print(f"\nRegistros com 'FRETE' na conta: {len(filtradas_frete)}")
for despesa in filtradas_frete[:5]:
    print(f"  {despesa['fornecedor']} | {despesa['conta_contabil']} | R$ {despesa['valor']:,.2f}")

conn.close()
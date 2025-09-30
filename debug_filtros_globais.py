#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== VERIFICANDO FILTROS GLOBAIS ===")

# 1. Primeiro, vamos ver TODOS os fornecedores em setembro/2025
print("\n1. TODOS os fornecedores em setembro/2025:")
query = """
SELECT fornecedor, SUM(valor_principal) as total
FROM contas_pagar 
WHERE competencia = '9/2025' AND status = 'Recebido'
GROUP BY fornecedor
ORDER BY total DESC
LIMIT 10
"""
result = conn.execute(query).fetchall()
for row in result:
    print(f"  {row['fornecedor']}: R$ {row['total']:,.2f}")

# 2. Agora SEM REIS TRANSPORTES
print("\n2. SEM REIS TRANSPORTES:")
query = """
SELECT fornecedor, SUM(valor_principal) as total
FROM contas_pagar 
WHERE competencia = '9/2025' 
  AND status = 'Recebido'
  AND fornecedor != 'REIS TRANSPORTES'
GROUP BY fornecedor
ORDER BY total DESC
LIMIT 10
"""
result = conn.execute(query).fetchall()
total_sem_reis = 0
for row in result:
    total_sem_reis += row['total']
    print(f"  {row['fornecedor']}: R$ {row['total']:,.2f}")

print(f"\nTOTAL SEM REIS: R$ {total_sem_reis:,.2f}")

# 3. Vamos verificar quantos registros tem REIS TRANSPORTES
print("\n3. Registros de REIS TRANSPORTES em setembro/2025:")
query = """
SELECT COUNT(*) as qtd, SUM(valor_principal) as total
FROM contas_pagar 
WHERE competencia = '9/2025' 
  AND status = 'Recebido'
  AND fornecedor = 'REIS TRANSPORTES'
"""
result = conn.execute(query).fetchone()
print(f"  Quantidade: {result['qtd']}")
print(f"  Total: R$ {result['total']:,.2f}")

# 4. Verificar outros possíveis filtros
print("\n4. Verificando se há outros fornecedores que podem estar sendo filtrados:")
query = """
SELECT fornecedor, COUNT(*) as qtd, SUM(valor_principal) as total
FROM contas_pagar 
WHERE competencia = '9/2025' AND status = 'Recebido'
  AND (fornecedor LIKE '%LSP%' OR fornecedor LIKE '%TRANSPORT%')
GROUP BY fornecedor
ORDER BY total DESC
"""
result = conn.execute(query).fetchall()
for row in result:
    print(f"  {row['fornecedor']}: {row['qtd']} registros, R$ {row['total']:,.2f}")

conn.close()
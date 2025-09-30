#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== INVESTIGAÇÃO DA INCONSISTÊNCIA DE DADOS ===")

# Lista dos 19 clientes FRZ
clientes_frz = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

print("=== ANÁLISE SETEMBRO 2025 ===")

# 1. RECEITAS DOS 19 CLIENTES FRZ (modal)
query_receitas_modal = """
SELECT SUM(valor_principal) as total_receitas
FROM contas_receber 
WHERE competencia = ?
  AND status = 'Recebido'
  AND cliente IN ({})
""".format(','.join(['?'] * len(clientes_frz)))

params = ['9/2025'] + clientes_frz
receitas_modal = conn.execute(query_receitas_modal, params).fetchone()
total_receitas_modal = float(receitas_modal['total_receitas'] or 0)

print(f"Receitas (19 clientes FRZ) - MODAL: R$ {total_receitas_modal:,.2f}")

# 2. DESPESAS SEM REIS TRANSPORTES (modal)
query_despesas_modal = """
SELECT SUM(valor_principal) as total_despesas
FROM contas_pagar 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
  AND fornecedor != 'REIS TRANSPORTES'
"""

despesas_modal = conn.execute(query_despesas_modal).fetchone()
total_despesas_modal = float(despesas_modal['total_despesas'] or 0)

print(f"Despesas (sem REIS) - MODAL: R$ {total_despesas_modal:,.2f}")

resultado_modal = total_receitas_modal - total_despesas_modal
print(f"RESULTADO MODAL: R$ {resultado_modal:,.2f}")

print("\n" + "="*60)

# 3. DADOS DO DASHBOARD PRINCIPAL (função build_dados_frz)
print("=== DADOS DO DASHBOARD PRINCIPAL ===")

# Simular a consulta do dashboard principal
# Vou verificar como são calculados os dados críticos

# Receitas TOTAIS (não só 19 clientes)
query_receitas_dash = """
SELECT SUM(valor_principal) as total_receitas
FROM contas_receber 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
"""

receitas_dash = conn.execute(query_receitas_dash).fetchone()
total_receitas_dash = float(receitas_dash['total_receitas'] or 0)

print(f"Receitas TOTAIS - DASHBOARD: R$ {total_receitas_dash:,.2f}")

# Despesas TOTAIS (incluindo REIS?)
query_despesas_dash = """
SELECT SUM(valor_principal) as total_despesas
FROM contas_pagar 
WHERE competencia = '9/2025'
  AND status = 'Recebido'
"""

despesas_dash = conn.execute(query_despesas_dash).fetchone()
total_despesas_dash = float(despesas_dash['total_despesas'] or 0)

print(f"Despesas TOTAIS - DASHBOARD: R$ {total_despesas_dash:,.2f}")

resultado_dash = total_receitas_dash - total_despesas_dash
print(f"RESULTADO DASHBOARD: R$ {resultado_dash:,.2f}")

print("\n" + "="*60)
print("=== COMPARAÇÃO ===")
print(f"Resultado MODAL:     R$ {resultado_modal:>15,.2f}")
print(f"Resultado DASHBOARD: R$ {resultado_dash:>15,.2f}")
print(f"DIFERENÇA:           R$ {abs(resultado_modal - resultado_dash):>15,.2f}")

print("\n=== POSSÍVEIS CAUSAS ===")
print("1. Modal usa apenas 19 clientes FRZ vs Dashboard usa todos os clientes")
print("2. Modal exclui REIS TRANSPORTES vs Dashboard pode incluir")
print("3. Diferentes critérios de status ou competência")

conn.close()
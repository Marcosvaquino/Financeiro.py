#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== INVESTIGAÇÃO COMPLETA DOS DADOS - SETEMBRO 2025 ===")

# 1. DASHBOARD - Cards inferiores (provavelmente dados totais)
print("\n🔍 DASHBOARD - Cards Inferiores:")
print("Resultado: -R$ 648.805")
print("Receitas:  R$ 2.372.321") 
print("Despesas:  R$ 3.021.126")
print("✅ Conferência: 2.372.321 - 3.021.126 = -648.805 ✅")

# 2. MODAL - Dados que estão sendo mostrados
print("\n🔍 MODAL - Dados Mostrados:")
print("Resultado: -R$ 2.122.573,66")
print("Receitas:  R$ 1.648.503 (agosto!)")
print("Despesas:  R$ 3.771.076")

print("\n" + "="*80)
print("VAMOS DESCOBRIR DE ONDE VÊM OS DADOS DO DASHBOARD")
print("="*80)

# Lista dos 19 clientes FRZ
clientes_frz = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA',
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO',
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA',
    'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

# TESTE 1: Receitas TOTAIS (todos os clientes)
query1 = "SELECT SUM(valor_principal) as total FROM contas_receber WHERE competencia = '9/2025' AND status = 'Recebido'"
result1 = conn.execute(query1).fetchone()
print(f"1. Receitas TOTAIS (todos clientes): R$ {float(result1['total'] or 0):,.2f}")

# TESTE 2: Receitas dos 19 clientes FRZ
query2 = """SELECT SUM(valor_principal) as total FROM contas_receber 
            WHERE competencia = ? AND status = 'Recebido' 
            AND cliente IN ({})""".format(','.join(['?'] * len(clientes_frz)))
params2 = ['9/2025'] + clientes_frz
result2 = conn.execute(query2, params2).fetchone()
print(f"2. Receitas FRZ (19 clientes): R$ {float(result2['total'] or 0):,.2f}")

# TESTE 3: Despesas TOTAIS (incluindo REIS)
query3 = "SELECT SUM(valor_principal) as total FROM contas_pagar WHERE competencia = '9/2025' AND status = 'Recebido'"
result3 = conn.execute(query3).fetchone()
print(f"3. Despesas TOTAIS (com REIS): R$ {float(result3['total'] or 0):,.2f}")

# TESTE 4: Despesas sem REIS TRANSPORTES
query4 = "SELECT SUM(valor_principal) as total FROM contas_pagar WHERE competencia = '9/2025' AND status = 'Recebido' AND fornecedor != 'REIS TRANSPORTES'"
result4 = conn.execute(query4).fetchone()
print(f"4. Despesas sem REIS TRANSPORTES: R$ {float(result4['total'] or 0):,.2f}")

# TESTE 5: Apenas REIS TRANSPORTES
query5 = "SELECT SUM(valor_principal) as total FROM contas_pagar WHERE competencia = '9/2025' AND status = 'Recebido' AND fornecedor = 'REIS TRANSPORTES'"
result5 = conn.execute(query5).fetchone()
print(f"5. Apenas REIS TRANSPORTES: R$ {float(result5['total'] or 0):,.2f}")

print("\n" + "="*80)
print("COMPARAÇÃO COM OS VALORES DO DASHBOARD:")
print("="*80)

dashboard_receitas = 2372321
dashboard_despesas = 3021126
dashboard_resultado = -648805

r1 = float(result1['total'] or 0)
r2 = float(result2['total'] or 0) 
d3 = float(result3['total'] or 0)
d4 = float(result4['total'] or 0)
reis = float(result5['total'] or 0)

print(f"Dashboard Receitas: R$ {dashboard_receitas:,.2f}")
print(f"✓ Receitas Totais:  R$ {r1:,.2f} {'✅' if abs(r1 - dashboard_receitas) < 1000 else '❌'}")
print(f"✓ Receitas FRZ:     R$ {r2:,.2f} {'✅' if abs(r2 - dashboard_receitas) < 1000 else '❌'}")

print(f"\nDashboard Despesas: R$ {dashboard_despesas:,.2f}")
print(f"✓ Despesas Totais:  R$ {d3:,.2f} {'✅' if abs(d3 - dashboard_despesas) < 1000 else '❌'}")
print(f"✓ Despesas s/REIS:  R$ {d4:,.2f} {'✅' if abs(d4 - dashboard_despesas) < 1000 else '❌'}")

print(f"\nREIS TRANSPORTES: R$ {reis:,.2f}")
print(f"Despesas com REIS - Despesas sem REIS = {d3:,.2f} - {d4:,.2f} = {d3-d4:,.2f}")

print("\n" + "="*80)
print("CONCLUSÃO:")
print("="*80)

if abs(r1 - dashboard_receitas) < 1000:
    print("✅ Dashboard usa RECEITAS TOTAIS")
else:
    print("❌ Dashboard não usa receitas totais")

if abs(d4 - dashboard_despesas) < 1000:
    print("✅ Dashboard usa DESPESAS SEM REIS")
elif abs(d3 - dashboard_despesas) < 1000:
    print("✅ Dashboard usa DESPESAS TOTAIS")
else:
    print("❌ Dashboard usa algum outro critério para despesas")

conn.close()
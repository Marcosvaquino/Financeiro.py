#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== ANÁLISE DOS DADOS DE RESULTADO ===")

# Lista dos 19 clientes FRZ
clientes_frz = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

# Análise dos últimos 3 meses
for i, mes_nome in enumerate([(9, 2025, "Setembro"), (8, 2025, "Agosto"), (7, 2025, "Julho")]):
    mes, ano, nome = mes_nome
    print(f"\n=== {nome.upper()} {ano} ===")
    
    # Receitas dos 19 clientes FRZ
    query_receitas = """
    SELECT SUM(valor_principal) as total_receitas
    FROM contas_receber 
    WHERE competencia = ?
      AND status = 'Recebido'
      AND cliente IN ({})
    """.format(','.join(['?'] * len(clientes_frz)))
    
    params = [f"{mes}/{ano}"] + clientes_frz
    receitas = conn.execute(query_receitas, params).fetchone()
    total_receitas = float(receitas['total_receitas'] or 0)
    
    # Despesas (TODOS os fornecedores EXCETO REIS TRANSPORTES)
    query_despesas = """
    SELECT SUM(valor_principal) as total_despesas
    FROM contas_pagar 
    WHERE competencia = ?
      AND status = 'Recebido'
      AND fornecedor != 'REIS TRANSPORTES'
    """
    
    despesas = conn.execute(query_despesas, [f"{mes}/{ano}"]).fetchone()
    total_despesas = float(despesas['total_despesas'] or 0)
    
    resultado = total_receitas - total_despesas
    margem = (resultado / total_receitas * 100) if total_receitas > 0 else 0
    
    print(f"Receitas (19 clientes FRZ): R$ {total_receitas:>12,.2f}")
    print(f"Despesas (sem REIS):        R$ {total_despesas:>12,.2f}")
    print(f"Resultado:                  R$ {resultado:>12,.2f}")
    print(f"Margem:                     {margem:>12.1f}%")
    
    # Ver os principais clientes do mês
    query_top_clientes = """
    SELECT cliente, SUM(valor_principal) as total
    FROM contas_receber 
    WHERE competencia = ?
      AND status = 'Recebido'
      AND cliente IN ({})
    GROUP BY cliente
    ORDER BY total DESC
    LIMIT 3
    """.format(','.join(['?'] * len(clientes_frz)))
    
    top_clientes = conn.execute(query_top_clientes, params).fetchall()
    print("Top 3 clientes:")
    for cliente in top_clientes:
        print(f"  {cliente['cliente']:<30}: R$ {cliente['total']:>10,.2f}")

# Comparação mês a mês
print(f"\n=== COMPARAÇÃO MENSAL ===")
meses_dados = []

for mes, ano in [(9, 2025), (8, 2025), (7, 2025)]:
    # Receitas
    params = [f"{mes}/{ano}"] + clientes_frz
    receitas = conn.execute("""
    SELECT SUM(valor_principal) as total
    FROM contas_receber 
    WHERE competencia = ? AND status = 'Recebido' AND cliente IN ({})
    """.format(','.join(['?'] * len(clientes_frz))), params).fetchone()
    
    # Despesas
    despesas = conn.execute("""
    SELECT SUM(valor_principal) as total
    FROM contas_pagar 
    WHERE competencia = ? AND status = 'Recebido' AND fornecedor != 'REIS TRANSPORTES'
    """, [f"{mes}/{ano}"]).fetchone()
    
    r = float(receitas['total'] or 0)
    d = float(despesas['total'] or 0)
    
    meses_dados.append({
        'mes': f"{mes:02d}/{ano}",
        'receitas': r,
        'despesas': d,
        'resultado': r - d
    })

print("Evolução mensal:")
for i, dados in enumerate(meses_dados):
    variacao = ""
    if i > 0:
        resultado_anterior = meses_dados[i-1]['resultado']
        if resultado_anterior != 0:
            var_pct = ((dados['resultado'] - resultado_anterior) / abs(resultado_anterior)) * 100
            variacao = f" ({var_pct:+.1f}%)"
    
    print(f"{dados['mes']}: Resultado R$ {dados['resultado']:>10,.2f}{variacao}")

conn.close()
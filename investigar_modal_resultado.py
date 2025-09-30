#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Conectar no banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=== INVESTIGAÇÃO DOS DADOS DO MODAL ===")

# Lista dos 19 clientes FRZ
clientes_frz = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

# Vamos simular exatamente o que a API faz
for i in range(3):
    mes_atual = 9 - i  # Setembro, Agosto, Julho
    ano_atual = 2025
    
    print(f"\n=== MÊS {mes_atual:02d}/{ano_atual} ===")
    
    # RECEITAS: Apenas os 19 clientes FRZ
    query_receitas = """
    SELECT SUM(valor_principal) as total_receitas
    FROM contas_receber 
    WHERE competencia = ?
      AND status = 'Recebido'
      AND cliente IN ({})
    """.format(','.join(['?'] * len(clientes_frz)))
    
    params = [f"{mes_atual}/{ano_atual}"] + clientes_frz
    receitas = conn.execute(query_receitas, params).fetchone()
    total_receitas = float(receitas['total_receitas'] or 0)
    
    # DESPESAS: COMO ESTÁ NA API - SEM REIS TRANSPORTES e apenas FRZ clientes
    # Vamos verificar como está realmente na função buscar_resultado_comparativo
    query_despesas = """
    SELECT SUM(valor_principal) as total_despesas
    FROM contas_pagar 
    WHERE competencia = ?
      AND status = 'Recebido'
      AND fornecedor IN ({})
    """.format(','.join(['?'] * len(clientes_frz)))
    
    despesas = conn.execute(query_despesas, params).fetchone()
    total_despesas = float(despesas['total_despesas'] or 0)
    
    resultado = total_receitas - total_despesas
    margem = (resultado / total_receitas * 100) if total_receitas > 0 else 0
    
    print(f"Receitas (19 clientes): R$ {total_receitas:>12,.2f}")
    print(f"Despesas (19 clientes): R$ {total_despesas:>12,.2f}")  
    print(f"Resultado:              R$ {resultado:>12,.2f}")
    print(f"Margem:                 {margem:>12.1f}%")
    
    # Agora vamos comparar com TODAS as despesas (como deveria ser?)
    query_despesas_todas = """
    SELECT SUM(valor_principal) as total_despesas
    FROM contas_pagar 
    WHERE competencia = ?
      AND status = 'Recebido'
      AND fornecedor != 'REIS TRANSPORTES'
    """
    
    despesas_todas = conn.execute(query_despesas_todas, [f"{mes_atual}/{ano_atual}"]).fetchone()
    total_despesas_todas = float(despesas_todas['total_despesas'] or 0)
    
    resultado_real = total_receitas - total_despesas_todas
    margem_real = (resultado_real / total_receitas * 100) if total_receitas > 0 else 0
    
    print(f"\n--- COMPARAÇÃO COM TODAS AS DESPESAS ---")
    print(f"Despesas (TODAS):       R$ {total_despesas_todas:>12,.2f}")
    print(f"Resultado REAL:         R$ {resultado_real:>12,.2f}")
    print(f"Margem REAL:            {margem_real:>12.1f}%")

conn.close()
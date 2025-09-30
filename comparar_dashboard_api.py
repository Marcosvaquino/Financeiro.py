#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys

# Adicionar o caminho do módulo financeiro
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from financeiro.main import build_dados_frz_log

print("=== COMPARAÇÃO DASHBOARD vs API ===")

# Pegar os mesmos dados que o dashboard usa
dados_dashboard = build_dados_frz_log(9, 2025)
totais = dados_dashboard['dados_criticos']['totais_mes']

print("\n🖥️ DADOS DO DASHBOARD (build_dados_frz_log):")
print(f"Receitas: R$ {totais['receita_realizada']:,.2f}")
print(f"Despesas: R$ {totais['despesa_realizada']:,.2f}")
print(f"Resultado: R$ {totais['resultado_realizado']:,.2f}")

print("\n📊 DADOS QUE APARECEM NO CARD INFERIOR:")
print("Receitas: R$ 2.372.321")
print("Despesas: R$ 3.021.126") 
print("Resultado: -R$ 648.805")

print("\n🔍 DIFERENÇAS:")
print(f"Receitas: {totais['receita_realizada'] - 2372321:,.2f}")
print(f"Despesas: {totais['despesa_realizada'] - 3021126:,.2f}")
print(f"Resultado: {totais['resultado_realizado'] - (-648805):,.2f}")

print("\n" + "="*60)
print("CONCLUSÃO:")
if abs(totais['receita_realizada'] - 2372321) < 1000:
    print("✅ API está usando os dados corretos do dashboard")
else:
    print("❌ API NÃO está usando os dados corretos do dashboard")
    print("🔧 Precisa investigar de onde vem os R$ 2.372.321 do card inferior")
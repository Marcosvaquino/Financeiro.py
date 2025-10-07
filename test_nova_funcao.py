#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from financeiro.cliente_helper import ClienteHelper

print("=== TESTE DA NOVA FUNÇÃO DE MAPEAMENTO ===")
print()

# Clientes problemáticos do manifesto
clientes_problematicos = [
    "Adoro Varzea Paulista",
    "Marfrig ( BRF )",
    "Adoro Vista Foods", 
    "Transferência"
]

print("TESTANDO NOVA FUNÇÃO buscar_multiplos_nomes_manifesto:")
resultado_novo = ClienteHelper.buscar_multiplos_nomes_manifesto(clientes_problematicos)

for cliente, dados in resultado_novo.items():
    print(f"'{cliente}':")
    print(f"  -> Nome Real: {dados.get('nome_real')}")
    print(f"  -> Nome Ajustado: {dados.get('nome_ajustado')}")
    print(f"  -> Encontrado: {dados.get('encontrado')}")
    print(f"  -> Método: {dados.get('metodo')}")
    print()

print("ESTATÍSTICAS:")
encontrados = sum(1 for d in resultado_novo.values() if d.get('encontrado'))
print(f"Total testados: {len(clientes_problematicos)}")
print(f"Encontrados: {encontrados}")
print(f"Não encontrados: {len(clientes_problematicos) - encontrados}")
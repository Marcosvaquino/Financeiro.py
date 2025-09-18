#!/usr/bin/env python3
"""Teste dos clientes da projeção"""

import os
import sys
sys.path.append('financeiro')

from financeiro.database import get_connection

def teste_clientes_projecao():
    print("🔍 TESTANDO CLIENTES DA PROJEÇÃO")
    print("=" * 50)
    
    clientes_permitidos = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    
    print(f"📋 Lista de clientes permitidos: {len(clientes_permitidos)} clientes")
    
    # Testa quais clientes existem no banco
    placeholders = ','.join(['?' for _ in clientes_permitidos])
    cur.execute(f"""
        SELECT DISTINCT cliente 
        FROM contas_receber 
        WHERE cliente IN ({placeholders})
        ORDER BY cliente
    """, tuple(clientes_permitidos))
    
    clientes_encontrados = cur.fetchall()
    
    print(f"\n✅ Clientes encontrados no banco: {len(clientes_encontrados)}")
    for cliente in clientes_encontrados:
        print(f"  - {cliente[0]}")
    
    # Lista clientes que não foram encontrados
    nomes_encontrados = [c[0] for c in clientes_encontrados]
    nao_encontrados = [c for c in clientes_permitidos if c not in nomes_encontrados]
    
    if nao_encontrados:
        print(f"\n❌ Clientes não encontrados: {len(nao_encontrados)}")
        for cliente in nao_encontrados:
            print(f"  - {cliente}")
    
    conn.close()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    teste_clientes_projecao()
#!/usr/bin/env python3
"""
Teste final do filtro com a configuração correta
"""
import os
import sqlite3

# Usar o caminho correto do banco na raiz
conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

# Lista específica de clientes
clientes_filtro = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

print("🎯 TESTE FINAL DO SISTEMA")
print("=" * 50)
print(f"📍 Banco: financeiro.db (raiz)")

# Verificar total geral
cur.execute("SELECT COUNT(*) FROM contas_receber")
total = cur.fetchone()[0]
print(f"📊 Total registros: {total:,}")

# Testar filtro completo (igual ao implementado no Flask)
placeholders = ','.join(['?' for _ in clientes_filtro])
cur.execute(f"""
    SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) 
    FROM contas_receber 
    WHERE status = 'Recebido'
    AND vencimento LIKE ?
    AND cliente IN ({placeholders})
""", ("%/08/2025%",) + tuple(clientes_filtro))

count, valor = cur.fetchone()

print(f"💰 Resultado do filtro:")
print(f"   • Registros: {count:,}")
print(f"   • Valor: R$ {valor:,.2f}")

def formatar_valor_brasileiro(valor):
    if valor == 0:
        return "0,00"
    valor_str = f"{valor:.2f}"
    partes = valor_str.split('.')
    parte_inteira = partes[0]
    parte_decimal = partes[1]
    if len(parte_inteira) > 3:
        inteira_invertida = parte_inteira[::-1]
        com_pontos = '.'.join([inteira_invertida[i:i+3] for i in range(0, len(inteira_invertida), 3)])
        parte_inteira = com_pontos[::-1]
    return f"{parte_inteira},{parte_decimal}"

print(f"   • Formatado: R$ {formatar_valor_brasileiro(valor)}")

conn.close()
print("✅ Teste finalizado!")
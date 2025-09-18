#!/usr/bin/env python3
"""
Script para comparar estruturas e valores encontrados vs esperados
"""
import sqlite3
import os

# Conectar ao banco (mesmo caminho que o Flask usa)
db_path = os.path.join('financeiro', 'financeiro.db')
print(f"🔍 Verificando banco: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Lista de clientes do filtro atual
clientes_filtro = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

mes = "08"
ano = "2025"

print("=" * 70)
print("🔍 ANÁLISE DETALHADA DOS DADOS")
print("=" * 70)

# 1. Verificar todos os clientes únicos no banco para agosto/2025 com status Recebido
print("\n📊 1. TODOS OS CLIENTES no banco (agosto/2025, Recebido):")
cur.execute("""
    SELECT DISTINCT cliente, COUNT(*), SUM(valor_principal)
    FROM contas_receber 
    WHERE status = 'Recebido'
    AND vencimento LIKE ?
    GROUP BY cliente
    ORDER BY SUM(valor_principal) DESC
""", (f"%/{mes}/{ano}%",))

todos_clientes = cur.fetchall()
total_todos = sum(row[2] for row in todos_clientes)

for cliente, count, valor in todos_clientes:
    print(f"  • {cliente:<50} | {count:>3} reg | R$ {valor:>12,.2f}")

print(f"\n📈 TOTAL GERAL (todos os clientes): R$ {total_todos:,.2f}")

# 2. Verificar clientes que estão no filtro
print(f"\n📊 2. CLIENTES DO FILTRO encontrados:")
placeholders = ','.join(['?' for _ in clientes_filtro])
cur.execute(f"""
    SELECT DISTINCT cliente, COUNT(*), SUM(valor_principal)
    FROM contas_receber 
    WHERE status = 'Recebido'
    AND vencimento LIKE ?
    AND cliente IN ({placeholders})
    GROUP BY cliente
    ORDER BY SUM(valor_principal) DESC
""", (f"%/{mes}/{ano}%",) + tuple(clientes_filtro))

clientes_encontrados = cur.fetchall()
total_filtro = sum(row[2] for row in clientes_encontrados)

for cliente, count, valor in clientes_encontrados:
    print(f"  ✅ {cliente:<50} | {count:>3} reg | R$ {valor:>12,.2f}")

print(f"\n📈 TOTAL FILTRO: R$ {total_filtro:,.2f}")

# 3. Verificar clientes que estão no banco mas NÃO no filtro
print(f"\n📊 3. CLIENTES NÃO INCLUÍDOS NO FILTRO:")
clientes_no_banco = {row[0] for row in todos_clientes}
clientes_no_filtro = {cliente for cliente in clientes_no_banco if cliente not in clientes_filtro}

for cliente in sorted(clientes_no_filtro):
    cur.execute("""
        SELECT COUNT(*), SUM(valor_principal)
        FROM contas_receber 
        WHERE status = 'Recebido'
        AND vencimento LIKE ?
        AND cliente = ?
    """, (f"%/{mes}/{ano}%", cliente))
    count, valor = cur.fetchone()
    if valor:
        print(f"  ❌ {cliente:<50} | {count:>3} reg | R$ {valor:>12,.2f}")

# 4. Verificar se há variações de nome
print(f"\n📊 4. POSSÍVEIS VARIAÇÕES DE NOME:")
for filtro_cliente in clientes_filtro:
    # Buscar nomes similares
    cur.execute("""
        SELECT DISTINCT cliente, COUNT(*), SUM(valor_principal)
        FROM contas_receber 
        WHERE status = 'Recebido'
        AND vencimento LIKE ?
        AND (cliente LIKE ? OR cliente LIKE ?)
        GROUP BY cliente
    """, (f"%/{mes}/{ano}%", f"%{filtro_cliente}%", f"%{filtro_cliente.split()[0]}%"))
    
    similares = cur.fetchall()
    if len(similares) > 1:
        print(f"\n  🔍 Variações para '{filtro_cliente}':")
        for cliente, count, valor in similares:
            no_filtro = "✅" if cliente in clientes_filtro else "❌"
            print(f"    {no_filtro} {cliente:<45} | {count:>3} reg | R$ {valor:>12,.2f}")

print("\n" + "=" * 70)
print(f"📊 RESUMO:")
print(f"  • Total geral (todos): R$ {total_todos:,.2f}")
print(f"  • Total filtro atual: R$ {total_filtro:,.2f}")
print(f"  • Esperado pelo usuário: R$ 1.615.880,70")
print(f"  • Diferença: R$ {1615880.70 - total_filtro:,.2f}")
print("=" * 70)

conn.close()
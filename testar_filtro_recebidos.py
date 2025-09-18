#!/usr/bin/env python3
"""
Script para testar o filtro específico de contas a receber com clientes e status 'Recebido'
"""
import sqlite3
import os

# Conectar ao banco
db_path = 'financeiro.db'  # Banco na raiz
print(f"📍 Caminho absoluto do banco: {os.path.abspath(db_path)}")
if not os.path.exists(db_path):
    print(f"❌ Banco não encontrado em: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Lista específica de clientes
clientes_filtro = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

# Testar para agosto/2025
mes = "08"
ano = "2025"

print("🔍 Testando filtro de contas a receber:")
print(f"📅 Mês/Ano: {mes}/{ano}")
print(f"👥 Clientes: {len(clientes_filtro)} específicos")
print(f"📊 Status: Recebido")
print("-" * 60)

# 1. Verificar total geral no banco
cur.execute("SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) FROM contas_receber")
total_registros, total_valor = cur.fetchone()
print(f"📊 Total geral no banco: {total_registros:,} registros - R$ {total_valor:,.2f}")

# 2. Verificar por status 'Recebido'
cur.execute("SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) FROM contas_receber WHERE status = 'Recebido'")
recebidos_count, recebidos_valor = cur.fetchone()
print(f"✅ Total status 'Recebido': {recebidos_count:,} registros - R$ {recebidos_valor:,.2f}")

# 3. Verificar por mês/ano específico
cur.execute("SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) FROM contas_receber WHERE vencimento LIKE ?", (f"%/{mes}/{ano}%",))
mes_count, mes_valor = cur.fetchone()
print(f"📅 Total para {mes}/{ano}: {mes_count:,} registros - R$ {mes_valor:,.2f}")

# 4. Verificar por clientes específicos
placeholders = ','.join(['?' for _ in clientes_filtro])
cur.execute(f"SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) FROM contas_receber WHERE cliente IN ({placeholders})", tuple(clientes_filtro))
clientes_count, clientes_valor = cur.fetchone()
print(f"👥 Total clientes específicos: {clientes_count:,} registros - R$ {clientes_valor:,.2f}")

# 5. FILTRO COMPLETO (igual ao implementado)
cur.execute(f"""
    SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) 
    FROM contas_receber 
    WHERE status = 'Recebido'
    AND vencimento LIKE ?
    AND cliente IN ({placeholders})
""", (f"%/{mes}/{ano}%",) + tuple(clientes_filtro))
resultado = cur.fetchone()
count_final, valor_final = resultado

print("-" * 60)
print("🎯 RESULTADO FINAL (com todos os filtros):")
print(f"📊 Registros encontrados: {count_final:,}")
print(f"💰 Valor total: R$ {valor_final:,.2f}")

# 6. Mostrar alguns exemplos dos dados encontrados
if count_final > 0:
    print("\n📋 Exemplos dos registros encontrados:")
    cur.execute(f"""
        SELECT cliente, vencimento, valor_principal, status 
        FROM contas_receber 
        WHERE status = 'Recebido'
        AND vencimento LIKE ?
        AND cliente IN ({placeholders})
        LIMIT 5
    """, (f"%/{mes}/{ano}%",) + tuple(clientes_filtro))
    
    exemplos = cur.fetchall()
    for cliente, vencimento, valor, status in exemplos:
        print(f"  • {cliente} - {vencimento} - R$ {valor:,.2f} - {status}")

# 7. Verificar clientes únicos encontrados
cur.execute(f"""
    SELECT DISTINCT cliente, COUNT(*), SUM(valor_principal)
    FROM contas_receber 
    WHERE status = 'Recebido'
    AND vencimento LIKE ?
    AND cliente IN ({placeholders})
    GROUP BY cliente
    ORDER BY cliente
""", (f"%/{mes}/{ano}%",) + tuple(clientes_filtro))

clientes_unicos = cur.fetchall()
if clientes_unicos:
    print("\n👥 Clientes encontrados com o filtro:")
    for cliente, count, valor in clientes_unicos:
        print(f"  • {cliente}: {count:,} registros - R$ {valor:,.2f}")

conn.close()
print(f"\n✅ Teste concluído!")
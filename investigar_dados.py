#!/usr/bin/env python3
"""
Script para investigar os dados reais no banco
"""
import sqlite3
import os

# Conectar ao banco
db_path = 'financeiro.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("🔍 INVESTIGAÇÃO COMPLETA DOS DADOS")
print("=" * 60)

# 1. Verificar formatos de data
print("📅 FORMATOS DE DATA:")
cur.execute("SELECT DISTINCT vencimento FROM contas_receber LIMIT 10")
datas = cur.fetchall()
print(f"Exemplos de datas: {[d[0] for d in datas]}")

# 2. Verificar dados para agosto especificamente
print("\n📅 DADOS PARA AGOSTO 2025:")
cur.execute("SELECT COUNT(*) FROM contas_receber WHERE vencimento LIKE '%/08/2025%'")
agosto_count = cur.fetchone()[0]
print(f"Total registros com /08/2025: {agosto_count:,}")

# Se não tem com /08/2025, verificar outros formatos
if agosto_count == 0:
    cur.execute("SELECT COUNT(*) FROM contas_receber WHERE vencimento LIKE '%08/2025%'")
    agosto_alt = cur.fetchone()[0]
    print(f"Total registros com 08/2025: {agosto_alt:,}")
    
    cur.execute("SELECT COUNT(*) FROM contas_receber WHERE vencimento LIKE '%2025-08%'")
    agosto_iso = cur.fetchone()[0]
    print(f"Total registros com 2025-08: {agosto_iso:,}")

# 3. Verificar clientes específicos
clientes_filtro = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

print(f"\n👥 VERIFICANDO CLIENTES ESPECÍFICOS ({len(clientes_filtro)} clientes):")
for cliente in clientes_filtro:
    cur.execute("SELECT COUNT(*) FROM contas_receber WHERE cliente = ?", (cliente,))
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  ✅ {cliente}: {count:,} registros")
    else:
        # Tentar busca aproximada
        cur.execute("SELECT COUNT(*), cliente FROM contas_receber WHERE cliente LIKE ? GROUP BY cliente", (f"%{cliente}%",))
        similares = cur.fetchall()
        if similares:
            print(f"  ⚠️  {cliente}: 0 registros exatos, mas encontrou similares:")
            for count_sim, nome_sim in similares:
                print(f"      - {nome_sim}: {count_sim:,}")
        else:
            print(f"  ❌ {cliente}: 0 registros")

# 4. Verificar status 'Recebido'
print(f"\n📊 STATUS 'Recebido':")
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE status = 'Recebido'")
recebido_count, recebido_valor = cur.fetchone()
print(f"Total status 'Recebido': {recebido_count:,} registros - R$ {recebido_valor or 0:,.2f}")

# 5. Verificar alguns exemplos de registros recebidos
if recebido_count > 0:
    print(f"\n📋 EXEMPLOS DE REGISTROS 'Recebido':")
    cur.execute("SELECT cliente, vencimento, valor_principal FROM contas_receber WHERE status = 'Recebido' LIMIT 5")
    exemplos = cur.fetchall()
    for cliente, vencimento, valor in exemplos:
        print(f"  • {cliente} - {vencimento} - R$ {valor:,.2f}")

# 6. Verificar se existe MINERVA especificamente
print(f"\n🔍 MINERVA S A especificamente:")
cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE cliente = 'MINERVA S A'")
minerva_count, minerva_valor = cur.fetchone()
print(f"MINERVA S A exato: {minerva_count:,} registros - R$ {minerva_valor or 0:,.2f}")

if minerva_count > 0:
    # Verificar status da MINERVA
    cur.execute("SELECT DISTINCT status, COUNT(*) FROM contas_receber WHERE cliente = 'MINERVA S A' GROUP BY status")
    status_minerva = cur.fetchall()
    print(f"Status MINERVA S A: {dict(status_minerva)}")
    
    # Verificar datas MINERVA
    cur.execute("SELECT DISTINCT vencimento FROM contas_receber WHERE cliente = 'MINERVA S A' AND vencimento LIKE '%08/2025%' OR vencimento LIKE '%2025-08%'")
    datas_agosto = cur.fetchall()
    print(f"MINERVA S A em agosto/2025: {len(datas_agosto)} datas diferentes")

conn.close()
print(f"\n✅ Investigação concluída!")
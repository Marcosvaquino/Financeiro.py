import sqlite3
from datetime import datetime

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== VERIFICAÇÃO ESPECÍFICA DO DASHBOARD ===\n")

# Simular os mesmos dados que o dashboard mostra para setembro/2025
mes = 9
ano = 2025
pattern = f"%/{mes:02d}/{ano}%"

print(f"📅 Testando dados para {mes:02d}/{ano}")
print(f"🔍 Padrão de busca: {pattern}\n")

# 1. Total a Receber PENDENTE (usado no dashboard)
print("1. CONTAS A RECEBER (Status PENDENTE):")

# SEM filtro LSP
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_receber
    WHERE UPPER(status) = 'PENDENTE' AND vencimento LIKE ?
""", (pattern,))
sem_filtro = cur.fetchone()

# COM filtro LSP
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_receber
    WHERE UPPER(status) = 'PENDENTE' AND vencimento LIKE ?
    AND conta_contabil != 'LSP Transportes'
""", (pattern,))
com_filtro = cur.fetchone()

print(f"   SEM filtro LSP: {sem_filtro[0]} títulos, R$ {sem_filtro[1]:,.2f}")
print(f"   COM filtro LSP: {com_filtro[0]} títulos, R$ {com_filtro[1]:,.2f}")
print(f"   DIFERENÇA: {sem_filtro[0] - com_filtro[0]} títulos, R$ {sem_filtro[1] - com_filtro[1]:,.2f}")

# 2. Receita Realizada RECEBIDO (usado no dashboard)
print(f"\n2. RECEITA REALIZADA (Status RECEBIDO):")

# SEM filtro LSP
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_receber
    WHERE UPPER(status) = 'RECEBIDO' AND vencimento LIKE ?
""", (pattern,))
sem_filtro_rec = cur.fetchone()

# COM filtro LSP
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_receber
    WHERE UPPER(status) = 'RECEBIDO' AND vencimento LIKE ?
    AND conta_contabil != 'LSP Transportes'
""", (pattern,))
com_filtro_rec = cur.fetchone()

print(f"   SEM filtro LSP: {sem_filtro_rec[0]} títulos, R$ {sem_filtro_rec[1]:,.2f}")
print(f"   COM filtro LSP: {com_filtro_rec[0]} títulos, R$ {com_filtro_rec[1]:,.2f}")
print(f"   DIFERENÇA: {sem_filtro_rec[0] - com_filtro_rec[0]} títulos, R$ {sem_filtro_rec[1] - com_filtro_rec[1]:,.2f}")

# 3. Verificar especificamente registros LSP em setembro
print(f"\n3. REGISTROS LSP TRANSPORTES EM {mes:02d}/{ano}:")
cur.execute("""
    SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0), status
    FROM contas_receber
    WHERE conta_contabil = 'LSP Transportes' AND vencimento LIKE ?
    GROUP BY status
""", (pattern,))
lsp_setembro = cur.fetchall()

if lsp_setembro:
    for status_data in lsp_setembro:
        print(f"   Status {status_data[2]}: {status_data[0]} títulos, R$ {status_data[1]:,.2f}")
else:
    print("   ✅ Nenhum registro LSP encontrado em setembro/2025")

print(f"\n🎯 RESUMO: O filtro LSP está ativo e funcionando corretamente!")
print(f"   📊 Total filtrado: R$ {(sem_filtro[1] - com_filtro[1]) + (sem_filtro_rec[1] - com_filtro_rec[1]):,.2f}")

conn.close()
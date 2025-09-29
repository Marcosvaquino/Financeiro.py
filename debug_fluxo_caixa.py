import sqlite3
from datetime import datetime

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== DEBUG: FLUXO DE CAIXA - COMPARAÇÃO DE CÁLCULOS ===\n")

# Teste 1: Fluxo de Caixa Setembro (como no card principal)
mes_set = 9
ano = 2025
pattern_set = f"%/{mes_set:02d}/{ano}%"

print(f"📅 SETEMBRO 2025 (Card Principal):")
print(f"   Padrão: {pattern_set}")

# PROJEÇÃO - Receita Meta
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0)
    FROM projecao 
    WHERE mes = ? AND ano = ?
""", (mes_set, ano))
projecao_set = cur.fetchone()[0] or 0.0
print(f"   📊 Projeção (Meta): R$ {projecao_set:,.2f}")

# CONTAS A PAGAR - Status PENDENTE (com filtro REIS TRANSPORTES)
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_pagar
    WHERE status != 'PAGO' AND status != 'Pago'
    AND vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern_set,))
pagar_set = cur.fetchone()[0] or 0.0
print(f"   💸 A Pagar (filtrado): R$ {pagar_set:,.2f}")

fluxo_set = projecao_set - pagar_set
print(f"   💰 FLUXO SETEMBRO: R$ {fluxo_set:,.2f}")

print("\n" + "="*60)

# Teste 2: Fluxo de Caixa Agosto (como na Análise Comparativa)
mes_ago = 8
pattern_ago = f"%/{mes_ago:02d}/{ano}%"

print(f"📅 AGOSTO 2025 (Análise Comparativa):")
print(f"   Padrão: {pattern_ago}")

# PROJEÇÃO - Receita Meta
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) 
    FROM projecao
    WHERE mes = ? AND ano = ?
""", (mes_ago, ano))
projecao_ago = cur.fetchone()[0] or 0.0
print(f"   📊 Projeção (Meta): R$ {projecao_ago:,.2f}")

# CONTAS A PAGAR - Status PENDENTE (com filtro REIS TRANSPORTES)
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_pagar
    WHERE vencimento LIKE ? AND UPPER(status) = 'PENDENTE'
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern_ago,))
pagar_ago = cur.fetchone()[0] or 0.0
print(f"   💸 A Pagar (filtrado): R$ {pagar_ago:,.2f}")

fluxo_ago = projecao_ago - pagar_ago
print(f"   💰 FLUXO AGOSTO: R$ {fluxo_ago:,.2f}")

print("\n" + "="*60)

# Teste 3: Verificar diferenças nos status
print(f"🔍 ANÁLISE DE STATUS - CONTAS A PAGAR:")

for mes_teste, nome_mes in [(8, "AGOSTO"), (9, "SETEMBRO")]:
    pattern_teste = f"%/{mes_teste:02d}/{ano}%"
    print(f"\n   {nome_mes} 2025:")
    
    # Todos os status
    cur.execute("""
        SELECT status, COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_pagar
        WHERE vencimento LIKE ?
        AND fornecedor != 'REIS TRANSPORTES'
        GROUP BY status
        ORDER BY status
    """, (pattern_teste,))
    
    status_dados = cur.fetchall()
    total_mes = 0
    for status, count, valor in status_dados:
        print(f"     Status '{status}': {count} títulos, R$ {valor:,.2f}")
        if status.upper() in ['PENDENTE', 'PAGO']:
            if status.upper() == 'PENDENTE':
                total_mes += valor
    
    print(f"     TOTAL PENDENTE: R$ {total_mes:,.2f}")

print("\n" + "="*60)

# Teste 4: Verificar se há registros REIS TRANSPORTES sendo filtrados
print(f"🚫 REGISTROS REIS TRANSPORTES FILTRADOS:")

for mes_teste, nome_mes in [(8, "AGOSTO"), (9, "SETEMBRO")]:
    pattern_teste = f"%/{mes_teste:02d}/{ano}%"
    
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_pagar
        WHERE vencimento LIKE ?
        AND fornecedor = 'REIS TRANSPORTES'
    """, (pattern_teste,))
    
    reis_dados = cur.fetchone()
    print(f"   {nome_mes}: {reis_dados[0]} títulos, R$ {reis_dados[1] or 0:,.2f} filtrados")

conn.close()
print(f"\n🎯 CONCLUSÃO: Verificar qual cálculo está correto e ajustar o inconsistente.")
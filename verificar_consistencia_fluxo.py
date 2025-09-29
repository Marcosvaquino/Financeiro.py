import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== VERIFICAÇÃO DE CONSISTÊNCIA DO FLUXO DE CAIXA ===\n")

mes = 9
ano = 2025
pattern = f"%/{mes:02d}/{ano}%"

# 1. CÁLCULO DO CARD PRINCIPAL (setembro atual)
# Projeção atual
cur.execute("SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao WHERE mes = ? AND ano = ?", (mes, ano))
receita_meta = cur.fetchone()[0] or 0.0

# Contas a pagar (TODOS os status)
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_pagar
    WHERE vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern,))
pagar_total = cur.fetchone()[0] or 0.0

fluxo_card_principal = receita_meta - pagar_total

print(f"📊 CARD PRINCIPAL (Setembro {ano}):")
print(f"   🎯 Projeção: R$ {receita_meta:,.2f}")
print(f"   📤 A Pagar (TODOS): R$ {pagar_total:,.2f}")
print(f"   💳 Fluxo: R$ {fluxo_card_principal:,.2f}")

print(f"\n" + "="*50)

# 2. CÁLCULO DA ANÁLISE COMPARATIVA (próximos 3 meses)
meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

print(f"📈 ANÁLISE COMPARATIVA (próximos 3 meses):")
for i in range(1, 4):  # Próximos 3 meses
    mes_proj = mes + i
    ano_proj = ano
    if mes_proj > 12:
        mes_proj -= 12
        ano_proj += 1
    
    # Projeção
    cur.execute("SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao WHERE mes = ? AND ano = ?", (mes_proj, ano_proj))
    receita_projetada = cur.fetchone()[0] or 0.0
    
    # Contas a pagar (TODOS os status - agora igual ao card principal)
    cur.execute("""
        SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_pagar
        WHERE vencimento LIKE ?
        AND fornecedor != 'REIS TRANSPORTES'
    """, (f"%/{mes_proj:02d}/{ano_proj}%",))
    contas_a_pagar = cur.fetchone()[0] or 0.0
    
    fluxo_projetado = receita_projetada - contas_a_pagar
    
    print(f"   {meses_nomes[mes_proj-1]}/{ano_proj}: Projeção R$ {receita_projetada:,.2f} - Pagar R$ {contas_a_pagar:,.2f} = R$ {fluxo_projetado:,.2f}")

# Teste específico para setembro (que está aparecendo errado)
print(f"\n🔍 TESTE ESPECÍFICO - SETEMBRO:")
# Setembro como próximo mês (seria outubro agora que estamos em setembro)
mes_test = 9
ano_test = 2025

cur.execute("SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao WHERE mes = ? AND ano = ?", (mes_test, ano_test))
proj_set = cur.fetchone()[0] or 0.0

cur.execute("""
    SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
    FROM contas_pagar
    WHERE vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (f"%/{mes_test:02d}/{ano_test}%",))
pagar_set = cur.fetchone()[0] or 0.0

fluxo_set = proj_set - pagar_set
print(f"   Set/2025: Projeção R$ {proj_set:,.2f} - Pagar R$ {pagar_set:,.2f} = R$ {fluxo_set:,.2f}")

print(f"\n✅ CONSISTÊNCIA: Card Principal e Análise Comparativa devem ter valores iguais!")

conn.close()
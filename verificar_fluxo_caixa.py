import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== VERIFICAÇÃO DOS CÁLCULOS DO FLUXO DE CAIXA ===\n")

mes = 9
ano = 2025
pattern = f"%/{mes:02d}/{ano}%"

print(f"📅 Verificando setembro/{ano}")

# 1. Receita Realizada (Recebida) - igual ao card Receita
print("\n1. RECEITA REALIZADA (RECEBIDA):")

# Lista dos 19 clientes principais
clientes_19 = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI',
    'VALENCIO JATAI', 'VALENCIO MATRIZ'
]

# Função para verificar se cliente pertence aos 19
def cliente_pertence_aos_19(cliente_banco):
    if not cliente_banco:
        return False
    
    cliente_upper = cliente_banco.upper().strip()
    for cliente_permitido in clientes_19:
        cliente_permitido_upper = cliente_permitido.upper().strip()
        if (cliente_permitido_upper in cliente_upper or 
            cliente_upper in cliente_permitido_upper or
            cliente_upper == cliente_permitido_upper):
            return True
    return False

# Buscar todos os registros RECEBIDOS dos 19 clientes com filtro LSP
cur.execute("""
    SELECT cliente, valor_principal
    FROM contas_receber
    WHERE UPPER(status) = 'RECEBIDO' AND vencimento LIKE ?
    AND conta_contabil != 'LSP Transportes'
""", (pattern,))

registros_recebidos = cur.fetchall()
receita_realizada = 0.0
count_receita = 0

for cliente_banco, valor in registros_recebidos:
    if cliente_pertence_aos_19(cliente_banco):
        receita_realizada += float(valor)
        count_receita += 1

print(f"   Receita Realizada: R$ {receita_realizada:,.2f} ({count_receita} títulos)")

# 2. Contas a Pagar Total
print("\n2. CONTAS A PAGAR:")
cur.execute("""
    SELECT 
        COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0),
        COUNT(*)
    FROM contas_pagar
    WHERE status != 'PAGO' AND status != 'Pago'
    AND vencimento LIKE ?
    AND fornecedor != 'REIS TRANSPORTES'
""", (pattern,))

pagar_dados = cur.fetchone()
total_pagar = pagar_dados[0] or 0.0
count_pagar = pagar_dados[1] or 0

print(f"   Contas a Pagar: R$ {total_pagar:,.2f} ({count_pagar} títulos)")

# 3. Fluxo de Caixa Calculado
fluxo_caixa = receita_realizada - total_pagar
print(f"\n3. FLUXO DE CAIXA:")
print(f"   Recebido - Pagar = R$ {receita_realizada:,.2f} - R$ {total_pagar:,.2f}")
print(f"   Resultado: R$ {fluxo_caixa:,.2f}")
print(f"   Status: {'Positivo' if fluxo_caixa >= 0 else 'Negativo'}")

# 4. Meta da Projeção para o fluxo projetado
cur.execute("""
    SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0)
    FROM projecao 
    WHERE mes = ? AND ano = ?
""", (mes, ano))
receita_meta = cur.fetchone()[0] or 0.0

fluxo_projetado = receita_meta - total_pagar
print(f"\n4. FLUXO DE CAIXA PROJETADO:")
print(f"   Projeção - Pagar = R$ {receita_meta:,.2f} - R$ {total_pagar:,.2f}")
print(f"   Resultado: R$ {fluxo_projetado:,.2f}")
print(f"   Status: {'Positivo' if fluxo_projetado >= 0 else 'Negativo'}")

print(f"\n🎯 RESUMO:")
print(f"   📊 Card Receita deve mostrar: R$ {receita_realizada:,.2f}")
print(f"   💧 Fluxo Normal deve mostrar: R$ {fluxo_caixa:,.2f} (Recebido - Pagar)")
print(f"   🔮 Fluxo Projetado deve mostrar: R$ {fluxo_projetado:,.2f} (Projeção - Pagar)")

conn.close()
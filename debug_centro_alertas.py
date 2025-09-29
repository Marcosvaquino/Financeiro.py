import sqlite3
from datetime import datetime
import unicodedata

def normalizar_nome_cliente(nome):
    if not nome:
        return ""
    nome = str(nome).upper().strip()
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(c for c in nome if unicodedata.category(c) != 'Mn')
    nome = nome.replace('  ', ' ')
    return nome

def eh_cliente_principal(cliente_nome):
    CLIENTES_19_PRINCIPAIS = [
        'LUIZ ANDRE VALENCIO',
        'ANTONIO LOPES DA SILVA NETO',
        'SONEPAR BRASIL LTDA',
        'DECOR ENGENHARIA E EMPREENDIMENTOS EIRELI',
        'ADRIANA VALENCIO',
        'CONDOMINIO RESIDENCIAL VIVENDAS DA SERRA',
        'CONDOMINIO GRAN RESERVA PARQUE',
        'CONDOMINIO BOULEVARD RESIDENCE',
        'JULIANA ANDRADE PAMPLONA',
        'JULIANA ANDRADE PAMPLONA EIRELI',
        'CONDOMINIO PARQUE RESIDENCIAL DAS FLORES',
        'CONDOMINIO RESIDENCIAL VALE VERDE',
        'CONDOMINIO MORADAS DE ITAICI II',
        'CONDOMINIO RESERVA DA MATA',
        'CONDOMINIO RESIDENCIAL PORTAL DOS IPES',
        'CONDOMINIO BELA VISTA ITAICI',
        'DIRECIONAL ENGENHARIA S/A',
        'RICARDO ANDRADE PAMPLONA',
        'CONDOMINIO QUINTA DA BARONESA'
    ]
    
    cliente_normalizado = normalizar_nome_cliente(cliente_nome)
    
    for cliente_principal in CLIENTES_19_PRINCIPAIS:
        if normalizar_nome_cliente(cliente_principal) == cliente_normalizado:
            return True
    return False

def analisar_centro_alertas():
    conn = sqlite3.connect('financeiro.db')
    cur = conn.cursor()
    
    agora = datetime.now()
    mes = agora.month
    ano = agora.year
    
    pattern = f"%/{mes:02d}/{ano}%"
    
    print("=" * 70)
    print(f"🚨 ANÁLISE DO CENTRO DE ALERTAS - {mes:02d}/{ano}")
    print("=" * 70)
    
    print(f"\n🔍 FILTRO APLICADO: {pattern}")
    print(f"📅 Data atual: {agora.strftime('%d/%m/%Y')}")
    
    # ===== 1. CONTAS A RECEBER VENCIDAS =====
    print(f"\n📋 1. CONTAS A RECEBER VENCIDAS (19 CLIENTES)")
    print("-" * 50)
    
    cur.execute("""
        SELECT 
            cliente, valor_principal, vencimento, status
        FROM contas_receber
        WHERE UPPER(status) = 'PENDENTE'
        AND vencimento LIKE ?
        AND LENGTH(vencimento) = 10
        AND DATE(SUBSTR(vencimento, 7, 4) || '-' || SUBSTR(vencimento, 4, 2) || '-' || SUBSTR(vencimento, 1, 2)) < DATE('now')
        ORDER BY vencimento
    """, (pattern,))
    
    contas_vencidas = cur.fetchall()
    
    # Filtrar apenas os 19 clientes principais
    contas_vencidas_19 = []
    total_vencidas_19 = 0
    
    for conta in contas_vencidas:
        if eh_cliente_principal(conta[0]):
            contas_vencidas_19.append(conta)
            total_vencidas_19 += float(conta[1])
    
    print(f"Total de contas vencidas (geral): {len(contas_vencidas)}")
    print(f"Contas vencidas (19 clientes): {len(contas_vencidas_19)}")
    print(f"Valor total vencido (19 clientes): R$ {total_vencidas_19:,.2f}")
    
    print(f"\n🔝 Top 5 contas vencidas (19 clientes):")
    for i, conta in enumerate(sorted(contas_vencidas_19, key=lambda x: float(x[1]), reverse=True)[:5]):
        print(f"  {i+1}. {conta[0]}: R$ {float(conta[1]):,.2f} (venc: {conta[2]})")
    
    # ===== 2. CONTAS A PAGAR VENCIDAS =====
    print(f"\n💳 2. CONTAS A PAGAR VENCIDAS")
    print("-" * 50)
    
    cur.execute("""
        SELECT 
            fornecedor, valor_principal, vencimento, status
        FROM contas_pagar
        WHERE status != 'PAGO' AND status != 'Pago'
        AND vencimento LIKE ?
        AND LENGTH(vencimento) = 10
        AND DATE(SUBSTR(vencimento, 7, 4) || '-' || SUBSTR(vencimento, 4, 2) || '-' || SUBSTR(vencimento, 1, 2)) < DATE('now')
        ORDER BY vencimento
    """, (pattern,))
    
    pagar_vencidas = cur.fetchall()
    total_pagar_vencidas = sum(float(conta[1]) for conta in pagar_vencidas)
    
    print(f"Contas a pagar vencidas: {len(pagar_vencidas)}")
    print(f"Valor total: R$ {total_pagar_vencidas:,.2f}")
    
    print(f"\n🔝 Top 5 contas a pagar vencidas:")
    for i, conta in enumerate(sorted(pagar_vencidas, key=lambda x: float(x[1]), reverse=True)[:5]):
        print(f"  {i+1}. {conta[0]}: R$ {float(conta[1]):,.2f} (venc: {conta[2]})")
    
    # ===== 3. TIPOS DE ALERTAS DISPONÍVEIS =====
    print(f"\n⚠️ 3. TIPOS DE ALERTAS DISPONÍVEIS NO SISTEMA")
    print("-" * 50)
    
    alertas_tipos = [
        "1. Contas a receber vencidas (19 clientes principais)",
        "2. Contas a pagar vencidas (todos os fornecedores)", 
        "3. Meta do mês baixa (< 50% atingida)",
        "4. Fluxo de caixa negativo",
        "5. Alta inadimplência (> 5% dos títulos vencidos)",
        "6. Queda na receita (> 10% vs mês anterior)",
        "7. Fluxo de caixa negativo projetado (múltiplos meses)",
        "8. Nenhum alerta (quando tudo está ok)"
    ]
    
    for alerta in alertas_tipos:
        print(f"  {alerta}")
    
    # ===== 4. ALERTAS ATIVOS AGORA =====
    print(f"\n🔥 4. ALERTAS ATIVOS PARA {mes:02d}/{ano}")
    print("-" * 50)
    
    alertas_ativos = []
    
    if len(contas_vencidas_19) > 0:
        alertas_ativos.append(f"{len(contas_vencidas_19)} conta(s) a receber vencida(s) - R$ {total_vencidas_19:,.0f}")
    
    if len(pagar_vencidas) > 0:
        alertas_ativos.append(f"{len(pagar_vencidas)} conta(s) a pagar vencida(s) - R$ {total_pagar_vencidas:,.0f}")
    
    # Verificar meta (usando dados da análise anterior)
    cur.execute("SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao WHERE mes = ? AND ano = ?", (mes, ano))
    meta = cur.fetchone()[0] or 0.0
    
    # Receita realizada (19 clientes)
    cur.execute("""
        SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_receber 
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
    """, (pattern,))
    receita_geral = cur.fetchone()[0] or 0.0
    
    # Filtrar por 19 clientes (precisaria refazer a query com filtro)
    percentual_meta = (receita_geral / meta * 100) if meta > 0 else 0
    
    if percentual_meta < 50:
        alertas_ativos.append(f"Meta do mês: apenas {percentual_meta:.1f}% atingida")
    
    if not alertas_ativos:
        alertas_ativos.append("Nenhum alerta crítico no momento")
    
    print(f"📊 Total de alertas ativos: {len(alertas_ativos)}")
    for i, alerta in enumerate(alertas_ativos, 1):
        print(f"  {i}. {alerta}")
    
    print("\n" + "=" * 70)
    
    conn.close()

if __name__ == "__main__":
    analisar_centro_alertas()
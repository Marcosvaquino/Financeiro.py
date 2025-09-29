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

def analisar_performance():
    conn = sqlite3.connect('financeiro.db')
    cur = conn.cursor()
    
    agora = datetime.now()
    mes = agora.month
    ano = agora.year
    
    pattern = f"%/{mes:02d}/{ano}%"
    
    print("=" * 60)
    print(f"📊 ANÁLISE DO CARD PERFORMANCE - {mes:02d}/{ano}")
    print("=" * 60)
    
    # 1. META ATINGIDA
    print("\n🎯 1. META ATINGIDA")
    print("-" * 30)
    
    # Meta (dados da projeção)
    cur.execute("SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao WHERE mes = ? AND ano = ?", (mes, ano))
    receita_meta = cur.fetchone()[0] or 0.0
    
    # Receita realizada (19 clientes principais, status RECEBIDO)
    cur.execute("""
        SELECT cliente, valor_principal, status 
        FROM contas_receber 
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
    """, (pattern,))
    
    receita_realizada = 0
    clientes_recebido = []
    
    for row in cur.fetchall():
        if eh_cliente_principal(row[0]):
            receita_realizada += float(row[1])
            clientes_recebido.append((row[0], float(row[1])))
    
    percentual_meta = (receita_realizada / receita_meta * 100) if receita_meta > 0 else 0
    
    print(f"Meta (Projeção): R$ {receita_meta:,.2f}")
    print(f"Realizado: R$ {receita_realizada:,.2f}")
    print(f"Percentual: {percentual_meta:.1f}%")
    
    # Top clientes que contribuíram
    print(f"\nTop 5 clientes recebidos:")
    for cliente, valor in sorted(clientes_recebido, key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {cliente}: R$ {valor:,.2f}")
    
    # 2. INADIMPLÊNCIA
    print("\n⚠️ 2. INADIMPLÊNCIA")
    print("-" * 30)
    
    # Total de títulos
    cur.execute("SELECT COUNT(*) FROM contas_receber WHERE vencimento LIKE ?", (pattern,))
    count_receber = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(*) FROM contas_pagar WHERE vencimento LIKE ?", (pattern,))
    count_pagar = cur.fetchone()[0] or 0
    
    total_titulos = count_receber + count_pagar
    
    # Títulos vencidos
    cur.execute("""
        SELECT COUNT(*) FROM contas_receber 
        WHERE vencimento LIKE ? AND UPPER(status) = 'PENDENTE'
        AND DATE(substr(vencimento, 7, 4) || '-' || substr(vencimento, 4, 2) || '-' || substr(vencimento, 1, 2)) < DATE('now')
    """, (pattern,))
    count_receber_vencidas = cur.fetchone()[0] or 0
    
    cur.execute("""
        SELECT COUNT(*) FROM contas_pagar 
        WHERE vencimento LIKE ? AND UPPER(status) = 'PENDENTE'
        AND DATE(substr(vencimento, 7, 4) || '-' || substr(vencimento, 4, 2) || '-' || substr(vencimento, 1, 2)) < DATE('now')
    """, (pattern,))
    count_pagar_vencidas = cur.fetchone()[0] or 0
    
    titulos_vencidos = count_receber_vencidas + count_pagar_vencidas
    percentual_inadimplencia = (titulos_vencidos / total_titulos * 100) if total_titulos > 0 else 0
    
    print(f"Total de títulos: {total_titulos}")
    print(f"Títulos vencidos: {titulos_vencidos}")
    print(f"Percentual inadimplência: {percentual_inadimplencia:.1f}%")
    
    # Status da inadimplência
    if percentual_inadimplencia > 5:
        status_inadim = "🔴 ALTA (Crítico)"
    elif percentual_inadimplencia > 2:
        status_inadim = "🟡 MODERADA (Atenção)"
    else:
        status_inadim = "🟢 BAIXA (Bom)"
    
    print(f"Status: {status_inadim}")
    
    # 3. TICKET MÉDIO
    print("\n💰 3. TICKET MÉDIO")
    print("-" * 30)
    
    # Número de transações (19 clientes principais, RECEBIDO)
    cur.execute("""
        SELECT COUNT(*) FROM contas_receber 
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
    """, (pattern,))
    
    total_transacoes_raw = cur.fetchone()[0] or 0
    
    # Filtrar por 19 clientes
    total_transacoes = len(clientes_recebido)  # Já filtrado acima
    
    ticket_medio = receita_realizada / total_transacoes if total_transacoes > 0 else 0
    
    print(f"Total de transações (19 clientes): {total_transacoes}")
    print(f"Receita total (19 clientes): R$ {receita_realizada:,.2f}")
    print(f"Ticket médio: R$ {ticket_medio:,.2f}")
    
    # 4. RESUMO GERAL
    print("\n📋 4. RESUMO - O QUE O CARD PERFORMANCE MOSTRA")
    print("-" * 50)
    print(f"✓ Meta Atingida: {percentual_meta:.1f}%")
    print(f"✓ Inadimplência: {percentual_inadimplencia:.1f}% ({status_inadim.split(' ')[1]})")
    print(f"✓ Ticket Médio: R$ {ticket_medio:,.2f}")
    
    print("\n" + "=" * 60)
    
    conn.close()

if __name__ == "__main__":
    analisar_performance()
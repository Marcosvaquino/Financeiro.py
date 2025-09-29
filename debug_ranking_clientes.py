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

def criar_condicao_clientes_principais():
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
    
    condicoes = []
    parametros = []
    
    for cliente in CLIENTES_19_PRINCIPAIS:
        cliente_normalizado = normalizar_nome_cliente(cliente)
        condicoes.append("UPPER(REPLACE(REPLACE(cliente, '  ', ' '), CHAR(160), ' ')) LIKE ?")
        parametros.append(f"%{cliente_normalizado}%")
    
    return f"({' OR '.join(condicoes)})", parametros

def analisar_ranking_clientes():
    conn = sqlite3.connect('financeiro.db')
    cur = conn.cursor()
    
    agora = datetime.now()
    mes = agora.month
    ano = agora.year
    
    pattern = f"%/{mes:02d}/{ano}%"
    
    print("=" * 70)
    print(f"🏆 ANÁLISE DO RANKING DE CLIENTES - {mes:02d}/{ano}")
    print("=" * 70)
    
    print(f"\n🔍 FILTRO APLICADO: {pattern}")
    
    # ===== 1. RANKING ATUAL (ANTES DA CORREÇÃO) =====
    print(f"\n📊 1. RANKING ATUAL - TODOS OS CLIENTES (TOP 10)")
    print("-" * 50)
    
    cur.execute("""
        SELECT 
            cliente,
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0) as total,
            COUNT(*) as qtd_transacoes
        FROM contas_receber
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
        GROUP BY cliente
        ORDER BY total DESC
        LIMIT 10
    """, (pattern,))
    
    ranking_geral = cur.fetchall()
    
    total_geral_recebido = sum(row[1] for row in ranking_geral)
    
    for i, (cliente, valor, qtd) in enumerate(ranking_geral, 1):
        percentual = (valor / total_geral_recebido * 100) if total_geral_recebido > 0 else 0
        eh_principal = "✅" if eh_cliente_principal(cliente) else "❌"
        print(f"  #{i} {eh_principal} {cliente}")
        print(f"      R$ {valor:,.2f} ({percentual:.1f}% do total) - {qtd} transações")
    
    # ===== 2. RANKING CORRIGIDO (19 CLIENTES PRINCIPAIS) =====
    print(f"\n🎯 2. RANKING CORRIGIDO - 19 CLIENTES PRINCIPAIS (TOP 10)")
    print("-" * 60)
    
    condicao_clientes, clientes_params = criar_condicao_clientes_principais()
    
    cur.execute(f"""
        SELECT 
            cliente,
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0) as total,
            COALESCE(SUM(CASE WHEN UPPER(status) = 'RECEBIDO' THEN CAST(valor_principal AS REAL) ELSE 0 END), 0.0) as recebido,
            COALESCE(SUM(CASE WHEN UPPER(status) = 'PENDENTE' THEN CAST(valor_principal AS REAL) ELSE 0 END), 0.0) as pendente,
            COUNT(*) as qtd_transacoes
        FROM contas_receber
        WHERE vencimento LIKE ?
        AND {condicao_clientes}
        GROUP BY cliente
        ORDER BY total DESC
        LIMIT 10
    """, [pattern] + clientes_params)
    
    ranking_19_clientes = cur.fetchall()
    
    if not ranking_19_clientes:
        print("  ⚠️  Nenhum cliente dos 19 principais no período")
    else:
        total_19_geral = sum(row[1] for row in ranking_19_clientes)
        
        for i, (cliente, total, recebido, pendente, qtd) in enumerate(ranking_19_clientes, 1):
            percentual = (total / total_19_geral * 100) if total_19_geral > 0 else 0
            print(f"  #{i} {cliente}")
            print(f"      Total: R$ {total:,.2f} ({percentual:.1f}%) - {qtd} transações")
            print(f"      Recebido: R$ {recebido:,.2f} | Pendente: R$ {pendente:,.2f}")
        
        print(f"\n📈 RESUMO:")
        print(f"  Total geral (19 clientes): R$ {total_19_geral:,.2f}")
        print(f"  Total recebido: R$ {sum(row[2] for row in ranking_19_clientes):,.2f}")
        print(f"  Total pendente: R$ {sum(row[3] for row in ranking_19_clientes):,.2f}")
        print(f"  Clientes ativos no ranking: {len(ranking_19_clientes)}")
    
    # ===== 3. COMPARAÇÃO =====
    print(f"\n⚖️ 3. COMPARAÇÃO")
    print("-" * 30)
    
    clientes_principais_no_geral = sum(1 for cliente, _, _ in ranking_geral if eh_cliente_principal(cliente))
    
    print(f"  Ranking Geral:")
    print(f"    - Total de clientes: {len(ranking_geral)}")
    print(f"    - Clientes principais presentes: {clientes_principais_no_geral}")
    print(f"    - Total recebido: R$ {total_geral_recebido:,.2f}")
    
    print(f"  Ranking 19 Clientes:")
    print(f"    - Total de clientes: {len(ranking_19_clientes)}")
    print(f"    - Total recebido: R$ {sum(row[1] for row in ranking_19_clientes):,.2f}")
    
    print("\n" + "=" * 70)
    
    conn.close()

if __name__ == "__main__":
    analisar_ranking_clientes()
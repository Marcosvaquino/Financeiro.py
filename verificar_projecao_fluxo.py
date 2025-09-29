import sqlite3
from datetime import datetime

def verificar_dados_projecao():
    conn = sqlite3.connect('financeiro.db')
    cur = conn.cursor()
    
    # Data atual para calcular próximos 3 meses
    agora = datetime.now()
    mes_atual = agora.month
    ano_atual = agora.year
    
    print(f"Data atual: {mes_atual}/{ano_atual}")
    print("=" * 50)
    
    # Verificar projeções dos próximos 3 meses
    for i in range(1, 4):
        mes_proj = mes_atual + i
        ano_proj = ano_atual
        if mes_proj > 12:
            mes_proj -= 12
            ano_proj += 1
        
        print(f"\n--- MÊS {mes_proj}/{ano_proj} ---")
        
        # Dados de projeção (sem filtro de clientes - todos os clientes da tabela projeção)
        cur.execute("""
            SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0), COUNT(*)
            FROM projecao
            WHERE mes = ? AND ano = ?
        """, (mes_proj, ano_proj))
        resultado_proj = cur.fetchone()
        receita_projetada = resultado_proj[0] or 0.0
        qtd_projecao = resultado_proj[1] or 0
        
        # Contas a pagar
        cur.execute("""
            SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0), COUNT(*)
            FROM contas_pagar
            WHERE vencimento LIKE ? AND UPPER(status) = 'PENDENTE'
        """, (f"%/{mes_proj:02d}/{ano_proj}%",))
        resultado_pagar = cur.fetchone()
        contas_a_pagar = resultado_pagar[0] or 0.0
        qtd_a_pagar = resultado_pagar[1] or 0
        
        fluxo = receita_projetada - contas_a_pagar
        
        print(f"Projeção: R$ {receita_projetada:,.2f} ({qtd_projecao} registros)")
        print(f"A Pagar: R$ {contas_a_pagar:,.2f} ({qtd_a_pagar} registros)")
        print(f"Fluxo (Projeção - A Pagar): R$ {fluxo:,.2f}")
    
    # Verificar também todos os dados de projeção disponíveis
    print("\n" + "=" * 50)
    print("RESUMO GERAL DE PROJEÇÕES:")
    cur.execute("""
        SELECT mes, ano, COUNT(*), SUM(valor)
        FROM projecao
        WHERE ano >= 2025
        GROUP BY mes, ano
        ORDER BY ano, mes
    """)
    
    for row in cur.fetchall():
        print(f"Mês {row[0]:02d}/{row[1]}: {row[2]} registros, Total: R$ {row[3]:,.2f}")
    
    conn.close()

if __name__ == "__main__":
    verificar_dados_projecao()
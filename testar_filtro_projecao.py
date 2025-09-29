import sqlite3

def testar_filtro_projecao():
    conn = sqlite3.connect('financeiro.db')
    cur = conn.cursor()
    
    # Verificar os clientes na tabela projeção
    print("=== CLIENTES NA TABELA PROJEÇÃO ===")
    cur.execute("SELECT DISTINCT cliente FROM projecao ORDER BY cliente")
    clientes_projecao = [row[0] for row in cur.fetchall()]
    print(f"Total de clientes únicos: {len(clientes_projecao)}")
    
    for cliente in clientes_projecao[:10]:  # Primeiros 10
        print(f"- {cliente}")
    
    if len(clientes_projecao) > 10:
        print(f"... e mais {len(clientes_projecao) - 10} clientes")
    
    # Verificar outubro especificamente
    print(f"\n=== DADOS OUTUBRO 2025 ===")
    cur.execute("""
        SELECT cliente, SUM(valor), COUNT(*)
        FROM projecao 
        WHERE mes = 10 AND ano = 2025 
        GROUP BY cliente 
        ORDER BY SUM(valor) DESC
    """)
    
    total_outubro = 0
    for i, row in enumerate(cur.fetchall()):
        if i < 10:  # Primeiros 10
            print(f"{row[0]}: R$ {row[1]:,.2f} ({row[2]} registros)")
        total_outubro += row[1]
    
    print(f"Total outubro: R$ {total_outubro:,.2f}")
    
    # Lista dos 19 clientes principais
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
    
    print(f"\n=== FILTRO DOS 19 CLIENTES PRINCIPAIS ===")
    
    # Teste com normalização
    import unicodedata
    
    def normalizar_nome_cliente(nome):
        if not nome:
            return ""
        nome = str(nome).upper().strip()
        nome = unicodedata.normalize('NFD', nome)
        nome = ''.join(c for c in nome if unicodedata.category(c) != 'Mn')
        nome = nome.replace('  ', ' ')
        return nome
    
    clientes_normalizados = [normalizar_nome_cliente(c) for c in CLIENTES_19_PRINCIPAIS]
    
    # Verificar correspondências
    matches = 0
    total_valor_filtrado = 0
    
    cur.execute("SELECT cliente, SUM(valor) FROM projecao WHERE mes = 10 AND ano = 2025 GROUP BY cliente")
    for row in cur.fetchall():
        cliente_normalizado = normalizar_nome_cliente(row[0])
        if any(normalizar_nome_cliente(cp) == cliente_normalizado for cp in CLIENTES_19_PRINCIPAIS):
            matches += 1
            total_valor_filtrado += row[1]
            print(f"✓ {row[0]}: R$ {row[1]:,.2f}")
    
    print(f"\nMatches encontrados: {matches}")
    print(f"Total filtrado: R$ {total_valor_filtrado:,.2f}")
    
    conn.close()

if __name__ == "__main__":
    testar_filtro_projecao()
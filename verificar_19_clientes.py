import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

# Lista dos 19 clientes da projeção
clientes_projecao = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 
    'FRIBOI', 'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 
    'JK DISTRIBUIDORA', 'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 
    'MARFRIG - PROMISSAO', 'MARFRIG GLOBAL FOODS S A', 'MINERVA S A',
    'PAMPLONA JANDIRA', 'PEIXES MEGGS PESCADOS LTDA - SJBV', 
    'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
]

print('🎯 VERIFICAÇÃO DOS 19 CLIENTES DA PROJEÇÃO:')
print('=' * 60)

total_valor_19_clientes = 0
clientes_encontrados = 0

for i, cliente in enumerate(clientes_projecao, 1):
    # Busca exata
    cur.execute('SELECT COUNT(*), COALESCE(SUM(valor_titulo), 0) FROM contas_receber WHERE cliente = ?', (cliente,))
    count_exato, valor_exato = cur.fetchone()
    
    # Busca com LIKE para encontrar variações (com espaços extras, etc.)
    cur.execute('SELECT COUNT(*), COALESCE(SUM(valor_titulo), 0) FROM contas_receber WHERE TRIM(cliente) LIKE ?', (f'%{cliente}%',))
    count_like, valor_like = cur.fetchone()
    
    if count_exato > 0:
        clientes_encontrados += 1
        total_valor_19_clientes += valor_exato or 0
        print(f'{i:2d}. ✅ {cliente}: {count_exato:,} registros, R$ {valor_exato:,.2f}')
    elif count_like > 0:
        clientes_encontrados += 1
        total_valor_19_clientes += valor_like or 0
        print(f'{i:2d}. ⚠️  {cliente}: {count_like:,} registros (variação), R$ {valor_like:,.2f}')
        # Mostra o nome real encontrado
        cur.execute('SELECT DISTINCT cliente FROM contas_receber WHERE TRIM(cliente) LIKE ?', (f'%{cliente}%',))
        nomes_reais = [row[0] for row in cur.fetchall()]
        for nome_real in nomes_reais:
            print(f'    -> "{nome_real}"')
    else:
        print(f'{i:2d}. ❌ {cliente}: Sem dados')

print(f'\n📊 RESUMO:')
print(f'Clientes com dados: {clientes_encontrados}/19')
print(f'💰 Valor total dos 19 clientes: R$ {total_valor_19_clientes:,.2f}')

# Verificar o total geral para comparação
cur.execute('SELECT SUM(valor_titulo) FROM contas_receber')
total_geral = cur.fetchone()[0] or 0
print(f'💰 Valor total geral: R$ {total_geral:,.2f}')

percentual = (total_valor_19_clientes / total_geral * 100) if total_geral > 0 else 0
print(f'📈 Os 19 clientes representam {percentual:.1f}% do total')

conn.close()
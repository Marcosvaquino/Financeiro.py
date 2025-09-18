import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Meses com dados recebidos ===")
cur.execute("""
    SELECT strftime('%m', vencimento) as mes, strftime('%Y', vencimento) as ano, 
           COUNT(*) as total_registros, SUM(valor_principal) as total_valor
    FROM contas_receber 
    WHERE status = 'Recebido'
    GROUP BY mes, ano
    ORDER BY ano, mes
""")

meses_dados = cur.fetchall()
for row in meses_dados:
    print(f"  {row[0]}/{row[1]}: {row[2]} registros, R$ {row[3]:.2f}")

print("\n=== Clientes com recebidos nos meses disponíveis ===")
# Vamos verificar os clientes da projeção nos meses que têm dados
clientes_projecao = ['ADORO FOODS', 'MARFRIG GLOBAL FOODS', 'GOLDPAC CD SAO JOSE DOS CAMPOS', 
                    'GFOODS BARUERI', 'LATICINIO CARMONA', 'MINERVA S A', 'PAMPLONA JANDIRA', 
                    'SANTA LUCIA', 'SAUDALI', 'VALENCIA JATAI']

for mes, ano, _, _ in meses_dados:
    if ano == '2025':  # Foca apenas em 2025
        print(f"\n--- Mês {mes}/{ano} ---")
        total_mes = 0
        count_mes = 0
        
        for cliente_proj in clientes_projecao:
            palavras = cliente_proj.split()
            if len(palavras) >= 1:
                palavra1 = palavras[0]
                palavra2 = palavras[1] if len(palavras) > 1 else palavras[0]
                
                cur.execute("""
                    SELECT COALESCE(SUM(valor_principal), 0), COUNT(*) 
                    FROM contas_receber 
                    WHERE status = 'Recebido' 
                    AND strftime('%m', vencimento) = ?
                    AND strftime('%Y', vencimento) = ?
                    AND (UPPER(cliente) LIKE ? OR UPPER(cliente) LIKE ?)
                """, (mes, ano, f"%{palavra1}%", f"%{palavra2}%"))
                
                resultado = cur.fetchone()
                if resultado[0] > 0:
                    print(f"    {cliente_proj}: R$ {resultado[0]:.2f} ({resultado[1]} registros)")
                    total_mes += resultado[0]
                    count_mes += resultado[1]
        
        print(f"  Total do mês: R$ {total_mes:.2f} ({count_mes} registros)")

conn.close()
import sqlite3

conn = sqlite3.connect('financeiro.db')
cur = conn.cursor()

print("=== Análise de compatibilidade entre clientes ===")

# Pega todos os clientes únicos da projeção para agosto 2025
cur.execute('SELECT DISTINCT cliente FROM projecao WHERE mes = 8 AND ano = 2025')
clientes_projecao = [row[0] for row in cur.fetchall()]

# Pega todos os clientes únicos de contas_receber com recebidos em agosto 2025
cur.execute("SELECT DISTINCT cliente FROM contas_receber WHERE status = 'Recebido' AND strftime('%m', vencimento) = '08' AND strftime('%Y', vencimento) = '2025'")
clientes_recebidos = [row[0] for row in cur.fetchall()]

print(f"Clientes na projeção para 08/2025: {len(clientes_projecao)}")
for cliente in clientes_projecao:
    print(f"  - {cliente}")

print(f"\nClientes com valores recebidos em 08/2025: {len(clientes_recebidos)}")
for cliente in clientes_recebidos:
    print(f"  - {cliente}")

print("\n=== Tentando encontrar correspondências aproximadas ===")
# Tenta encontrar correspondências usando LIKE
correspondencias = []
for cliente_proj in clientes_projecao:
    palavras = cliente_proj.split()
    for cliente_rec in clientes_recebidos:
        # Verifica se há palavras em comum
        palavras_rec = cliente_rec.upper().split()
        palavras_comuns = set(palavras) & set(palavras_rec)
        if len(palavras_comuns) >= 2:  # Pelo menos 2 palavras em comum
            correspondencias.append((cliente_proj, cliente_rec, palavras_comuns))
            print(f"  MATCH: '{cliente_proj}' <-> '{cliente_rec}' (palavras: {palavras_comuns})")

print(f"\nTotal de correspondências encontradas: {len(correspondencias)}")

# Vamos testar uma consulta mais flexível
print("\n=== Teste de consulta flexível ===")
total_recebido = 0
count_recebido = 0

for cliente_proj in clientes_projecao:
    palavras = cliente_proj.split()
    if len(palavras) >= 2:
        # Monta uma consulta LIKE com as principais palavras
        palavra1 = palavras[0]
        palavra2 = palavras[1] if len(palavras) > 1 else palavras[0]
        
        cur.execute("""
            SELECT COALESCE(SUM(valor_principal), 0), COUNT(*) 
            FROM contas_receber 
            WHERE status = 'Recebido' 
            AND strftime('%m', vencimento) = '08'
            AND strftime('%Y', vencimento) = '2025'
            AND (UPPER(cliente) LIKE ? OR UPPER(cliente) LIKE ?)
        """, (f"%{palavra1}%", f"%{palavra2}%"))
        
        resultado = cur.fetchone()
        if resultado[0] > 0:
            print(f"  Cliente '{cliente_proj}': R$ {resultado[0]:.2f} ({resultado[1]} registros)")
            total_recebido += resultado[0]
            count_recebido += resultado[1]

print(f"\nTotal aproximado recebido em 08/2025: R$ {total_recebido:.2f} ({count_recebido} registros)")

conn.close()
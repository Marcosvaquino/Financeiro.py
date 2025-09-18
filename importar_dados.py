import sys
import os
sys.path.append('financeiro')

from importacao import salvar_contas_receber
import pandas as pd

print("=== IMPORTANDO DADOS PARA O BANCO ===\n")

arquivo_csv = 'uploads/lancamentos-a-receber_16-09-2025_13-53.csv'

print(f"1. Lendo arquivo: {arquivo_csv}")

try:
    # Lê o CSV com pandas - tenta diferentes encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(arquivo_csv, delimiter=';', encoding=encoding)
            print(f"   Sucesso com encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Não foi possível ler o arquivo com nenhum encoding testado")
    print(f"   Arquivo lido com sucesso: {len(df)} linhas")
    
    # Chama a função de importação com o caminho do arquivo
    print("\n2. Importando para o banco de dados...")
    salvar_contas_receber(arquivo_csv)
    print("   ✓ Dados importados com sucesso!")
    
    # Verifica se os dados foram importados
    print("\n3. Verificando importação...")
    import sqlite3
    conn = sqlite3.connect('financeiro/financeiro.db')
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM contas_receber")
    total = cur.fetchone()[0]
    print(f"   Total de registros no banco: {total}")
    
    # Verifica MINERVA S A
    cur.execute("SELECT COUNT(*) FROM contas_receber WHERE UPPER(cliente) LIKE '%MINERVA S A%'")
    minerva_total = cur.fetchone()[0]
    print(f"   Registros de MINERVA S A: {minerva_total}")
    
    # Verifica MINERVA S A em agosto
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(valor_principal), 0)
        FROM contas_receber 
        WHERE UPPER(cliente) LIKE '%MINERVA S A%' 
        AND vencimento LIKE '%/08/2025%'
        AND status = 'Recebido'
    """)
    resultado = cur.fetchone()
    print(f"   MINERVA S A - Agosto/2025 - Recebido: {resultado[0]} registros, R$ {resultado[1]:,.2f}")
    
    conn.close()
    
except Exception as e:
    print(f"   ✗ Erro: {e}")
    import traceback
    traceback.print_exc()
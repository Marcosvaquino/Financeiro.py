"""
Script para verificar peso por cidade no banco de dados
"""

import sqlite3

conn = sqlite3.connect(r'z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro.db')
cursor = conn.cursor()

# Consultar dados
cursor.execute('''
    SELECT cidade, valor, peso 
    FROM mapa_calor_dados 
    ORDER BY peso DESC 
    LIMIT 30
''')

print("\n" + "="*80)
print("🔍 TOP 30 CIDADES POR PESO NO BANCO DE DADOS")
print("="*80)
print(f"{'Cidade':<30} {'Ocorrências':<15} {'Peso (ton)':<15}")
print("-"*80)

total_ocorrencias = 0
total_peso = 0

for row in cursor.fetchall():
    cidade, valor, peso = row
    total_ocorrencias += valor
    total_peso += peso
    print(f"{cidade:<30} {valor:<15} {peso:<15.2f}")

print("-"*80)
print(f"{'TOTAL':<30} {total_ocorrencias:<15} {total_peso:<15.2f}")
print("="*80)

# Verificar estatísticas gerais
cursor.execute('SELECT COUNT(*), SUM(valor), SUM(peso) FROM mapa_calor_dados')
total_cidades, soma_valor, soma_peso = cursor.fetchone()

print(f"\n📊 ESTATÍSTICAS GERAIS:")
print(f"   Total de Cidades: {total_cidades}")
print(f"   Total Ocorrências: {soma_valor}")
print(f"   Total Peso: {soma_peso:.2f} ton")

# Verificar se há cidades com peso 0
cursor.execute('SELECT COUNT(*) FROM mapa_calor_dados WHERE peso = 0 OR peso IS NULL')
sem_peso = cursor.fetchone()[0]
print(f"   Cidades sem peso: {sem_peso}")

print("\n" + "="*80)

conn.close()

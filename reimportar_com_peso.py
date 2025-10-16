"""
Script para REIMPORTAR o arquivo endereço clientes.xlsx com a coluna PESO
"""

import pandas as pd
import sqlite3
from datetime import datetime

# Ler arquivo Excel
arquivo = r'z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro\uploads\endereço clientes.xlsx'
print("📂 Lendo arquivo Excel...")
df = pd.read_excel(arquivo)

print(f"✅ Arquivo lido: {len(df)} linhas")
print(f"📋 Colunas: {df.columns.tolist()}")

# Verificar se tem coluna Peso
if 'Peso' not in df.columns:
    print("❌ ERRO: Coluna 'Peso' não encontrada!")
    print("Colunas disponíveis:", df.columns.tolist())
    exit(1)

print(f"\n📊 Amostra dos dados:")
print(df[['Cidade', 'Quantidade', 'Peso']].head(10))

# Agrupar por cidade
print("\n🔄 Agrupando dados por cidade...")
cidades_agrupadas = {}

for idx, row in df.iterrows():
    cidade = str(row['Cidade']).strip()
    qtd = row.get('Quantidade', 0)
    peso = row.get('Peso', 0)
    
    if pd.notna(cidade) and cidade.upper() not in ['NAN', 'NONE', '']:
        cidade_upper = cidade.upper()
        if cidade_upper not in cidades_agrupadas:
            cidades_agrupadas[cidade_upper] = {
                'cidade': cidade,
                'quantidade': 0,
                'peso': 0.0
            }
        
        cidades_agrupadas[cidade_upper]['quantidade'] += qtd if pd.notna(qtd) else 0
        
        if pd.notna(peso):
            try:
                cidades_agrupadas[cidade_upper]['peso'] += float(peso)
            except (ValueError, TypeError):
                pass

print(f"✅ {len(cidades_agrupadas)} cidades únicas encontradas")

# Mostrar top 10 por peso
top_peso = sorted(cidades_agrupadas.items(), key=lambda x: x[1]['peso'], reverse=True)[:10]
print("\n🏆 TOP 10 CIDADES POR PESO:")
print(f"{'Cidade':<25} {'Quantidade':<12} {'Peso (ton)':<15}")
print("-"*55)
for cidade_upper, info in top_peso:
    print(f"{info['cidade']:<25} {info['quantidade']:<12} {info['peso']:<15.2f}")

# Confirmar antes de salvar
print("\n" + "="*70)
resposta = input("💾 Deseja SUBSTITUIR os dados do banco? (sim/não): ")

if resposta.lower() != 'sim':
    print("❌ Operação cancelada.")
    exit(0)

# Conectar ao banco
print("\n🔄 Conectando ao banco de dados...")
conn = sqlite3.connect(r'z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro.db')
cursor = conn.cursor()

# Limpar dados antigos
print("🗑️ Limpando dados antigos...")
cursor.execute('DELETE FROM mapa_calor_dados')
cursor.execute('DELETE FROM mapa_calor_uploads')
conn.commit()

# Criar novo upload
print("📝 Criando registro de upload...")
cursor.execute('''
    INSERT INTO mapa_calor_uploads (nome_arquivo, total_locais, total_linhas, total_erros)
    VALUES (?, ?, ?, ?)
''', ('endereço clientes.xlsx', len(cidades_agrupadas), len(df), 0))

upload_id = cursor.lastrowid

# IMPORTANTE: Precisamos geocodificar as cidades
# Dicionário de coordenadas SP
cidades_coords = {
    'SÃO PAULO': [-23.5505, -46.6333],
    'CAMPINAS': [-22.9056, -47.0608],
    'SANTOS': [-23.9618, -46.3322],
    'SÃO JOSÉ DOS CAMPOS': [-23.2237, -45.9009],
    'SOROCABA': [-23.5015, -47.4526],
    'GUARULHOS': [-23.4538, -46.5333],
    'SANTO ANDRÉ': [-23.6633, -46.5333],
    'OSASCO': [-23.5329, -46.7918],
    'SÃO BERNARDO DO CAMPO': [-23.6914, -46.5646],
    'MAUÁ': [-23.6700, -46.4611],
    'DIADEMA': [-23.6861, -46.6208],
    'BARUERI': [-23.5106, -46.8767],
    'CAÇAPAVA': [-23.1003, -45.7073],
    'ITAQUAQUECETUBA': [-23.4869, -46.3483],
    'JUNDIAÍ': [-23.1864, -46.8842],
    'TABOÃO DA SERRA': [-23.6088, -46.7575],
    'INDAIATUBA': [-23.0903, -47.2180],
}

print("💾 Salvando dados com PESO...")
salvos = 0
sem_coords = 0

for cidade_upper, info in cidades_agrupadas.items():
    coords = cidades_coords.get(cidade_upper)
    
    if coords:
        cursor.execute('''
            INSERT INTO mapa_calor_dados (upload_id, cidade, latitude, longitude, valor, peso)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (upload_id, info['cidade'], coords[0], coords[1], info['quantidade'], info['peso']))
        salvos += 1
    else:
        sem_coords += 1

conn.commit()
conn.close()

print("\n" + "="*70)
print(f"✅ Dados salvos com sucesso!")
print(f"   Cidades salvas: {salvos}")
print(f"   Cidades sem coordenadas: {sem_coords}")
print(f"   Total peso: {sum(info['peso'] for info in cidades_agrupadas.values()):.2f} ton")
print("="*70)
print("\n💡 Agora recarregue a página do mapa de calor!")

import sys, os
root = r'D:\OneDrive\PROJETOFINANCEIRO.PY'
sys.path.insert(0, root)

import pandas as pd
import sqlite3

print("🔄 CORRIGINDO COLUNA Cliente_Real...")

# 1. Ler o Manifesto_Acumulado.xlsx
manifesto_path = os.path.join(root, 'financeiro', 'uploads', 'Manifesto_Acumulado.xlsx')
print(f"📊 Lendo arquivo: {manifesto_path}")
df = pd.read_excel(manifesto_path)

print(f"✅ {len(df)} registros carregados")

# 2. Buscar todos os clientes cadastrados no banco
print("🔍 Buscando clientes cadastrados no banco...")
conn = sqlite3.connect(os.path.join(root, 'financeiro.db'))
cursor = conn.cursor()

cursor.execute("SELECT nome_real, nome_ajustado FROM clientes_suporte WHERE ativo = 1")
clientes_cadastrados = cursor.fetchall()
conn.close()

# Criar dicionário de mapeamento: nome_real -> nome_ajustado
mapeamento = {}
for nome_real, nome_ajustado in clientes_cadastrados:
    mapeamento[nome_real.upper().strip()] = nome_ajustado

print(f"👥 {len(mapeamento)} clientes encontrados no banco:")
for real, ajustado in list(mapeamento.items())[:5]:
    print(f"  {real} → {ajustado}")

# 3. Aplicar o mapeamento
print("🔄 Aplicando mapeamento...")
def mapear_cliente(nome_cliente):
    if pd.isna(nome_cliente) or nome_cliente == 0:
        return '0'
    
    nome_upper = str(nome_cliente).upper().strip()
    if nome_upper in mapeamento:
        return mapeamento[nome_upper]
    else:
        # Se não encontrar, retorna o nome original
        return str(nome_cliente).strip()

# Aplicar o mapeamento na coluna Cliente_Real
df['Cliente_Real'] = df['Cliente'].apply(mapear_cliente)

# 4. Verificar resultados
print("📊 Verificando resultados...")
print(f"Cliente_Real únicos após mapeamento: {df['Cliente_Real'].nunique()}")
print("Primeiros 10 valores únicos:")
for i, (valor, count) in enumerate(df['Cliente_Real'].value_counts().head(10).items()):
    print(f"  {i+1}. {valor}: {count} registros")

# 5. Salvar arquivo
print("💾 Salvando arquivo...")
df.to_excel(manifesto_path, index=False)

print("✅ CORREÇÃO CONCLUÍDA!")
print(f"📁 Arquivo salvo: {manifesto_path}")
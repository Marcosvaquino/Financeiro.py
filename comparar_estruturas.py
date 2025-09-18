import sqlite3

# Conecta ao banco
conn = sqlite3.connect('financeiro/financeiro.db')
cur = conn.cursor()

print("=== COMPARAÇÃO DE ESTRUTURAS ===\n")

print("1. Estrutura ATUAL da tabela contas_receber:")
cur.execute("PRAGMA table_info(contas_receber)")
colunas_atuais = cur.fetchall()
for coluna in colunas_atuais:
    print(f"   {coluna[1]} ({coluna[2]})")

print("\n2. Estrutura ESPERADA pela função de importação:")
esperadas = [
    "cnpj_filial", "filial", "cnpj_cliente", "cliente", "sequencia", 
    "numero_documento", "cheque", "emissao", "vencimento", "vencimento_original",
    "competencia", "valor_principal", "juros_desc", "valor_titulo", 
    "data_baixa", "data_liquidacao", "banco_pagto", "conta_pagto", 
    "forma_pagto", "observacoes", "conta_contabil", "status", "email_fatura"
]

for col in esperadas:
    print(f"   {col}")

print("\n3. Diferenças encontradas:")
atuais_nomes = [col[1] for col in colunas_atuais]
print("   Na tabela atual mas não na esperada:")
for col in atuais_nomes:
    if col not in esperadas:
        print(f"     - {col}")

print("   Na esperada mas não na tabela atual:")
for col in esperadas:
    if col not in atuais_nomes:
        print(f"     + {col}")

conn.close()
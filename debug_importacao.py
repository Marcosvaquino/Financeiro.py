import sys
import os
sys.path.append('financeiro')

import pandas as pd
from database import get_connection

print("=== DEBUG DA IMPORTAÇÃO ===\n")

arquivo_csv = 'uploads/lancamentos-a-receber_16-09-2025_13-53.csv'

# 1. Lê o arquivo CSV
print("1. Lendo arquivo CSV...")
df = pd.read_csv(arquivo_csv, delimiter=';', encoding='latin-1')
print(f"   Linhas lidas: {len(df)}")
print(f"   Colunas: {list(df.columns)}")

# 2. Verifica o mapeamento de colunas
print("\n2. Verificando mapeamento de colunas...")
column_mapping = {
    'CNPJ Filial': 'cnpj_filial',
    'Filial': 'filial', 
    'CNPJ Cliente': 'cnpj_cliente',
    'Cliente': 'cliente',
    'Sequência': 'sequencia',
    'Nº Documento': 'documento',
    'Cheque': 'cheque',
    'Emissão': 'emissao',
    'Vencimento': 'vencimento',
    'Vencimento Original': 'vencimento_original',
    'Competência': 'competencia',
    'Valor Principal': 'valor_principal',
    'Juros/Desc': 'juros_desc',
    'Valor Título': 'valor_titulo',
    'Data Baixa': 'data_baixa',
    'Data Liquidação': 'data_liquidacao',
    'Banco Pagto': 'banco_recebimento',
    'Conta Pagto': 'conta_recebimento',
    'Forma Pagto': 'forma_recebimento',
    'Observações': 'observacoes',
    'Conta Contábil': 'conta_contabil',
    'Status': 'status',
    'Email para fatura': 'descricao_receita'
}

print("   Colunas encontradas:")
for csv_col, db_col in column_mapping.items():
    if csv_col in df.columns:
        print(f"     ✓ {csv_col} -> {db_col}")
    else:
        print(f"     ✗ {csv_col} -> {db_col} (AUSENTE)")

# 3. Testa algumas conversões
print("\n3. Testando conversões de dados...")
if 'Cliente' in df.columns:
    minerva_count = df[df['Cliente'].str.contains('MINERVA S A', na=False)].shape[0]
    print(f"   Registros de MINERVA S A encontrados: {minerva_count}")

if 'Vencimento' in df.columns:
    agosto_count = df[df['Vencimento'].str.contains('/08/', na=False)].shape[0]
    print(f"   Registros com vencimento em agosto: {agosto_count}")

# 4. Aplica o mapeamento
print("\n4. Aplicando mapeamento...")
df_mapped = df.rename(columns=column_mapping)
print(f"   Colunas após mapeamento: {list(df_mapped.columns)}")

# 5. Verifica dados específicos
if 'cliente' in df_mapped.columns and 'vencimento' in df_mapped.columns and 'status' in df_mapped.columns:
    teste_filtro = df_mapped[
        (df_mapped['cliente'].str.contains('MINERVA S A', na=False)) &
        (df_mapped['vencimento'].str.contains('/08/', na=False)) &
        (df_mapped['status'] == 'Recebido')
    ]
    print(f"\n5. Teste do filtro MINERVA S A + Agosto + Recebido: {len(teste_filtro)} registros")
    
    if len(teste_filtro) > 0:
        print("   Primeiros registros:")
        for i, row in teste_filtro.head(3).iterrows():
            print(f"     {row['cliente']} | {row['vencimento']} | {row['valor_principal']} | {row['status']}")

print("\n6. Tentando importar para o banco...")
try:
    conn = get_connection()
    
    # Converte valores
    if 'valor_principal' in df_mapped.columns:
        df_mapped['valor_principal'] = df_mapped['valor_principal'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_mapped['valor_principal'] = pd.to_numeric(df_mapped['valor_principal'], errors='coerce').fillna(0)
    
    # Adiciona centro_custo
    df_mapped['centro_custo'] = ''
    
    # Filtra colunas
    colunas_tabela = ['cnpj_filial', 'filial', 'cnpj_cliente', 'cliente', 'sequencia', 
                      'documento', 'cheque', 'emissao', 'vencimento', 'vencimento_original',
                      'competencia', 'valor_principal', 'juros_desc', 'valor_titulo',
                      'data_baixa', 'data_liquidacao', 'banco_recebimento', 'conta_recebimento',
                      'forma_recebimento', 'observacoes', 'conta_contabil', 'centro_custo',
                      'status', 'descricao_receita']
    
    colunas_existentes = [col for col in colunas_tabela if col in df_mapped.columns]
    df_final = df_mapped[colunas_existentes]
    
    print(f"   Colunas finais: {list(df_final.columns)}")
    print(f"   Registros a inserir: {len(df_final)}")
    
    # Insere no banco
    df_final.to_sql("contas_receber", conn, if_exists="append", index=False)
    conn.commit()
    print("   ✓ Inserção bem-sucedida!")
    
    # Verifica se foi inserido
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM contas_receber")
    total = cur.fetchone()[0]
    print(f"   Total no banco após inserção: {total}")
    
    conn.close()
    
except Exception as e:
    print(f"   ✗ Erro: {e}")
    import traceback
    traceback.print_exc()
import os
import pandas as pd
import sqlite3

# Caminho para o banco na raiz do projeto (um nível acima)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "financeiro.db")

# =========================
# Conexão com o banco
# =========================
def get_connection():
    return sqlite3.connect(DB_PATH)


# =========================
# Carregar CSV ou XLSX
# =========================
def carregar_dataframe(filepath):
    if filepath.endswith(".csv"):
        # Lista de encodings para testar
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        # Lista de separadores para testar
        separators = [';', ',', '\t']
        
        df = None
        for encoding in encodings:
            for sep in separators:
                try:
                    print(f"🔄 Tentando encoding={encoding}, sep='{sep}'")
                    df = pd.read_csv(
                        filepath, 
                        sep=sep, 
                        encoding=encoding, 
                        on_bad_lines='skip',
                        skipinitialspace=True,
                        quotechar='"',
                        engine='python'  # Mais flexível para arquivos malformados
                    )
                    if len(df.columns) >= 4:  # Verificação básica de que o arquivo foi lido corretamente
                        print(f"✅ Sucesso com encoding={encoding}, sep='{sep}', colunas={len(df.columns)}")
                        break
                except Exception as e:
                    print(f"❌ Falhou encoding={encoding}, sep='{sep}': {str(e)[:100]}")
                    continue
            if df is not None and len(df.columns) >= 4:
                break
        
        if df is None or len(df.columns) < 4:
            raise ValueError("Não foi possível ler o arquivo CSV com nenhuma combinação de encoding/separador")
            
    elif filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou XLSX.")
    
    print(f"📊 Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas")
    print(f"🏷️ Colunas detectadas: {list(df.columns)[:5]}...")  # Mostra primeiras 5 colunas
    
    # Mapeia os nomes das colunas para o padrão do banco
    mapeamento_colunas = {
        # Contas a Pagar
        'CNPJ Filial': 'cnpj_filial',
        'Filial': 'filial', 
        'CNPJ Fornecedor': 'cnpj_fornecedor',
        'Fornecedor': 'fornecedor',
        'Sequência': 'sequencia',
        'Nº Documento': 'numero_documento',
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
        'Banco Pagto': 'banco_pagto',
        'Conta Pagto': 'conta_pagto',
        'Forma Pagto': 'forma_pagto',
        'Observações': 'observacoes',
        'Conta Contábil': 'conta_contabil',
        'Centro de Custo': 'centro_custo',
        'Status': 'status',
        'Descrição Despesa': 'descricao_despesa',
        
        # Contas a Receber
        'CNPJ Cliente': 'cnpj_cliente',
        'Cliente': 'cliente',
        'Email para fatura': 'email_fatura'
    }
    
    # Renomeia apenas as colunas que existem no DataFrame
    colunas_existentes = {col: mapeamento_colunas[col] for col in df.columns if col in mapeamento_colunas}
    df = df.rename(columns=colunas_existentes)
    print(f"🔄 Colunas mapeadas: {len(colunas_existentes)} de {len(df.columns)}")
    
    return df


# =========================
# Função principal
# =========================
def importar_arquivo(file_storage):
    """Processa o arquivo enviado e salva no banco"""

    filename = file_storage.filename
    
    # Determina o nome padronizado baseado no conteúdo
    if "receber" in filename.lower():
        standard_filename = "contas-a-receber.csv"
        action = "receber"
    elif "pagar" in filename.lower():
        standard_filename = "contas-a-pagar.csv"
        action = "pagar"
    else:
        return "⚠️ Arquivo ignorado (nome não reconhecido)."
    
    # Configura caminhos: sempre usar a pasta 'uploads' dentro do pacote financeiro
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, standard_filename)
    
    # Remove arquivo anterior se existir
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"🗑️ Arquivo anterior removido: {standard_filename}")
    
    # Salva com nome padronizado
    file_storage.save(filepath)
    print(f"💾 Arquivo salvo como: {standard_filename}")

    try:
        # Limpa dados anteriores do banco antes de importar
        conn = get_connection()
        cur = conn.cursor()
        
        if action == "receber":
            cur.execute("DELETE FROM contas_receber")
            print("🧹 Dados anteriores de contas a receber removidos")
            salvar_contas_receber(filepath)
            conn.commit()
            conn.close()
            return "📥 Contas a Receber importadas com sucesso!"
        elif action == "pagar":
            cur.execute("DELETE FROM contas_pagar")
            print("🧹 Dados anteriores de contas a pagar removidos")
            salvar_contas_pagar(filepath)
            conn.commit()
            conn.close()
            return "📤 Contas a Pagar importadas com sucesso!"
            
    except Exception as e:
        return f"❌ Erro ao importar {filename}: {str(e)}"


# =========================
# Contas a Receber
# =========================
def salvar_contas_receber(filepath):
    print(f"🔄 Iniciando importação de: {filepath}")
    df = carregar_dataframe(filepath)
    print(f"📊 Dados carregados: {len(df)} registros")

    conn = get_connection()
    cur = conn.cursor()
    
    print(f"🔗 Conectado ao banco: {DB_PATH}")

    # Mapeamento das colunas do CSV para as colunas da tabela
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
        'Email para fatura': 'descricao_receita'  # Usando campo disponível
    }
    
    print(f"🏷️ Colunas originais: {list(df.columns)}")
    
    # Renomeia as colunas
    df = df.rename(columns=column_mapping)
    print(f"🏷️ Colunas após mapeamento: {list(df.columns)}")
    
    # Adiciona coluna centro_custo se não existir
    if 'centro_custo' not in df.columns:
        df['centro_custo'] = ''
        print("➕ Adicionada coluna centro_custo")
    
    # Função para converter valores monetários brasileiros
    def converter_valor_brasileiro(valor):
        if pd.isna(valor) or valor == '':
            return 0.0
        try:
            # Converte para string e remove espaços
            valor_str = str(valor).strip()
            # Remove pontos (separadores de milhares) e substitui vírgula por ponto
            valor_str = valor_str.replace('.', '').replace(',', '.')
            return float(valor_str)
        except:
            return 0.0
    
    # Converte valores monetários do formato brasileiro para float
    colunas_monetarias = ['valor_principal', 'juros_desc', 'valor_titulo']
    for coluna in colunas_monetarias:
        if coluna in df.columns:
            valores_originais = df[coluna].head(3).tolist()
            df[coluna] = df[coluna].apply(converter_valor_brasileiro)
            valores_convertidos = df[coluna].head(3).tolist()
            print(f"💰 {coluna}: {valores_originais} → {valores_convertidos}")
    
    # Remove a coluna id se existir (é auto incremento)
    if 'id' in df.columns:
        df = df.drop('id', axis=1)
        print("🗑️ Removida coluna id")
    
    # Seleciona apenas as colunas que existem na tabela
    colunas_tabela = ['cnpj_filial', 'filial', 'cnpj_cliente', 'cliente', 'sequencia', 
                      'documento', 'cheque', 'emissao', 'vencimento', 'vencimento_original',
                      'competencia', 'valor_principal', 'juros_desc', 'valor_titulo',
                      'data_baixa', 'data_liquidacao', 'banco_recebimento', 'conta_recebimento',
                      'forma_recebimento', 'observacoes', 'conta_contabil', 'centro_custo',
                      'status', 'descricao_receita']
    
    # Filtra apenas as colunas que existem tanto no DataFrame quanto na tabela
    colunas_existentes = [col for col in colunas_tabela if col in df.columns]
    print(f"✅ Colunas para inserir: {colunas_existentes}")
    df_filtrado = df[colunas_existentes]
    
    # Verificar dados específicos antes da inserção
    minerva_count = len(df_filtrado[df_filtrado['cliente'].str.contains('MINERVA', na=False)])
    if minerva_count > 0:
        print(f"🔍 Registros MINERVA encontrados: {minerva_count}")
        minerva_sample = df_filtrado[df_filtrado['cliente'].str.contains('MINERVA', na=False)].head(2)
        print(f"📋 Amostra MINERVA:")
        for idx, row in minerva_sample.iterrows():
            print(f"  - {row['cliente']} | {row['vencimento']} | R$ {row['valor_principal']:.2f} | {row['status']}")

    # Contar registros antes da inserção
    cur.execute("SELECT COUNT(*) FROM contas_receber")
    antes = cur.fetchone()[0]
    print(f"📊 Registros no banco antes: {antes:,}")

    # Inserir dados
    df_filtrado.to_sql("contas_receber", conn, if_exists="append", index=False)
    print("💾 Dados inseridos no banco")
    
    # Commit explícito
    conn.commit()
    print("✅ Commit realizado")
    
    # Contar registros após a inserção
    cur.execute("SELECT COUNT(*) FROM contas_receber")
    depois = cur.fetchone()[0]
    print(f"📊 Registros no banco depois: {depois:,}")
    print(f"➕ Registros adicionados: {depois - antes:,}")
    
    # Verificar especificamente MINERVA após inserção
    cur.execute("SELECT COUNT(*) FROM contas_receber WHERE cliente LIKE '%MINERVA%'")
    minerva_db = cur.fetchone()[0]
    print(f"🔍 MINERVA no banco após inserção: {minerva_db:,}")
    
    conn.close()
    print("🔚 Conexão fechada")


# =========================
# Contas a Pagar
# =========================
def salvar_contas_pagar(filepath):
    df = carregar_dataframe(filepath)

    conn = get_connection()
    cur = conn.cursor()

    # cria tabela do zero
    cur.execute("DROP TABLE IF EXISTS contas_pagar")
    cur.execute("""
    CREATE TABLE contas_pagar (
        cnpj_filial TEXT,
        filial TEXT,
        cnpj_fornecedor TEXT,
        fornecedor TEXT,
        sequencia TEXT,
        numero_documento TEXT,
        cheque TEXT,
        emissao TEXT,
        vencimento TEXT,
        vencimento_original TEXT,
        competencia TEXT,
        valor_principal REAL,
        juros_desc REAL,
        valor_titulo REAL,
        data_baixa TEXT,
        data_liquidacao TEXT,
        banco_pagto TEXT,
        conta_pagto TEXT,
        forma_pagto TEXT,
        observacoes TEXT,
        conta_contabil TEXT,
        centro_custo TEXT,
        status TEXT,
        descricao_despesa TEXT
    )
    """)

    # Mapeamento de colunas semelhantes ao CSV -> tabela
    mapping = {
        'CNPJ Filial': 'cnpj_filial',
        'Filial': 'filial',
        'CNPJ Fornecedor': 'cnpj_fornecedor',
        'Fornecedor': 'fornecedor',
        'Sequência': 'sequencia',
        'Nº Documento': 'numero_documento',
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
        'Banco Pagto': 'banco_pagto',
        'Conta Pagto': 'conta_pagto',
        'Forma Pagto': 'forma_pagto',
        'Observações': 'observacoes',
        'Conta Contábil': 'conta_contabil',
        'Centro de Custo': 'centro_custo',
        'Status': 'status',
        'Descrição Despesa': 'descricao_despesa'
    }

    # Renomeia colunas que existem
    col_exist = {c: mapping[c] for c in df.columns if c in mapping}
    df = df.rename(columns=col_exist)

    # Garante coluna centro_custo
    if 'centro_custo' not in df.columns:
        df['centro_custo'] = ''

    # Conversor de valores brasileiros -> float
    def converter_valor_brasileiro(valor):
        import pandas as pd
        if pd.isna(valor) or valor == '':
            return 0.0
        try:
            valor_str = str(valor).strip()
            valor_str = valor_str.replace('.', '').replace(',', '.')
            return float(valor_str)
        except:
            return 0.0

    colunas_monetarias = ['valor_principal', 'juros_desc', 'valor_titulo']
    for coluna in colunas_monetarias:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(converter_valor_brasileiro)

    # Seleciona apenas colunas da tabela
    colunas_tabela = ['cnpj_filial','filial','cnpj_fornecedor','fornecedor','sequencia','numero_documento',
                      'cheque','emissao','vencimento','vencimento_original','competencia','valor_principal',
                      'juros_desc','valor_titulo','data_baixa','data_liquidacao','banco_pagto','conta_pagto',
                      'forma_pagto','observacoes','conta_contabil','centro_custo','status','descricao_despesa']

    colunas_existentes = [col for col in colunas_tabela if col in df.columns]
    df_filtrado = df[colunas_existentes]

    # Insere na tabela
    df_filtrado.to_sql("contas_pagar", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

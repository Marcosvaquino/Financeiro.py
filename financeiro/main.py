from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_from_directory
from .database import init_db, get_connection
from .importacao import importar_arquivo
import bcrypt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "frz-secret"  # chave de sessão

# Função para formatação brasileira de valores
def format_currency(value):
    """Formata valores para padrão brasileiro: 1.234.567,89"""
    if value is None or value == '':
        return "0,00"
    
    # Converte para float e trata erros
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return "0,00"
    
    # Formata e converte para padrão brasileiro
    formatted = "{:,.2f}".format(num_value)
    # Troca separadores: vírgula por X, ponto por vírgula, X por ponto
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

# Registra a função no Jinja2
app.jinja_env.filters['currency'] = format_currency

# Função inteligente para normalizar nomes de clientes
def normalizar_nome_cliente(nome):
    """Normaliza nomes removendo acentos, espaços extras e padronizando maiúsculas"""
    import unicodedata
    
    if not nome:
        return ""
    
    # Remove acentos
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(char for char in nome if unicodedata.category(char) != 'Mn')
    
    # Converte para maiúsculo e remove espaços extras
    nome = nome.upper().strip()
    
    # Remove espaços duplos
    while '  ' in nome:
        nome = nome.replace('  ', ' ')
    
    return nome

# Lista dos 19 clientes principais (normalizados)
CLIENTES_19_PRINCIPAIS = [
    'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
    'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
    'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
    'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
    'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAI'
]

def eh_cliente_principal(nome_cliente):
    """Verifica se um cliente está na lista dos 19 principais usando normalização inteligente"""
    nome_normalizado = normalizar_nome_cliente(nome_cliente)
    
    # Verifica contra cada cliente da lista principal
    for cliente_principal in CLIENTES_19_PRINCIPAIS:
        cliente_principal_normalizado = normalizar_nome_cliente(cliente_principal)
        
        # Verifica match exato
        if nome_normalizado == cliente_principal_normalizado:
            return True
            
        # Verifica match parcial para casos como "GTFOODS BARUERI " (com espaço)
        if cliente_principal_normalizado in nome_normalizado or nome_normalizado in cliente_principal_normalizado:
            # Só aceita se a diferença for apenas espaços
            if abs(len(nome_normalizado) - len(cliente_principal_normalizado)) <= 2:
                return True
    
    return False

def filtrar_clientes_principais(cursor, tabela, condicoes_extras=""):
    """
    Retorna lista de clientes principais da tabela com suas variações reais do banco
    """
    # Busca todos os clientes únicos da tabela
    query = f"SELECT DISTINCT cliente FROM {tabela} {condicoes_extras}"
    cursor.execute(query)
    todos_clientes = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Filtra apenas os que são clientes principais
    clientes_filtrados = []
    for cliente in todos_clientes:
        if eh_cliente_principal(cliente):
            clientes_filtrados.append(cliente)
    
    return clientes_filtrados

def criar_condicao_clientes_principais(cursor, tabela, condicoes_extras=""):
    """
    Cria condição SQL para filtrar apenas os 19 clientes principais
    """
    clientes_reais = filtrar_clientes_principais(cursor, tabela, condicoes_extras)
    
    if not clientes_reais:
        return "1=0", []  # Nenhum cliente encontrado
    
    # Cria placeholders
    placeholders = ','.join(['?' for _ in clientes_reais])
    condicao = f"cliente IN ({placeholders})"
    
    return condicao, clientes_reais

# --- helper: login required decorator ---
from functools import wraps
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

# Registra blueprints de módulos adicionais (placeholders)
try:
    from .upload_sistema import bp as upload_bp
    app.register_blueprint(upload_bp)
except Exception:
    pass
try:
    from .frete import bp as frete_bp
    app.register_blueprint(frete_bp)
except Exception:
    pass
try:
    from .armazem import bp as armazem_bp
    app.register_blueprint(armazem_bp)
except Exception:
    pass
try:
    from .logistica import bp as logistica_bp
    app.register_blueprint(logistica_bp)
except Exception:
    pass
try:
    from .suporte import bp as suporte_bp
    app.register_blueprint(suporte_bp)
except Exception:
    pass

# Inicializa banco de dados somente quando executado como script
# (não executar no import para evitar apagar dados durante testes/imports)

# ============================
# FUNÇÕES AUXILIARES
# ============================

def formatar_valor_brasileiro(valor):
    """Formata valor para padrão brasileiro: 1.234.567,89"""
    # Garante que o valor seja numérico
    try:
        if isinstance(valor, str):
            # Remove formatação brasileira se existir
            valor = valor.replace('.', '').replace(',', '.')
        valor = float(valor) if valor else 0.0
    except (ValueError, TypeError):
        valor = 0.0
    
    if valor == 0:
        return "0,00"
    
    # Converte para string com 2 casas decimais
    valor_str = f"{valor:.2f}"
    
    # Separa parte inteira e decimal
    partes = valor_str.split('.')
    parte_inteira = partes[0]
    parte_decimal = partes[1]
    
    # Adiciona pontos de milhares na parte inteira
    if len(parte_inteira) > 3:
        # Inverte, adiciona pontos e inverte novamente
        inteira_invertida = parte_inteira[::-1]
        com_pontos = '.'.join([inteira_invertida[i:i+3] for i in range(0, len(inteira_invertida), 3)])
        parte_inteira = com_pontos[::-1]
    
    return f"{parte_inteira},{parte_decimal}"

# ============================
# ROTAS PRINCIPAIS
# ============================

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("planejamento"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, senha_hash, nome FROM usuarios WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(senha.encode("utf-8"), user[1].encode("utf-8")):
            session["user_id"] = user[0]
            session["user_name"] = user[2]
            return redirect(url_for("planejamento"))
        else:
            flash("Usuário ou senha inválidos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================
# PÁGINAS DO MENU
# ============================

@app.route("/planejamento")
@login_required
def planejamento():
    # Pega parâmetros de filtro
    mes = request.args.get('mes')
    ano = request.args.get('ano')
    
    # Se não tiver filtros, usa o mês e ano atual
    if not mes or not ano:
        from datetime import datetime
        now = datetime.now()
        # Garante que mes e ano fiquem em strings no formato esperado
        mes = mes or f"{now.month:02d}"
        ano = ano or str(now.year)
    
    # Busca dados filtrados
    data = build_dashboard_data_with_filters(mes, ano)
    data['selected_month'] = mes
    data['selected_year'] = ano
    
    return render_template("planejamento.html", data=data, selected_month=mes, selected_year=ano)


@app.route("/planejamento_frz")
@login_required
def planejamento_frz():
    """Página de Planejamento FRZ com dados dos bancos."""
    # Parâmetros de filtro (padrão: setembro 2025)
    mes = request.args.get('mes', 9, type=int)
    ano = request.args.get('ano', 2025, type=int)
    
    # Buscar dados do FRZ
    dados_frz = build_dados_frz(mes, ano)
    
    return render_template("planejamento_frz.html", dados=dados_frz, mes=mes, ano=ano)


def build_dados_frz(mes, ano):
    """Constrói dados do FRZ por semanas (sábado a sexta) para o mês/ano especificado."""
    
    # Lista dos 19 clientes FRZ
    clientes_frz = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGOS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
    ]
    
    # Calcular semanas do mês (sábado a sexta)
    semanas = calcular_semanas_sabado_sexta(mes, ano)
    
    # Estrutura de dados
    dados = {
        'mes': mes,
        'ano': ano,
        'semanas': semanas,
        'clientes': {}
    }
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Para cada cliente, buscar dados de cada semana
    for cliente in clientes_frz:
        dados['clientes'][cliente] = {}
        
        for i, semana in enumerate(semanas):
            dados['clientes'][cliente][f'semana_{i+1}'] = {
                'projetado': buscar_valor_projetado(cur, cliente, semana, mes, ano),
                'realizado': buscar_valor_realizado(cur, cliente, semana, mes, ano)
            }
        
        # Total do mês para o cliente
        dados['clientes'][cliente]['total_mes'] = {
            'projetado': sum([dados['clientes'][cliente][f'semana_{i+1}']['projetado'] for i in range(5)]),
            'realizado': sum([dados['clientes'][cliente][f'semana_{i+1}']['realizado'] for i in range(5)])
        }

    # --- Novo: calcular totais realizados por semana considerando TODOS os lançamentos em contas_pagar ---
    # Isso é usado para calcular "despesas gerais" (agora vindo de contas_pagar)
    semanas_totais_todos_realizado = []
    for semana in semanas:
        # se semana vazia
        if semana['inicio'] is None or semana['fim'] is None:
            semanas_totais_todos_realizado.append(0.0)
            continue

        inicio = semana['inicio']
        fim = semana['fim']
        # Se a semana estiver no mesmo mês/ano: projetado/realizado virão de contas_pagar
        if inicio.month == fim.month and inicio.year == fim.year:
            # realizado: somente status RECEBIDO (interpretado como pago/realizado)
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0.0) FROM contas_pagar
                WHERE UPPER(status) = 'RECEBIDO'
                AND (
                    CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN ? AND ?
                )
            """, (inicio.year, inicio.month, inicio.day, fim.day))
            total_real_sem = cur.fetchone()[0] or 0.0

            # projetado: todos os registros (sem filtro de status)
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0.0) FROM contas_pagar
                WHERE (
                    CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN ? AND ?
                )
            """, (inicio.year, inicio.month, inicio.day, fim.day))
            total_proj_sem = cur.fetchone()[0] or 0.0
            total_sem = (total_proj_sem, total_real_sem)
        else:
            # parte no mês/ano de inicio (dia inicio..31)
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0.0) FROM contas_pagar
                WHERE (
                    CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN ? AND 31
                )
            """, (inicio.year, inicio.month, inicio.day))
            p1_proj = cur.fetchone()[0] or 0.0
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0.0) FROM contas_pagar
                WHERE UPPER(status) = 'RECEBIDO'
                AND (
                    CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN ? AND 31
                )
            """, (inicio.year, inicio.month, inicio.day))
            p1_real = cur.fetchone()[0] or 0.0

            # parte no mês/ano de fim (1..dia fim)
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0.0) FROM contas_pagar
                WHERE (
                    CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN 1 AND ?
                )
            """, (fim.year, fim.month, fim.day))
            p2_proj = cur.fetchone()[0] or 0.0
            cur.execute("""
                SELECT COALESCE(SUM(valor_principal), 0.0) FROM contas_pagar
                WHERE UPPER(status) = 'RECEBIDO'
                AND (
                    CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                    CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN 1 AND ?
                )
            """, (fim.year, fim.month, fim.day))
            p2_real = cur.fetchone()[0] or 0.0
            total_sem = (p1_proj + p2_proj, p1_real + p2_real)

        semanas_totais_todos_realizado.append(total_sem)

    # anexa ao dicionário de dados para uso em cálculo de totais
    # cada item agora é (projetado_total_semana, realizado_total_semana)
    dados['semanas_totais_todos_realizado'] = semanas_totais_todos_realizado

    # --- Novo: calcular totais projetados por semana considerando TODOS os clientes (tabela projecao) ---
    semanas_totais_todos_projetado = []
    for semana in semanas:
        if semana['inicio'] is None or semana['fim'] is None:
            semanas_totais_todos_projetado.append(0.0)
            continue

        inicio = semana['inicio']
        fim = semana['fim']

        if inicio.month == fim.month and inicio.year == fim.year:
            cur.execute("""
                SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao
                WHERE mes = ? AND ano = ? AND dia BETWEEN ? AND ?
            """, (inicio.month, inicio.year, inicio.day, fim.day))
            totalp = cur.fetchone()[0] or 0.0
        else:
            cur.execute("""
                SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao
                WHERE mes = ? AND ano = ? AND dia BETWEEN ? AND 31
            """, (inicio.month, inicio.year, inicio.day))
            p1 = cur.fetchone()[0] or 0.0
            cur.execute("""
                SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) FROM projecao
                WHERE mes = ? AND ano = ? AND dia BETWEEN 1 AND ?
            """, (fim.month, fim.year, fim.day))
            p2 = cur.fetchone()[0] or 0.0
            totalp = p1 + p2

        semanas_totais_todos_projetado.append(totalp)

    dados['semanas_totais_todos_projetado'] = semanas_totais_todos_projetado
    
    # Calcular totais gerais
    dados['totais'] = calcular_totais_frz(dados)
    
    conn.close()
    return dados


def calcular_semanas_sabado_sexta(mes, ano):
    """Retorna as semanas do mês baseadas no padrão estático do print fornecido."""
    
    # Mapeamento estático das semanas para cada mês (baseado no print)
    semanas_estaticas = {
        1: [  # Janeiro
            {'label': 'SEMANA 1 A 7', 'inicio_dia': 1, 'fim_dia': 7},
            {'label': 'SEMANA 8 A 14', 'inicio_dia': 8, 'fim_dia': 14},
            {'label': 'SEMANA 15 A 21', 'inicio_dia': 15, 'fim_dia': 21},
            {'label': 'SEMANA 22 A 28', 'inicio_dia': 22, 'fim_dia': 28},
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        2: [  # Fevereiro
            {'label': 'SEMANA 1 A 7', 'inicio_dia': 1, 'fim_dia': 7},
            {'label': 'SEMANA 8 A 14', 'inicio_dia': 8, 'fim_dia': 14},
            {'label': 'SEMANA 15 A 21', 'inicio_dia': 15, 'fim_dia': 21},
            {'label': 'SEMANA 22 A 28', 'inicio_dia': 22, 'fim_dia': 28},
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        3: [  # Março
            {'label': 'SEMANA 1 A 7', 'inicio_dia': 1, 'fim_dia': 7},
            {'label': 'SEMANA 8 A 14', 'inicio_dia': 8, 'fim_dia': 14},
            {'label': 'SEMANA 15 A 21', 'inicio_dia': 15, 'fim_dia': 21},
            {'label': 'SEMANA 22 A 28', 'inicio_dia': 22, 'fim_dia': 28},
            {'label': 'SEMANA 29 A 4', 'inicio_dia': 29, 'fim_dia': 4}  # Abril
        ],
        4: [  # Abril
            {'label': 'SEMANA 5 A 11', 'inicio_dia': 5, 'fim_dia': 11},
            {'label': 'SEMANA 12 A 18', 'inicio_dia': 12, 'fim_dia': 18},
            {'label': 'SEMANA 19 A 25', 'inicio_dia': 19, 'fim_dia': 25},
            {'label': 'SEMANA 26 A 2', 'inicio_dia': 26, 'fim_dia': 2},  # Maio
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        5: [  # Maio
            {'label': 'SEMANA 3 A 9', 'inicio_dia': 3, 'fim_dia': 9},
            {'label': 'SEMANA 10 A 16', 'inicio_dia': 10, 'fim_dia': 16},
            {'label': 'SEMANA 17 A 23', 'inicio_dia': 17, 'fim_dia': 23},
            {'label': 'SEMANA 24 A 30', 'inicio_dia': 24, 'fim_dia': 30},
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        6: [  # Junho
            {'label': 'SEMANA 31 A 6', 'inicio_dia': 31, 'fim_dia': 6},  # Maio-Junho
            {'label': 'SEMANA 7 A 13', 'inicio_dia': 7, 'fim_dia': 13},
            {'label': 'SEMANA 14 A 20', 'inicio_dia': 14, 'fim_dia': 20},
            {'label': 'SEMANA 21 A 27', 'inicio_dia': 21, 'fim_dia': 27},
            {'label': 'SEMANA 28 A 4', 'inicio_dia': 28, 'fim_dia': 4}  # Julho
        ],
        7: [  # Julho
            {'label': 'SEMANA 5 A 11', 'inicio_dia': 5, 'fim_dia': 11},
            {'label': 'SEMANA 12 A 18', 'inicio_dia': 12, 'fim_dia': 18},
            {'label': 'SEMANA 19 A 25', 'inicio_dia': 19, 'fim_dia': 25},
            {'label': 'SEMANA 26 A 1', 'inicio_dia': 26, 'fim_dia': 1},  # Agosto
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        8: [  # Agosto
            {'label': 'SEMANA 2 A 8', 'inicio_dia': 2, 'fim_dia': 8},
            {'label': 'SEMANA 9 A 15', 'inicio_dia': 9, 'fim_dia': 15},
            {'label': 'SEMANA 16 A 22', 'inicio_dia': 16, 'fim_dia': 22},
            {'label': 'SEMANA 23 A 29', 'inicio_dia': 23, 'fim_dia': 29},
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        9: [  # Setembro
            {'label': 'SEMANA 30 A 5', 'inicio_dia': 30, 'fim_dia': 5},  # Agosto-Setembro
            {'label': 'SEMANA 6 A 12', 'inicio_dia': 6, 'fim_dia': 12},
            {'label': 'SEMANA 13 A 19', 'inicio_dia': 13, 'fim_dia': 19},
            {'label': 'SEMANA 20 A 26', 'inicio_dia': 20, 'fim_dia': 26},
            {'label': 'SEMANA 27 A 3', 'inicio_dia': 27, 'fim_dia': 3}  # Outubro
        ],
        10: [  # Outubro
            {'label': 'SEMANA 4 A 10', 'inicio_dia': 4, 'fim_dia': 10},
            {'label': 'SEMANA 11 A 17', 'inicio_dia': 11, 'fim_dia': 17},
            {'label': 'SEMANA 18 A 24', 'inicio_dia': 18, 'fim_dia': 24},
            {'label': 'SEMANA 25 A 31', 'inicio_dia': 25, 'fim_dia': 31},
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        11: [  # Novembro
            {'label': 'SEMANA 1 A 7', 'inicio_dia': 1, 'fim_dia': 7},
            {'label': 'SEMANA 8 A 14', 'inicio_dia': 8, 'fim_dia': 14},
            {'label': 'SEMANA 15 A 21', 'inicio_dia': 15, 'fim_dia': 21},
            {'label': 'SEMANA 22 A 28', 'inicio_dia': 22, 'fim_dia': 28},
            {'label': '-', 'inicio_dia': None, 'fim_dia': None}
        ],
        12: [  # Dezembro
            {'label': 'SEMANA 29 A 5', 'inicio_dia': 29, 'fim_dia': 5},  # Novembro-Dezembro
            {'label': 'SEMANA 6 A 12', 'inicio_dia': 6, 'fim_dia': 12},
            {'label': 'SEMANA 13 A 19', 'inicio_dia': 13, 'fim_dia': 19},
            {'label': 'SEMANA 20 A 26', 'inicio_dia': 20, 'fim_dia': 26},
            {'label': 'SEMANA 27 A 2', 'inicio_dia': 27, 'fim_dia': 2}  # Janeiro próximo
        ]
    }
    
    from datetime import datetime
    
    # Pegar as semanas estáticas para o mês
    semanas_do_mes = semanas_estaticas.get(mes, [])
    
    semanas = []
    for idx, semana_config in enumerate(semanas_do_mes):
        if semana_config['inicio_dia'] is None:
            # Semana vazia
            semanas.append({
                'inicio': None,
                'fim': None,
                'label': '-'
            })
            continue

        # Calcular as datas reais (suportando semanas que cruzam mês anterior/próximo)
        start_day = semana_config['inicio_dia']
        end_day = semana_config['fim_dia']
        try:
            # Inicializar anos/meses para inicio e fim
            inicio_year = ano
            inicio_month = mes
            fim_year = ano
            fim_month = mes

            if start_day > end_day:
                # A semana cruza um mês: decidir se o início é no mês anterior ou o fim é no mês seguinte
                # Regra: se for a primeira semana (idx==0) assume que começa no mês anterior e termina no mês corrente.
                # Se for a última semana (idx==4) assume que começa no mês corrente e termina no mês seguinte.
                if idx == 0:
                    # início no mês anterior
                    if mes == 1:
                        inicio_month = 12
                        inicio_year = ano - 1
                    else:
                        inicio_month = mes - 1
                    fim_month = mes
                    fim_year = ano
                elif idx == 4:
                    # fim no mês seguinte
                    inicio_month = mes
                    inicio_year = ano
                    if mes == 12:
                        fim_month = 1
                        fim_year = ano + 1
                    else:
                        fim_month = mes + 1
                else:
                    # Caso intermediário: por segurança assumir início no mês corrente e fim no mês corrente
                    inicio_month = mes
                    fim_month = mes

            inicio = datetime(inicio_year, inicio_month, start_day)
            fim = datetime(fim_year, fim_month, min(end_day, 31))
        except ValueError:
            inicio = None
            fim = None

        semanas.append({
            'inicio': inicio,
            'fim': fim,
            'label': semana_config['label']
        })
    
    return semanas


def buscar_valor_projetado(cur, cliente, semana, mes, ano):
    """Busca valor projetado para o cliente na semana especificada."""
    # Se a semana está vazia (label = '-'), retornar 0
    if semana['inicio'] is None or semana['fim'] is None:
        return 0.0
    
    # Se a semana cruza meses (inicio e fim em meses diferentes), somar em dois intervalos
    inicio = semana['inicio']
    fim = semana['fim']
    if inicio is None or fim is None:
        return 0.0

    if inicio.month == fim.month and inicio.year == fim.year:
        cur.execute("SELECT SUM(valor) FROM projecao WHERE cliente = ? AND mes = ? AND ano = ? AND dia BETWEEN ? AND ?",
                    (cliente, inicio.month, inicio.year, inicio.day, fim.day))
        resultado = cur.fetchone()[0]
        return resultado if resultado else 0.0
    else:
        # parte 1: inicio.month/inicio.year de inicio.day..31
        cur.execute("SELECT SUM(valor) FROM projecao WHERE cliente = ? AND mes = ? AND ano = ? AND dia BETWEEN ? AND 31",
                    (cliente, inicio.month, inicio.year, inicio.day))
        p1 = cur.fetchone()[0] or 0.0
        # parte 2: fim.month/fim.year de 1..fim.day
        cur.execute("SELECT SUM(valor) FROM projecao WHERE cliente = ? AND mes = ? AND ano = ? AND dia BETWEEN 1 AND ?",
                    (cliente, fim.month, fim.year, fim.day))
        p2 = cur.fetchone()[0] or 0.0
        return p1 + p2


def buscar_valor_realizado(cur, cliente, semana, mes, ano):
    """Busca valor realizado (recebido) para o cliente na semana especificada."""
    from datetime import datetime
    
    # Se a semana está vazia (label = '-'), retornar 0
    if semana['inicio'] is None or semana['fim'] is None:
        return 0.0
    
    # Converter datas da semana para formato de comparação
    inicio_semana = semana['inicio']
    fim_semana = semana['fim']

    if inicio_semana is None or fim_semana is None:
        return 0.0

    # Se a semana está no mesmo mês/ano
    if inicio_semana.month == fim_semana.month and inicio_semana.year == fim_semana.year:
        cur.execute("""
            SELECT SUM(valor_principal) FROM contas_receber 
            WHERE cliente = ? AND UPPER(status) = 'RECEBIDO'
            AND (
                CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN ? AND ?
            )
        """, (
            cliente,
            inicio_semana.year,
            inicio_semana.month,
            inicio_semana.day,
            fim_semana.day
        ))
        resultado = cur.fetchone()[0]
        return resultado if resultado else 0.0
    else:
        # Somar parte no mês/ano de inicio (dia inicio..31)
        cur.execute("""
            SELECT SUM(valor_principal) FROM contas_receber 
            WHERE cliente = ? AND UPPER(status) = 'RECEBIDO'
            AND (
                CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN ? AND 31
            )
        """, (
            cliente,
            inicio_semana.year,
            inicio_semana.month,
            inicio_semana.day
        ))
        p1 = cur.fetchone()[0] or 0.0

        # Somar parte no mês/ano de fim (1..dia fim)
        cur.execute("""
            SELECT SUM(valor_principal) FROM contas_receber 
            WHERE cliente = ? AND UPPER(status) = 'RECEBIDO'
            AND (
                CAST(SUBSTR(vencimento, 7, 4) AS INTEGER) = ? AND
                CAST(SUBSTR(vencimento, 4, 2) AS INTEGER) = ? AND
                CAST(SUBSTR(vencimento, 1, 2) AS INTEGER) BETWEEN 1 AND ?
            )
        """, (
            cliente,
            fim_semana.year,
            fim_semana.month,
            fim_semana.day
        ))
        p2 = cur.fetchone()[0] or 0.0
        return p1 + p2


def calcular_totais_frz(dados):
    """Calcula totais gerais, despesas e resultado do FRZ."""
    totais = {
        'total_geral': {'projetado': 0, 'realizado': 0},
        'despesas_gerais': {'projetado': 0, 'realizado': 0},
        'resultado': {'projetado': 0, 'realizado': 0},
        'semanas': {},
        'despesas_semanas': {}
    }
    
    # Calcular totais por semana
    for semana_num in range(1, 6):  # semanas 1 a 5
        totais['semanas'][f'semana_{semana_num}'] = {'projetado': 0, 'realizado': 0}
        
        for cliente, valores in dados['clientes'].items():
            totais['semanas'][f'semana_{semana_num}']['projetado'] += valores[f'semana_{semana_num}']['projetado']
            totais['semanas'][f'semana_{semana_num}']['realizado'] += valores[f'semana_{semana_num}']['realizado']
    
    # Somar todos os clientes para total geral
    for cliente, valores in dados['clientes'].items():
        totais['total_geral']['projetado'] += valores['total_mes']['projetado']
        totais['total_geral']['realizado'] += valores['total_mes']['realizado']
    
    # Calcular despesas por semana (10% do total de cada semana)
    for semana_num in range(1, 6):
        # projetado: preferimos usar o total projetado de TODOS os clientes (quando disponível)
        projetado_val = None
        # projetado: preferir o total de contas_pagar calculado por semana (quando disponível)
        projetado_val = None
        try:
            todos_sem = dados.get('semanas_totais_todos_realizado')
            if todos_sem and len(todos_sem) >= semana_num:
                sem_item = todos_sem[semana_num-1]
                # sem_item pode ser tupla (proj_total_pagar, real_total_pagar)
                if isinstance(sem_item, (list, tuple)) and len(sem_item) >= 2:
                    projetado_val = float(sem_item[0])
        except Exception:
            projetado_val = None

        # se não houver o total vindo de contas_pagar, tentar a tabela 'projecao' (se disponível)
        if projetado_val is None:
            try:
                todos_projetados = dados.get('semanas_totais_todos_projetado')
                if todos_projetados and len(todos_projetados) >= semana_num:
                    projetado_val = float(todos_projetados[semana_num-1])
            except Exception:
                projetado_val = None

        # fallback final: usa o comportamento antigo (total dos 19 clientes)
        if projetado_val is None:
            projetado_val = totais['semanas'][f'semana_{semana_num}']['projetado']

        # realizado: preferimos usar o total realizado de TODOS os clientes (quando disponível)
        realizado_val = None
        try:
            # dados.semanas_totais_todos_realizado agora contém tuplas (projetado, realizado)
            todos_sem = dados.get('semanas_totais_todos_realizado')
            if todos_sem and len(todos_sem) >= semana_num:
                sem_item = todos_sem[semana_num-1]
                # sem_item pode ser uma tupla (proj, real) ou apenas um float antigo
                if isinstance(sem_item, (list, tuple)) and len(sem_item) >= 2:
                    realizado_val = float(sem_item[1])
                else:
                    realizado_val = float(sem_item)
        except Exception:
            realizado_val = None

        # fallback: usa o comportamento antigo (10% do total dos 19 clientes) se não tivermos os totais globais
        if realizado_val is None:
            realizado_val = totais['semanas'][f'semana_{semana_num}']['realizado']

        totais['despesas_semanas'][f'semana_{semana_num}'] = {
            'projetado': projetado_val,
            'realizado': realizado_val
        }
    
    # Total de despesas gerais (soma de todas as semanas)
    totais['despesas_gerais']['projetado'] = sum([totais['despesas_semanas'][f'semana_{i}']['projetado'] for i in range(1, 6)])
    totais['despesas_gerais']['realizado'] = sum([totais['despesas_semanas'][f'semana_{i}']['realizado'] for i in range(1, 6)])
    
    # Resultado = Total - Despesas
    totais['resultado']['projetado'] = totais['total_geral']['projetado'] - totais['despesas_gerais']['projetado']
    totais['resultado']['realizado'] = totais['total_geral']['realizado'] - totais['despesas_gerais']['realizado']
    
    return totais


def build_dashboard_data_with_filters(mes, ano, limit_recent=20):
    """Coleta dados filtrados por mês/ano incluindo projeções."""
    conn = get_connection()
    cur = conn.cursor()

    # Converte parâmetros para inteiro
    mes_int = int(mes)
    ano_int = int(ano)

    # Normaliza mes/ano como strings no formato esperado (mês com zero à esquerda)
    mes = f"{mes_int:02d}"
    ano = str(ano_int)

    # Lista específica de clientes para filtrar (incluindo variações encontradas no banco)
    clientes_filtro = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'GTFOODS BARUERI ', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'Saudali', 'VALENCIO JATAÍ'
    ]
    
    # Busca receita realizada (APENAS os 19 clientes pré-cadastrados e status recebido)
    # Lista FIXA dos 19 clientes permitidos (regra rígida)
    clientes_19_rigidos = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
    ]
    
    # Função para verificar se um cliente do banco pertence aos 19
    def cliente_pertence_aos_19(cliente_banco):
        cliente_upper = cliente_banco.upper().strip()
        for cliente_permitido in clientes_19_rigidos:
            cliente_permitido_upper = cliente_permitido.upper().strip()
            # Busca flexível: contém ou é contido
            if (cliente_permitido_upper in cliente_upper or 
                cliente_upper in cliente_permitido_upper or
                cliente_upper == cliente_permitido_upper):
                return True
        return False
    
    # Busca TODOS os registros dos 19 clientes no mês/ano (sem filtro de status)
    pattern = f"%/{mes}/{ano}%"
    
    # Query para pegar TODOS os registros do mês (independente do status) e filtrar em Python
    cur.execute("""
        SELECT cliente, valor_principal
        FROM contas_receber
        WHERE vencimento LIKE ?
    """, (pattern,))
    
    todos_registros = cur.fetchall()
    
    # Filtra apenas os que pertencem aos 19 clientes (sem filtro de status)
    total_receber_count = 0
    total_receber_valor = 0.0
    
    for cliente_banco, valor in todos_registros:
        if cliente_pertence_aos_19(cliente_banco):
            try:
                valor_float = float(valor)
                total_receber_valor += valor_float
                total_receber_count += 1
            except (ValueError, TypeError):
                continue
    
    # Simula o resultado no formato esperado
    contas_receber = (total_receber_count, total_receber_valor)

    # Busca dados de contas a pagar (TODOS os registros do mês/ano)
    # Puxar 100% dos custos onde o mês de vencimento corresponde ao filtro
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_pagar
        WHERE vencimento LIKE ?
    """, (pattern,))
    contas_pagar = cur.fetchone()

    # Busca dados de projeção
    cur.execute("""
        SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0), COUNT(*) 
        FROM projecao 
        WHERE mes = ? AND ano = ?
    """, (mes_int, ano_int))
    projecao_result = cur.fetchone()
    projecao_valor = projecao_result[0] or 0.0
    projecao_count = projecao_result[1] or 0

    # Busca valores já recebidos no mês (status = 'Recebido') 
    # apenas dos clientes que estão na projeção usando correspondência flexível
    
    # Mapa de correspondências entre nomes na projeção e no banco
    correspondencias = {
        'ADORO FOODS': ['ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS'],
        'MARFRIG GLOBAL FOODS': ['MARFRIG GLOBAL FOODS S A', 'MARFRIG - PROMISSAO', 'MARFRIG - ITUPEVA CD'],
        'GOLDPAC CD SAO JOSE DOS CAMPOS': ['GOLDPAO CD SAO JOSE DOS CAMPOS'],
        'GFOODS BARUERI': ['GTFOODS BARUERI', 'GTFOODS BARUERI '],
        'LATICINIO CARMONA': ['LATICINIO CARMONA'],
        'MINERVA S A': ['MINERVA S A'],
        'PAMPLONA JANDIRA': ['PAMPLONA JANDIRA'],
        'SANTA LUCIA': ['SANTA LUCIA'],
        'SAUDALI': ['Saudali'],
        'VALENCIA JATAI': ['Valencio Jataí']
    }
    
    # Busca os clientes que estão na projeção para o mês/ano específico
    cur.execute("""
        SELECT DISTINCT cliente 
        FROM projecao 
        WHERE mes = ? AND ano = ?
    """, (mes_int, ano_int))
    clientes_projecao = [row[0] for row in cur.fetchall()]

    # Lista de clientes permitidos (mesma usada na tela de projeção)
    clientes_permitidos = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
    ]

    # Função para resolver cliente armazenado na projeção para um nome canônico
    def resolver_cliente_projecao(valor):
        # tenta tratar como id
        try:
            cid = int(valor)
            if 1 <= cid <= len(clientes_permitidos):
                return clientes_permitidos[cid-1]
        except Exception:
            pass
        # tenta casar por igualdade ou uppercase
        if valor in clientes_permitidos:
            return valor
        up = str(valor).upper()
        for nome in clientes_permitidos:
            if up == nome.upper():
                return nome
        # fallback: retorna valor original
        return valor

    # Função para converter valores para float (aceita já float ou string em formato brasileiro)
    def convert_br_to_float(value_str):
        if value_str is None:
            return 0.0
        if isinstance(value_str, (int, float)):
            return float(value_str)
        try:
            s = str(value_str).strip()
            return float(s.replace('.', '').replace(',', '.'))
        except Exception:
            return 0.0

    # PARA O CARD "RECEITA REALIZADA": usar apenas status RECEBIDO dos 19 clientes
    # Busca todos os registros com status RECEBIDO no mês/ano e filtra pelos 19 clientes
    recebido_cond = "(UPPER(TRIM(status)) = 'RECEBIDO')"
    
    cur.execute(f"""
        SELECT cliente, valor_principal
        FROM contas_receber
        WHERE {recebido_cond}
        AND vencimento LIKE ?
    """, (pattern,))
    
    registros_recebidos = cur.fetchall()
    
    # Filtra apenas os que pertencem aos 19 clientes com status RECEBIDO
    recebido_count = 0
    recebido_valor = 0.0
    
    for cliente_banco, valor in registros_recebidos:
        if cliente_pertence_aos_19(cliente_banco):
            try:
                valor_float = float(valor)
                recebido_valor += valor_float
                recebido_count += 1
            except (ValueError, TypeError):
                continue

    # PARA O CARD "CONTAS A PAGAR" (valores realizados): usar apenas status RECEBIDO
    pago_cond = "(UPPER(TRIM(status)) = 'RECEBIDO')"
    
    cur.execute(f"""
        SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_pagar
        WHERE {pago_cond}
        AND vencimento LIKE ?
    """, (pattern,))
    
    contas_pagar_realizadas = cur.fetchone()

    # Busca lançamentos recentes para a tabela (filtrando por padrão de vencimento)
    cur.execute(f"""
        SELECT 
            cliente as nome,
            valor_principal,
            vencimento,
            status,
            'receber' as tipo
        FROM contas_receber 
        WHERE vencimento LIKE ?
        UNION ALL
        SELECT 
            fornecedor as nome,
            valor_principal,
            vencimento,
            status,
            'pagar' as tipo
        FROM contas_pagar 
        WHERE vencimento LIKE ?
        ORDER BY vencimento
        LIMIT ?
    """, (pattern, pattern, limit_recent))
    lancamentos = cur.fetchall()

    # Normaliza valores em lancamentos para float (previne TypeError em templates)
    normalized_lancamentos = []
    for row in lancamentos:
        nome = row[0]
        try:
            valor = convert_br_to_float(row[1])
        except Exception:
            valor = 0.0
        venc = row[2]
        status = row[3]
        tipo = row[4]
        normalized_lancamentos.append((nome, valor, venc, status, tipo))

    # Alertas (vencimentos próximos 7 dias no período filtrado)
    # Não confiamos em date()/strftime sobre strings no formato dd/mm/YYYY,
    # então buscamos os vencimentos no mês/ano e contamos em Python os que caem
    # nos próximos 7 dias.
    cur.execute("SELECT vencimento FROM contas_receber WHERE status != 'Pago' AND vencimento LIKE ?", (pattern,))
    vr = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT vencimento FROM contas_pagar WHERE status != 'Pago' AND vencimento LIKE ?", (pattern,))
    vp = [r[0] for r in cur.fetchall()]
    alertas = 0
    hoje = datetime.now().date()
    limite = hoje + timedelta(days=7)
    for v in vr + vp:
        try:
            # Espera formato 'DD/MM/YYYY'
            d = datetime.strptime(v.strip(), '%d/%m/%Y').date()
            if hoje <= d <= limite:
                alertas += 1
        except Exception:
            # ignora formatos desconhecidos
            continue

    conn.close()

    # Calcula totais - Garante que sejam float
    total_receber = float(contas_receber[1] or 0)
    total_pagar = float(contas_pagar[1] or 0)
    saldo_projetado = total_receber - total_pagar
    
    # Calcula rentabilidade dos CARDS DE CIMA (estatísticas/projeção)
    if total_pagar > 0:
        rentabilidade_estatisticas = ((total_receber - total_pagar) / total_pagar) * 100
    else:
        rentabilidade_estatisticas = 0.0 if total_receber == 0 else 100.0
    
    # Calcula rentabilidade dos CARDS DE BAIXO (realizados)
    contas_pagar_realizadas_valor = float(contas_pagar_realizadas[1] or 0)
    if contas_pagar_realizadas_valor > 0:
        rentabilidade_realizada = ((recebido_valor - contas_pagar_realizadas_valor) / contas_pagar_realizadas_valor) * 100
    else:
        rentabilidade_realizada = 0.0 if recebido_valor == 0 else 100.0
    
    # Garante que valores de projeção e recebido sejam float
    projecao_valor = float(projecao_valor)
    recebido_valor = float(recebido_valor)

    # Calcula percentuais para barras (valores numéricos, 0..100)
    # Percentual do saldo: heurística existente (75 se positivo, 25 se não)
    percent_saldo = 75 if saldo_projetado > 0 else 25

    # Percentual de recebido sobre projeção (0..100)
    if projecao_valor > 0:
        percent_receber = (recebido_valor / projecao_valor) * 100
    else:
        percent_receber = 0.0
    if percent_receber > 100:
        percent_receber = 100.0

    # Percentual de rentabilidade dos CARDS DE CIMA (estatísticas)
    if rentabilidade_estatisticas >= 50:
        percent_rentabilidade_estatisticas = 90  # Excelente rentabilidade
    elif rentabilidade_estatisticas >= 20:
        percent_rentabilidade_estatisticas = 70  # Boa rentabilidade
    elif rentabilidade_estatisticas >= 0:
        percent_rentabilidade_estatisticas = 50  # Rentabilidade positiva
    else:
        percent_rentabilidade_estatisticas = 25  # Rentabilidade negativa

    # Percentual de rentabilidade dos CARDS DE BAIXO (realizados)
    if rentabilidade_realizada >= 50:
        percent_rentabilidade_realizada = 90  # Excelente rentabilidade
    elif rentabilidade_realizada >= 20:
        percent_rentabilidade_realizada = 70  # Boa rentabilidade
    elif rentabilidade_realizada >= 0:
        percent_rentabilidade_realizada = 50  # Rentabilidade positiva
    else:
        percent_rentabilidade_realizada = 25  # Rentabilidade negativa

    # Textos formatados para exibição (percentual com 1 casa decimal)
    percent_receber_text = f"{percent_receber:.1f}%"
    rentabilidade_estatisticas_text = f"{rentabilidade_estatisticas:.1f}%"
    rentabilidade_realizada_text = f"{rentabilidade_realizada:.1f}%"

    return {
        'total_receber': formatar_valor_brasileiro(total_receber),
        'total_receber_raw': total_receber,
        'total_pagar': formatar_valor_brasileiro(total_pagar),
        'total_pagar_raw': total_pagar,
        'saldo_projetado': formatar_valor_brasileiro(saldo_projetado),
        'saldo_projetado_raw': saldo_projetado,
        'total_lancamentos': (contas_receber[0] or 0) + (contas_pagar[0] or 0),
        'alertas': alertas,
        'lancamentos': normalized_lancamentos,
        'projecao_receber': formatar_valor_brasileiro(projecao_valor),
        'projecao_receber_raw': projecao_valor,
        'projecao_receber_count': projecao_count,
        'receita_realizada': formatar_valor_brasileiro(recebido_valor),
        'receita_realizada_raw': recebido_valor,
        'receita_realizada_count': recebido_count,
        'contas_pagar_realizadas': formatar_valor_brasileiro(contas_pagar_realizadas[1] or 0),
        'contas_pagar_realizadas_raw': contas_pagar_realizadas[1] or 0,
        'contas_pagar_realizadas_count': contas_pagar_realizadas[0] or 0,
        # Rentabilidades separadas
        'rentabilidade_estatisticas': rentabilidade_estatisticas_text,
        'rentabilidade_estatisticas_raw': rentabilidade_estatisticas,
        'rentabilidade_realizada': rentabilidade_realizada_text,
        'rentabilidade_realizada_raw': rentabilidade_realizada,
        # percentuais para barras (numéricos e texto)
        'percent_saldo': percent_saldo,
        'percent_receber': percent_receber,
        'percent_receber_text': percent_receber_text,
        'percent_rentabilidade_estatisticas': percent_rentabilidade_estatisticas,
        'percent_rentabilidade_realizada': percent_rentabilidade_realizada
    }


def build_dashboard_data(limit_recent=20):
    """Coleta dados de contas a pagar/receber e retorna o dicionário usado no dashboard."""
    conn = get_connection()
    cur = conn.cursor()

    # Busca dados de contas a receber
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) 
        FROM contas_receber 
        WHERE status != 'Pago'
    """)
    contas_receber = cur.fetchone()

    # Busca dados de contas a pagar
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(valor_principal), 0) 
        FROM contas_pagar 
        WHERE status != 'Pago'
    """)
    contas_pagar = cur.fetchone()

    # Busca lançamentos recentes para a tabela
    cur.execute(f"""
        SELECT 
            cliente as nome,
            valor_principal,
            vencimento,
            status,
            'receber' as tipo
        FROM contas_receber 
        WHERE status != 'Pago'
        UNION ALL
        SELECT 
            fornecedor as nome,
            valor_principal,
            vencimento,
            status,
            'pagar' as tipo
        FROM contas_pagar 
        WHERE status != 'Pago'
        ORDER BY vencimento
        LIMIT {limit_recent}
    """)
    lancamentos = cur.fetchall()

    # Busca alertas (vencimentos próximos)
    cur.execute("""
        SELECT COUNT(*) 
        FROM (
            SELECT vencimento FROM contas_receber WHERE status != 'Pago'
            UNION ALL
            SELECT vencimento FROM contas_pagar WHERE status != 'Pago'
        ) 
        WHERE date(vencimento) <= date('now', '+7 days')
    """)
    alertas = cur.fetchone()[0]

    conn.close()

    # Calcula saldo projetado
    total_receber = contas_receber[1] or 0
    total_pagar = contas_pagar[1] or 0
    saldo_projetado = total_receber - total_pagar

    # Prepara dados para o template
    dashboard_data = {
        'total_receber': formatar_valor_brasileiro(total_receber),
        'total_receber_raw': total_receber,
        'total_pagar': formatar_valor_brasileiro(total_pagar),
        'total_pagar_raw': total_pagar,
        'saldo_projetado': formatar_valor_brasileiro(saldo_projetado),
        'saldo_projetado_raw': saldo_projetado,
        'total_lancamentos': (contas_receber[0] or 0) + (contas_pagar[0] or 0),
        'alertas': alertas,
        'lancamentos': lancamentos
    }

    return dashboard_data


# Painel removido - estava causando erro com arquivos XLSX
# Função build_dashboard_data_filtered também removida


# API do painel removida - estava causando erro com arquivos XLSX


@app.route("/projecao", methods=["GET", "POST"])
@login_required
def projecao():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        mes = int(request.form["mes"])
        ano = int(request.form["ano"])

        # Salva as projeções
        for key, value in request.form.items():
            if key.startswith("cliente_") and value.strip():
                _, cliente_id, dia = key.split("_")
                cliente_id = int(cliente_id)
                dia = int(dia)
                valor = float(value.replace(".", "").replace(",", "."))

                # Remove duplicado
                cur.execute("""
    
    # Se o usuário escolheu um MÊS válido (mes != 'Todos'), aplicar filtro por mês (ano pode ser 'Todos')
    # Se ano for 'Todos' usamos o ano atual como fallback para buscar projeções/lançamentos naquele mês do ano atual.
    from datetime import datetime
    now = datetime.now()
    if mes and mes != 'Todos':
        # se o ano for 'Todos' ou vazio, usar ano atual
        ano_param = ano if ano and ano != 'Todos' else str(now.year)
        data = build_dashboard_data_with_filters(mes, ano_param, status_filter=status_filter, client_filter=client_filter, min_value=min_value, max_value=max_value, search=search)
    elif ano and ano != 'Todos':
        # caso apenas ano seja informado, filtrar por ano (mês será vazio e a função tratará)
        mes_param = mes if mes and mes != 'Todos' else f"{now.month:02d}"
        data = build_dashboard_data_with_filters(mes_param, ano, status_filter=status_filter, client_filter=client_filter, min_value=min_value, max_value=max_value, search=search)
    else:
        # nenhum filtro de mês/ano: usar agregador geral
        data = build_dashboard_data()
                """, (cliente_id, dia, mes, ano, valor))

        conn.commit()
        flash("Projeção salva com sucesso!", "success")

    # Lista específica de clientes para a projeção (EXATAMENTE como definido)
    clientes_permitidos = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
    ]

    # Sempre apresentar exatamente os 19 clientes na ordem definida.
    # Cada cliente recebe um id sequencial (1..19) usado no formulário da matriz.
    clientes = [(i+1, nome) for i, nome in enumerate(clientes_permitidos)]

    conn.close()
    return render_template("projecao.html", clientes=clientes)


@app.route('/api/projecao', methods=['GET'])
def api_get_projecao():
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    if not mes or not ano:
        return jsonify({'status': 'error', 'message': 'mes e ano são obrigatórios'}), 400

    conn = get_connection()
    cur = conn.cursor()
    # Lista fixa de nomes (mesma ordem usada na tela de projeção)
    clientes_permitidos = [
        'ADORO', 'ADORO S.A.', 'ADORO SAO CARLOS', 'AGRA FOODS', 'ALIBEM', 'FRIBOI',
        'GOLDPAO CD SAO JOSE DOS CAMPOS', 'GTFOODS BARUERI', 'JK DISTRIBUIDORA', 
        'LATICINIO CARMONA', 'MARFRIG - ITUPEVA CD', 'MARFRIG - PROMISSAO', 
        'MARFRIG GLOBAL FOODS S A', 'MINERVA S A', 'PAMPLONA JANDIRA', 
        'PEIXES MEGGS PESCADOS LTDA - SJBV', 'SANTA LUCIA', 'SAUDALI', 'VALENCIO JATAÍ'
    ]

    # Inicializa estrutura com zeros para todos os 19 clientes
    data = {nome: [0.0] * 31 for nome in clientes_permitidos}

    # Busca registros salvos na tabela projecao (cliente pode ser id ou nome)
    cur.execute("SELECT cliente, dia, valor FROM projecao WHERE mes = ? AND ano = ?", (mes, ano))
    rows = cur.fetchall()

    # Função auxiliar para obter nome do cliente a partir do valor armazenado
    def resolver_nome(cliente_field):
        # se for número, tenta mapear para a lista (id baseado em 1)
        try:
            cid = int(cliente_field)
            if 1 <= cid <= len(clientes_permitidos):
                return clientes_permitidos[cid-1]
        except Exception:
            pass
        # caso contrário, tenta casar por substring exata
        if cliente_field in clientes_permitidos:
            return cliente_field
        # tenta uppercase comparando sem acentos simples
        up = cliente_field.upper()
        for nome in clientes_permitidos:
            if up == nome.upper():
                return nome
        # fallback: retorna o campo original
        return cliente_field

    for cliente_field, dia, valor in rows:
        nome = resolver_nome(cliente_field)
        if nome not in data:
            # ignora qualquer cliente fora da lista permitida
            continue
        if 1 <= dia <= 31:
            try:
                data[nome][dia-1] = float(valor)
            except Exception:
                data[nome][dia-1] = 0.0

    linhas = []
    for nome in clientes_permitidos:
        linhas.append({'cliente': nome, 'valores': data[nome]})

    conn.close()
    return jsonify({'status': 'success', 'linhas': linhas})


@app.route('/api/projecao', methods=['POST'])
def api_post_projecao():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Esperado JSON'}), 400

    data = request.get_json()
    mes = data.get('mes')
    ano = data.get('ano')
    linhas = data.get('linhas', [])

    if not mes or not ano:
        return jsonify({'status': 'error', 'message': 'mes e ano são obrigatórios'}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        # substitui todas as entradas do mês/ano (delete + insert)
        cur.execute("DELETE FROM projecao WHERE mes = ? AND ano = ?", (mes, ano))

        for linha in linhas:
            cliente = linha.get('cliente', '')
            valores = linha.get('valores', [])
            # garante 31 posições
            for i in range(31):
                dia = i + 1
                try:
                    valor = float(valores[i]) if i < len(valores) else 0.0
                except Exception:
                    valor = 0.0
                cur.execute("INSERT INTO projecao (cliente, dia, mes, ano, valor) VALUES (?, ?, ?, ?, ?)", (cliente, dia, mes, ano, valor))

        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()


@app.route("/dashboard")
@login_required
def dashboard():
    # Obter mês e ano atual como padrão
    mes_atual = request.args.get('mes', datetime.now().month)
    ano_atual = request.args.get('ano', datetime.now().year)
    
    # Buscar dados do FRZ para o dashboard
    dados_frz = build_dados_frz(int(mes_atual), int(ano_atual))
    
    # Preparar dados para os gráficos
    dados_dashboard = {
        'mes': mes_atual,
        'ano': ano_atual,
        'frz': dados_frz
    }
    
    return render_template("dashboard.html", dados=dados_dashboard)


@app.route("/resumo")
@login_required
def resumo():
    """Página de resumo executivo com KPIs principais e alertas"""
    from datetime import datetime, timedelta
    
    # Pegar parâmetros de filtro (padrão: mês atual)
    mes = request.args.get('mes', datetime.now().month)
    ano = request.args.get('ano', datetime.now().year)
    
    try:
        mes = int(mes)
        ano = int(ano)
    except (ValueError, TypeError):
        mes = datetime.now().month
        ano = datetime.now().year
    
    conn = get_connection()
    cur = conn.cursor()
    
    # ===== CALCULAR KPIs PRINCIPAIS =====
    
    # 1. RECEITA TOTAL (realizada vs projetada)
    pattern = f"%/{mes:02d}/{ano}%"
    
    # Receita realizada (apenas clientes dos 19 e status RECEBIDO)
    # Usar sistema inteligente para filtrar clientes principais
    condicao_clientes, clientes_reais = criar_condicao_clientes_principais(
        cur, 'contas_receber', 
        f"WHERE vencimento LIKE '{pattern}' AND UPPER(status) = 'RECEBIDO'"
    )
    
    cur.execute(f"""
        SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_receber
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO' 
        AND {condicao_clientes}
    """, [pattern] + clientes_reais)
    receita_realizada = cur.fetchone()[0] or 0.0
    
    # Total A Receber (TODOS os status + 19 clientes + mês/ano) para detalhamento da receita
    condicao_clientes_total, clientes_reais_total = criar_condicao_clientes_principais(
        cur, 'contas_receber', 
        f"WHERE vencimento LIKE '{pattern}'"
    )
    
    cur.execute(f"""
        SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_receber
        WHERE vencimento LIKE ? 
        AND {condicao_clientes_total}
    """, [pattern] + clientes_reais_total)
    receita_total_a_receber = cur.fetchone()[0] or 0.0
    
    # Receita projetada (meta da projeção)
    cur.execute("""
        SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0)
        FROM projecao 
        WHERE mes = ? AND ano = ?
    """, (mes, ano))
    receita_meta = cur.fetchone()[0] or 0.0
    
    # 2. CONTAS A RECEBER (total e vencidas) - filtrado por mês/ano + 19 clientes + Status Pendente
    # Usar sistema inteligente para filtrar clientes principais
    condicao_clientes_receber, clientes_reais_receber = criar_condicao_clientes_principais(
        cur, 'contas_receber', 
        f"WHERE vencimento LIKE '{pattern}' AND UPPER(status) = 'PENDENTE'"
    )
    
    cur.execute(f"""
        SELECT 
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0),
            COUNT(*)
        FROM contas_receber
        WHERE UPPER(status) = 'PENDENTE'
        AND vencimento LIKE ?
        AND {condicao_clientes_receber}
    """, [pattern] + clientes_reais_receber)
    receber_dados = cur.fetchone()
    total_receber = receber_dados[0] or 0.0
    count_receber = receber_dados[1] or 0
    
    # Contas vencidas (vencimento < hoje) - filtrado por mês/ano + 19 clientes + Status Pendente
    hoje = datetime.now().strftime("%d/%m/%Y")
    cur.execute(f"""
        SELECT 
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0),
            COUNT(*)
        FROM contas_receber
        WHERE UPPER(status) = 'PENDENTE'
        AND vencimento LIKE ?
        AND {condicao_clientes_receber}
        AND LENGTH(vencimento) = 10
        AND DATE(SUBSTR(vencimento, 7, 4) || '-' || SUBSTR(vencimento, 4, 2) || '-' || SUBSTR(vencimento, 1, 2)) < DATE('now')
    """, [pattern] + clientes_reais_receber)
    receber_vencidas_dados = cur.fetchone()
    receber_vencidas = receber_vencidas_dados[0] or 0.0
    count_receber_vencidas = receber_vencidas_dados[1] or 0
    
    # 3. CONTAS A PAGAR (total e vencidas) - filtrado por mês/ano
    cur.execute("""
        SELECT 
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0),
            COUNT(*)
        FROM contas_pagar
        WHERE status != 'PAGO' AND status != 'Pago'
        AND vencimento LIKE ?
    """, (pattern,))
    pagar_dados = cur.fetchone()
    total_pagar = pagar_dados[0] or 0.0
    count_pagar = pagar_dados[1] or 0
    
    # Contas vencidas (vencimento < hoje) - filtrado por mês/ano
    cur.execute("""
        SELECT 
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0),
            COUNT(*)
        FROM contas_pagar
        WHERE status != 'PAGO' AND status != 'Pago'
        AND vencimento LIKE ?
        AND LENGTH(vencimento) = 10
        AND DATE(SUBSTR(vencimento, 7, 4) || '-' || SUBSTR(vencimento, 4, 2) || '-' || SUBSTR(vencimento, 1, 2)) < DATE('now')
    """, (pattern,))
    pagar_vencidas_dados = cur.fetchone()
    pagar_vencidas = pagar_vencidas_dados[0] or 0.0
    count_pagar_vencidas = pagar_vencidas_dados[1] or 0
    
    # 4. FLUXO DE CAIXA (simplificado: receber - pagar)
    fluxo_caixa = total_receber - total_pagar
    
    # 5. TOP 5 CLIENTES DO MÊS (19 clientes principais, por valor total - recebido + pendente)
    cur.execute(f"""
        SELECT 
            cliente,
            COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0) as total,
            COALESCE(SUM(CASE WHEN UPPER(status) = 'RECEBIDO' THEN CAST(valor_principal AS REAL) ELSE 0 END), 0.0) as recebido,
            COALESCE(SUM(CASE WHEN UPPER(status) = 'PENDENTE' THEN CAST(valor_principal AS REAL) ELSE 0 END), 0.0) as pendente
        FROM contas_receber
        WHERE vencimento LIKE ?
        AND {condicao_clientes}
        GROUP BY cliente
        ORDER BY total DESC
        LIMIT 5
    """, [pattern] + clientes_reais)
    top_clientes = cur.fetchall()
    
    # ===== DADOS COMPARATIVOS E PROJEÇÕES =====
    
    # Calcular mês anterior
    mes_anterior = mes - 1 if mes > 1 else 12
    ano_anterior = ano if mes > 1 else ano - 1
    pattern_anterior = f"%/{mes_anterior:02d}/{ano_anterior}%"
    
    # Receita do período anterior (também filtrada pelos 19 clientes)
    condicao_clientes_anterior, clientes_reais_anterior = criar_condicao_clientes_principais(
        cur, 'contas_receber', 
        f"WHERE vencimento LIKE '{pattern_anterior}' AND UPPER(status) = 'RECEBIDO'"
    )
    
    cur.execute(f"""
        SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
        FROM contas_receber
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
        AND {condicao_clientes_anterior}
    """, [pattern_anterior] + clientes_reais_anterior)
    receita_anterior = cur.fetchone()[0] or 0.0
    
    # Crescimento percentual
    crescimento_receita = ((receita_realizada - receita_anterior) / receita_anterior * 100) if receita_anterior > 0 else 0
    
    # Calcular largura da barra de crescimento (entre 10% e 100%)
    barra_crescimento = max(10, min(100, 50 + crescimento_receita))
    
    # Projeção de fluxo de caixa para próximos 3 meses: Projeção - A Pagar
    projecao_fluxo = []
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for i in range(1, 4):  # Próximos 3 meses
        mes_proj = mes + i
        ano_proj = ano
        if mes_proj > 12:
            mes_proj -= 12
            ano_proj += 1
        
        # Buscar dados da projeção (todos os clientes da tabela projecao)
        cur.execute("""
            SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0) 
            FROM projecao
            WHERE mes = ? AND ano = ?
        """, (mes_proj, ano_proj))
        receita_projetada = cur.fetchone()[0] or 0.0
        
        # Buscar contas a pagar para o mês (status = 'PENDENTE')
        cur.execute("""
            SELECT COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0)
            FROM contas_pagar
            WHERE vencimento LIKE ? AND UPPER(status) = 'PENDENTE'
        """, (f"%/{mes_proj:02d}/{ano_proj}%",))
        contas_a_pagar = cur.fetchone()[0] or 0.0
        
        # Fluxo = Projeção - A Pagar
        fluxo_projetado = receita_projetada - contas_a_pagar
        
        projecao_fluxo.append({
            'nome': meses_nomes[mes_proj - 1],
            'valor': fluxo_projetado
        })
    
    # Alertas de fluxo
    alertas_fluxo = [proj for proj in projecao_fluxo if proj['valor'] < 0]
    
    # Cálculo de inadimplência
    total_títulos = count_receber + count_pagar
    títulos_vencidos = count_receber_vencidas + count_pagar_vencidas
    percentual_inadimplencia = (títulos_vencidos / total_títulos * 100) if total_títulos > 0 else 0
    
    # Ticket médio (baseado nos 19 clientes)
    cur.execute(f"""
        SELECT COUNT(*) FROM contas_receber 
        WHERE vencimento LIKE ? AND UPPER(status) = 'RECEBIDO'
        AND {condicao_clientes}
    """, [pattern] + clientes_reais)
    total_transacoes = cur.fetchone()[0] or 1
    ticket_medio = receita_realizada / total_transacoes if total_transacoes > 0 else 0
    
    # ===== CALCULAR STATUS GERAL =====
    # Lógica: Verde se receita > 80% da meta e fluxo positivo
    #         Amarelo se receita > 50% da meta OU fluxo positivo
    #         Vermelho caso contrário
    
    percentual_meta = (receita_realizada / receita_meta * 100) if receita_meta > 0 else 0
    
    if percentual_meta >= 80 and fluxo_caixa >= 0:
        status_geral = {"cor": "success", "texto": "Situação Estável", "emoji": "🟢"}
    elif percentual_meta >= 50 or fluxo_caixa >= 0:
        status_geral = {"cor": "warning", "texto": "Atenção Necessária", "emoji": "🟡"}
    else:
        status_geral = {"cor": "danger", "texto": "Ação Urgente", "emoji": "🔴"}
    
    # ===== ALERTAS CONTEXTUAIS APRIMORADOS =====
    alertas = []
    
    if count_receber_vencidas > 0:
        alertas.append(f"{count_receber_vencidas} conta(s) a receber vencida(s) - R$ {receber_vencidas:,.0f}")
    
    if count_pagar_vencidas > 0:
        alertas.append(f"{count_pagar_vencidas} conta(s) a pagar vencida(s) - R$ {pagar_vencidas:,.0f}")
    
    if percentual_meta < 50:
        alertas.append(f"Meta do mês: apenas {percentual_meta:.1f}% atingida")
    
    if fluxo_caixa < 0:
        alertas.append(f"Fluxo de caixa negativo - R$ {fluxo_caixa:,.0f}")
    
    if percentual_inadimplencia > 5:
        alertas.append(f"Alta inadimplência: {percentual_inadimplencia:.1f}% dos títulos vencidos")
    
    if crescimento_receita < -10:
        alertas.append(f"Queda na receita: {crescimento_receita:.1f}% vs mês anterior")
    
    if len(alertas_fluxo) > 1:
        alertas.append(f"Fluxo de caixa negativo projetado para {len(alertas_fluxo)} meses")
    
    if not alertas:
        alertas.append("Nenhum alerta crítico no momento")
    
    # ===== ESTRUTURA DE DADOS PARA O TEMPLATE =====
    dados_resumo = {
        'mes': mes,
        'ano': ano,
        'status_geral': status_geral,
        'kpis': {
            'receita': {
                'realizada': receita_realizada,
                'meta': receita_meta,
                'percentual': percentual_meta,
                'total_a_receber': receita_total_a_receber,
                'percentual_falta_a_receber': ((receita_total_a_receber - receita_realizada) / receita_total_a_receber * 100) if receita_total_a_receber > 0 else 0,
                'percentual_falta_planejamento': ((receita_meta - receita_realizada) / receita_meta * 100) if receita_meta > 0 else 0
            },
            'fluxo_caixa': {
                'valor': fluxo_caixa,
                'positivo': fluxo_caixa >= 0
            },
            'receber': {
                'total': total_receber,
                'vencidas': receber_vencidas,
                'count': count_receber,
                'count_vencidas': count_receber_vencidas
            },
            'pagar': {
                'total': total_pagar,
                'vencidas': pagar_vencidas,
                'count': count_pagar,
                'count_vencidas': count_pagar_vencidas
            }
        },
        'comparacao': {
            'mes_anterior': mes_anterior,
            'ano_anterior': ano_anterior,
            'receita_anterior': receita_anterior,
            'crescimento_receita': crescimento_receita,
            'barra_crescimento': barra_crescimento
        },
        'projecao_fluxo': projecao_fluxo,
        'alertas_fluxo': alertas_fluxo,
        'inadimplencia': {
            'percentual': percentual_inadimplencia,
            'total_vencidos': títulos_vencidos,
            'total_titulos': total_títulos
        },
        'ticket_medio': ticket_medio,
        'top_clientes': top_clientes,
        'alertas': alertas
    }
    
    conn.close()
    return render_template('resumo.html', dados=dados_resumo)


@app.route("/consolidacao")
@login_required
def consolidacao():
    return "<h2>Página de Consolidação (em construção)</h2>"


# ============================
# IMPORTAÇÃO DE ARQUIVOS
# ============================

@app.route("/importacao", methods=["GET", "POST"])
@login_required
def importacao():
    if request.method == "POST":
        if "files" not in request.files:
            flash("Nenhum arquivo enviado!", "error")
            return redirect(url_for("importacao"))

        files = request.files.getlist("files")
        if not files or files[0].filename == "":
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(url_for("importacao"))

        for file in files:
            msg = importar_arquivo(file)
            flash(f"{file.filename}: {msg}", "success")

        return redirect(url_for("importacao"))

    # lista de arquivos enviados (pasta uploads)
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
    uploads = []
    if os.path.isdir(uploads_dir):
        for fname in sorted(os.listdir(uploads_dir), reverse=True):
            fpath = os.path.join(uploads_dir, fname)
            try:
                mtime = os.path.getmtime(fpath)
                size = os.path.getsize(fpath)

                # Gera um nome de exibição amigável: remove timestamp inserido pelos uploads temporários
                display_name = fname
                # Padrão: base.TIMESTAMP.ext  (ex: contas-a-receber.1758628304.csv)
                parts = fname.split('.')
                if len(parts) >= 3 and parts[-2].isdigit():
                    # junta a parte base e a extensão
                    display_name = '.'.join(parts[:-2] + [parts[-1]])

                uploads.append({
                    'name': fname,            # nome do arquivo no disco (usado para download)
                    'display_name': display_name,  # nome amigável mostrado na UI
                    'mtime': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': size
                })
            except Exception:
                continue

    return render_template("importacao.html", uploads=uploads)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
    return send_from_directory(uploads_dir, filename)


# ============================
# EXECUÇÃO
# ============================

if __name__ == "__main__":
    # Inicializa banco ao iniciar o servidor
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

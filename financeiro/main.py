from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_from_directory
from .database import init_db, get_connection
from .importacao import importar_arquivo
import bcrypt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "frz-secret"  # chave de sessão

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
    
    # Calcular totais gerais
    dados['totais'] = calcular_totais_frz(dados)
    
    conn.close()
    return dados


def calcular_semanas_sabado_sexta(mes, ano):
    """Calcula as 5 semanas do mês no formato sábado-sexta, evitando sobreposição entre meses."""
    from datetime import datetime, timedelta
    
    # Primeiro dia do mês
    primeiro_dia = datetime(ano, mes, 1)
    
    # Encontrar o primeiro sábado que contém ou antecede o primeiro dia do mês
    # weekday(): 0=segunda, 1=terça, ..., 5=sábado, 6=domingo
    dias_atras_para_sabado = (primeiro_dia.weekday() + 2) % 7
    primeiro_sabado = primeiro_dia - timedelta(days=dias_atras_para_sabado)
    
    # AJUSTE: Se o primeiro sábado for de um mês anterior E já teve muitos dias desse mês anterior,
    # avançar para o primeiro sábado que está majoritariamente no mês atual
    if primeiro_sabado.month != mes:
        # Se o primeiro sábado é do mês anterior, verificar se a maioria da semana está no mês atual
        fim_semana = primeiro_sabado + timedelta(days=6)
        dias_no_mes_atual = 0
        
        # Contar quantos dias da semana estão no mês atual
        for i in range(7):
            dia_semana = primeiro_sabado + timedelta(days=i)
            if dia_semana.month == mes:
                dias_no_mes_atual += 1
        
        # Se menos de 4 dias estão no mês atual (menos da metade), pular para próximo sábado
        if dias_no_mes_atual < 4:
            primeiro_sabado += timedelta(days=7)
    
    semanas = []
    for i in range(5):
        inicio_semana = primeiro_sabado + timedelta(weeks=i)
        fim_semana = inicio_semana + timedelta(days=6)  # sexta-feira
        
        # Label mostra apenas os dias
        label = f"SEMANA {inicio_semana.day} A {fim_semana.day}"
        
        semanas.append({
            'inicio': inicio_semana,
            'fim': fim_semana,
            'label': label
        })
    
    return semanas


def buscar_valor_projetado(cur, cliente, semana, mes, ano):
    """Busca valor projetado para o cliente na semana especificada."""
    # Buscar na tabela projecao
    cur.execute("""
        SELECT SUM(valor) FROM projecao 
        WHERE cliente = ? AND mes = ? AND ano = ? 
        AND dia BETWEEN ? AND ?
    """, (cliente, mes, ano, semana['inicio'].day, semana['fim'].day))
    
    resultado = cur.fetchone()[0]
    return resultado if resultado else 0.0


def buscar_valor_realizado(cur, cliente, semana, mes, ano):
    """Busca valor realizado (recebido) para o cliente na semana especificada."""
    from datetime import datetime
    
    # Converter datas da semana para formato de comparação
    inicio_semana = semana['inicio']
    fim_semana = semana['fim']
    
    # Buscar na tabela contas_receber com status 'RECEBIDO' 
    # filtrando por data de vencimento dentro da semana específica
    # Formato esperado: DD/MM/YYYY
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
        ano,  # Ano (YYYY)
        mes,  # Mês (MM)
        inicio_semana.day,  # Dia inicial da semana
        fim_semana.day      # Dia final da semana
    ))
    
    resultado = cur.fetchone()[0]
    return resultado if resultado else 0.0


def calcular_totais_frz(dados):
    """Calcula totais gerais, despesas e resultado do FRZ."""
    totais = {
        'total_geral': {'projetado': 0, 'realizado': 0},
        'despesas_gerais': {'projetado': 0, 'realizado': 0},
        'resultado': {'projetado': 0, 'realizado': 0}
    }
    
    # Somar todos os clientes
    for cliente, valores in dados['clientes'].items():
        totais['total_geral']['projetado'] += valores['total_mes']['projetado']
        totais['total_geral']['realizado'] += valores['total_mes']['realizado']
    
    # TODO: Implementar lógica de despesas gerais baseada nos dados reais
    # Por enquanto, usar 10% do total como estimativa
    totais['despesas_gerais']['projetado'] = totais['total_geral']['projetado'] * 0.1
    totais['despesas_gerais']['realizado'] = totais['total_geral']['realizado'] * 0.1
    
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
                    DELETE FROM projecao
                    WHERE cliente = ? AND dia = ? AND mes = ? AND ano = ?
                """, (cliente_id, dia, mes, ano))

                cur.execute("""
                    INSERT INTO projecao (cliente, dia, mes, ano, valor)
                    VALUES (?, ?, ?, ?, ?)
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
def dashboard():
    return "<h2>Página de Dashboard (em construção)</h2>"


@app.route("/resumo")
def resumo():
    return "<h2>Página de Resumo (em construção)</h2>"


@app.route("/consolidacao")
def consolidacao():
    return "<h2>Página de Consolidação (em construção)</h2>"


# ============================
# IMPORTAÇÃO DE ARQUIVOS
# ============================

@app.route("/importacao", methods=["GET", "POST"])
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
                uploads.append({
                    'name': fname,
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
    # Inicializa banco ao iniciar o servidor localmente
    init_db()
    app.run(debug=True)

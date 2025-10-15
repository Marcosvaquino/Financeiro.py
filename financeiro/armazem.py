from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
import pandas as pd
import os
import calendar
from datetime import datetime, timedelta
from collections import defaultdict
from werkzeug.utils import secure_filename

bp = Blueprint('armazem', __name__, url_prefix='/armazem')

# Caminho do arquivo
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ARMAZEM_FILE = os.path.join(UPLOAD_FOLDER, 'ARMAZEM.xlsx')


def carregar_dados_armazem():
    """Carrega e processa os dados da planilha ARMAZEM (ambas as abas: SJC e JAC)"""
    try:
        if not os.path.exists(ARMAZEM_FILE):
            return None
        
        # ===== LER ABA SJC =====
        df_sjc = pd.read_excel(ARMAZEM_FILE, sheet_name='SJC', header=None)
        df_sjc = df_sjc.iloc[3:].reset_index(drop=True)  # Pula as 3 primeiras linhas
        
        df_sjc.columns = [
            'Data', 'Mes', 
            'Geral_Carros', 'Geral_Peso',
            'Mafrig_Foods_Carros', 'Mafrig_Foods_Peso',
            'Mafrig_Atacado_Carros', 'Mafrig_Atacado_Peso',
            'Gold_Pao_Carros', 'Gold_Pao_Peso',
            'Compartilhado_Carros', 
            'Valencio_Peso', 'Alibem_Agra_Peso', 'Saudali_Peso', 'Pamplona_Peso', 'GT_Foods_Peso', 'Santa_Lucia_Peso',
            'Compartilhado_Peso',
            'Friboi_Carros', 'Friboi_Peso',
            'Total_SJC_Carros', 'Total_SJC_Peso'
        ]
        
        df_sjc['Filial'] = 'SJC'
        
        # Colunas que não existem em SJC (preenche com 0)
        df_sjc['Adoro_Carros'] = 0
        df_sjc['Adoro_Peso'] = 0
        df_sjc['Vista_Foods_Carros'] = 0
        df_sjc['Vista_Foods_Peso'] = 0
        df_sjc['Mieggs_Carros'] = 0
        df_sjc['Mieggs_Peso'] = 0
        df_sjc['Minerva_JAC_Carros'] = 0
        df_sjc['Minerva_JAC_Peso'] = 0
        
        # ===== LER ABA JAC =====
        df_jac = pd.read_excel(ARMAZEM_FILE, sheet_name='JAC', header=None)
        df_jac = df_jac.iloc[3:].reset_index(drop=True)  # Pula as 3 primeiras linhas
        
        df_jac.columns = [
            'Data', 'Mes',
            'Geral_Carros', 'Geral_Peso',
            'Adoro_Carros', 'Adoro_Peso',
            'Vista_Foods_Carros', 'Vista_Foods_Peso',
            'Mieggs_Carros', 'Mieggs_Peso',
            'Minerva_JAC_Carros', 'Minerva_JAC_Peso',
            'Total_JAC_Carros', 'Total_JAC_Peso'
        ]
        
        df_jac['Filial'] = 'JAC'
        
        # Colunas que não existem em JAC (preenche com 0)
        df_jac['Mafrig_Foods_Carros'] = 0
        df_jac['Mafrig_Foods_Peso'] = 0
        df_jac['Mafrig_Atacado_Carros'] = 0
        df_jac['Mafrig_Atacado_Peso'] = 0
        df_jac['Gold_Pao_Carros'] = 0
        df_jac['Gold_Pao_Peso'] = 0
        df_jac['Compartilhado_Carros'] = 0
        df_jac['Valencio_Peso'] = 0
        df_jac['Alibem_Agra_Peso'] = 0
        df_jac['Saudali_Peso'] = 0
        df_jac['Pamplona_Peso'] = 0
        df_jac['GT_Foods_Peso'] = 0
        df_jac['Santa_Lucia_Peso'] = 0
        df_jac['Compartilhado_Peso'] = 0
        df_jac['Friboi_Carros'] = 0
        df_jac['Friboi_Peso'] = 0
        
        # ===== COMBINAR AS DUAS ABAS =====
        df = pd.concat([df_sjc, df_jac], ignore_index=True)
        
        # Converte data
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        
        # Remove linhas sem data
        df = df.dropna(subset=['Data'])
        
        # Converte colunas numéricas
        colunas_numericas = [col for col in df.columns if col not in ['Data', 'Mes', 'Filial']]
        for col in colunas_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Adiciona colunas de dia, mês e ano
        df['Dia'] = df['Data'].dt.day
        df['Mes_Num'] = df['Data'].dt.month
        df['Ano'] = df['Data'].dt.year
        
        return df
        
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
        return None


@bp.route('/')
def index():
    return render_template('armazem_standalone.html')


@bp.route('/importacao', methods=['GET', 'POST'])
def importacao():
    """Página e processamento de importação de arquivos do armazém"""
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo foi selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['arquivo']
        
        # Verifica se um arquivo foi realmente selecionado
        if file.filename == '':
            flash('Nenhum arquivo foi selecionado', 'error')
            return redirect(request.url)
        
        # Verifica a extensão do arquivo
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            flash('Formato de arquivo inválido. Use apenas .xlsx ou .xls', 'error')
            return redirect(request.url)
        
        try:
            # Garante que o diretório existe
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # Salva o arquivo com nome fixo
            filepath = os.path.join(UPLOAD_FOLDER, 'ARMAZEM.xlsx')
            file.save(filepath)
            
            # Tenta carregar o arquivo para validar
            df = carregar_dados_armazem()
            if df is None or df.empty:
                flash('Erro ao processar o arquivo. Verifique o formato.', 'error')
                return redirect(request.url)
            
            flash(f'✅ Arquivo importado com sucesso! {len(df)} registros carregados.', 'success')
            return redirect(url_for('armazem.index'))
            
        except Exception as e:
            flash(f'Erro ao importar arquivo: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET - mostra o formulário
    ultima_importacao = None
    if os.path.exists(ARMAZEM_FILE):
        timestamp = os.path.getmtime(ARMAZEM_FILE)
        ultima_importacao = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y às %H:%M')
    
    return render_template('armazem_importacao.html', ultima_importacao=ultima_importacao)


@bp.route('/api/dados', methods=['GET'])
def api_dados():
    """API para retornar dados do armazém com filtros"""
    try:
        df = carregar_dados_armazem()
        
        if df is None:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Filtros
        dia = request.args.get('dia')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        filial = request.args.get('filial')
        
        # Cria uma cópia para aplicar filtros
        df_filtrado = df.copy()
        
        # Aplica filtros
        if dia and dia != 'TODOS':
            df_filtrado = df_filtrado[df_filtrado['Dia'] == int(dia)]
        
        if mes and mes != 'TODOS':
            df_filtrado = df_filtrado[df_filtrado['Mes_Num'] == int(mes)]
        
        if ano and ano != 'TODOS':
            df_filtrado = df_filtrado[df_filtrado['Ano'] == int(ano)]
        
        if filial and filial != 'TODAS':
            df_filtrado = df_filtrado[df_filtrado['Filial'] == filial]
        
        # Calcula estatísticas gerais
        total_carros = int(df_filtrado['Geral_Carros'].sum())
        total_peso = float(df_filtrado['Geral_Peso'].sum())
        media_diaria_carros = float(df_filtrado['Geral_Carros'].mean()) if len(df_filtrado) > 0 else 0
        media_diaria_peso = float(df_filtrado['Geral_Peso'].mean()) if len(df_filtrado) > 0 else 0
        
        # === DADOS POR EMBARCADOR (TODOS, incluindo compartilhados) ===
        # IMPORTANTE: Ignora o filtro de FILIAL para mostrar sempre todas as filiais
        # Aplica apenas filtros de dia, mês e ano
        df_embarcadores = df.copy()
        
        if dia and dia != 'TODOS':
            df_embarcadores = df_embarcadores[df_embarcadores['Dia'] == int(dia)]
        
        if mes and mes != 'TODOS':
            df_embarcadores = df_embarcadores[df_embarcadores['Mes_Num'] == int(mes)]
        
        if ano and ano != 'TODOS':
            df_embarcadores = df_embarcadores[df_embarcadores['Ano'] == int(ano)]
        
        # SJC: Mafrig Foods, Friboi, Mafrig Atacado, Gold Pão, Compartilhados
        # JAC: Adoro, Vista Foods, Mieggs, Minerva
        embarcadores = {
            'MIEGGS (SJC)': {
                'carros': int(df_embarcadores[df_embarcadores['Filial'] == 'SJC']['Mafrig_Foods_Carros'].sum()),
                'peso': float(df_embarcadores[df_embarcadores['Filial'] == 'SJC']['Mafrig_Foods_Peso'].sum() / 1000)
            },
            'MIEGGS (JAC)': {
                'carros': int(df_embarcadores[df_embarcadores['Filial'] == 'JAC']['Mieggs_Carros'].sum()),
                'peso': float(df_embarcadores[df_embarcadores['Filial'] == 'JAC']['Mieggs_Peso'].sum() / 1000)
            },
            'FRIBOI': {
                'carros': int(df_embarcadores['Friboi_Carros'].sum()),
                'peso': float(df_embarcadores['Friboi_Peso'].sum() / 1000)
            },
            'MINERVA (SJC)': {
                'carros': int(df_embarcadores[df_embarcadores['Filial'] == 'SJC']['Mafrig_Atacado_Carros'].sum()),
                'peso': float(df_embarcadores[df_embarcadores['Filial'] == 'SJC']['Mafrig_Atacado_Peso'].sum() / 1000)
            },
            'MINERVA (JAC)': {
                'carros': int(df_embarcadores[df_embarcadores['Filial'] == 'JAC']['Minerva_JAC_Carros'].sum()),
                'peso': float(df_embarcadores[df_embarcadores['Filial'] == 'JAC']['Minerva_JAC_Peso'].sum() / 1000)
            },
            'GOLD PÃO': {
                'carros': int(df_embarcadores['Gold_Pao_Carros'].sum()),
                'peso': float(df_embarcadores['Gold_Pao_Peso'].sum() / 1000)
            },
            'MAFRIG (Compart)': {
                'carros': int(df_embarcadores['Compartilhado_Carros'].sum()),
                'peso': float((
                    df_embarcadores['Valencio_Peso'].sum() +
                    df_embarcadores['Alibem_Agra_Peso'].sum() +
                    df_embarcadores['Saudali_Peso'].sum() +
                    df_embarcadores['Pamplona_Peso'].sum() +
                    df_embarcadores['GT_Foods_Peso'].sum() +
                    df_embarcadores['Santa_Lucia_Peso'].sum()
                ) / 1000)
            },
            'FRZ LOG (Compart)': {
                'carros': int(df_embarcadores['Compartilhado_Carros'].sum()),
                'peso': float(df_embarcadores['Compartilhado_Peso'].sum() / 1000)
            },
            'ADORO': {
                'carros': int(df_embarcadores['Adoro_Carros'].sum()),
                'peso': float(df_embarcadores['Adoro_Peso'].sum() / 1000)
            },
            'VISTA FOODS': {
                'carros': int(df_embarcadores['Vista_Foods_Carros'].sum()),
                'peso': float(df_embarcadores['Vista_Foods_Peso'].sum() / 1000)
            }
        }
        
        # === DADOS MENSAIS (Gráfico de barras + linha) ===
        # IMPORTANTE: Este gráfico é afetado APENAS pelo filtro de ANO, não por dia/mês
        df_mensal = df.copy()  # Usa df original, não filtrado
        
        # Aplica apenas filtro de ano e filial
        if ano and ano != 'TODOS':
            df_mensal = df_mensal[df_mensal['Ano'] == int(ano)]
        
        if filial and filial != 'TODAS':
            df_mensal = df_mensal[df_mensal['Filial'] == filial]
        
        df_mensal['Ano_Mes'] = df_mensal['Data'].dt.to_period('M')
        
        mensal_agrupado = df_mensal.groupby('Ano_Mes').agg({
            'Geral_Carros': 'sum',
            'Geral_Peso': 'sum'
        }).reset_index()
        
        mensal_agrupado['Ano_Mes'] = mensal_agrupado['Ano_Mes'].astype(str)
        
        dados_mensais = []
        for _, row in mensal_agrupado.iterrows():
            dados_mensais.append({
                'mes': row['Ano_Mes'],
                'carros': int(row['Geral_Carros']),
                'peso': float(row['Geral_Peso'])
            })
        
        # === PESO POR FILIAL (Pizza) ===
        # Usa todos os dados (não filtrado) para mostrar distribuição anual
        peso_sjc = float(df[df['Filial'] == 'SJC']['Geral_Peso'].sum())
        peso_jac = float(df[df['Filial'] == 'JAC']['Geral_Peso'].sum()) if 'JAC' in df['Filial'].values else 0
        
        # Só mostra JAC se tiver dados
        if peso_jac > 0:
            peso_filiais = {
                'SJC': peso_sjc,
                'JAC': peso_jac
            }
        else:
            peso_filiais = {
                'SJC': peso_sjc
            }
        
        # === EVOLUÇÃO DIÁRIA DO MÊS SELECIONADO (1 a 31) ===
        # Se mes e ano foram selecionados, mostra todos os dias daquele mês
        evolucao_diaria = []
        
        if mes and mes != 'TODOS' and ano and ano != 'TODOS':
            mes_int = int(mes)
            ano_int = int(ano)
            
            # Filtra pelo mês e ano (usa df original, não o filtrado por dia)
            df_mes = df[(df['Mes_Num'] == mes_int) & (df['Ano'] == ano_int)]
            
            # Aplica filtro de filial se tiver
            if filial and filial != 'TODAS':
                df_mes = df_mes[df_mes['Filial'] == filial]
            
            # Cria entrada para cada dia do mês (1 a 31)
            dias_no_mes = calendar.monthrange(ano_int, mes_int)[1]
            
            for dia_num in range(1, dias_no_mes + 1):
                df_dia = df_mes[df_mes['Dia'] == dia_num]
                
                evolucao_diaria.append({
                    'dia': dia_num,
                    'carros': int(df_dia['Geral_Carros'].sum()) if len(df_dia) > 0 else 0,
                    'peso': float(df_dia['Geral_Peso'].sum()) if len(df_dia) > 0 else 0
                })
        else:
            # Se não tem filtro de mês, mostra os últimos 31 registros com dados
            df_com_dados = df[df['Geral_Carros'] > 0].copy()
            
            # Aplica filtro de filial se tiver
            if filial and filial != 'TODAS':
                df_com_dados = df_com_dados[df_com_dados['Filial'] == filial]
            
            df_sorted = df_com_dados.sort_values('Data')
            for _, row in df_sorted.tail(31).iterrows():
                evolucao_diaria.append({
                    'dia': row['Data'].strftime('%d/%m'),
                    'carros': int(row['Geral_Carros']),
                    'peso': float(row['Geral_Peso'])
                })
        
        # === TABELA DETALHADA (Últimos 30 dias de TODAS as filiais) ===
        # Mostra últimos 30 dias com todas as colunas de embarcadores
        # Filtra apenas registros com dados (onde Geral_Carros > 0)
        df_com_dados = df[df['Geral_Carros'] > 0].sort_values('Data', ascending=False)
        df_recente = df_com_dados.head(30)
        
        tabela = []
        for _, row in df_recente.iterrows():
            tabela.append({
                'data': row['Data'].strftime('%d/%m/%Y'),
                'filial': row['Filial'],
                'carros': int(row['Geral_Carros']),
                'peso': float(row['Geral_Peso']),
                # SJC
                'mafrig_foods': int(row['Mafrig_Foods_Carros']),
                'mafrig_atacado': int(row['Mafrig_Atacado_Carros']),
                'gold_pao': int(row['Gold_Pao_Carros']),
                'mafrig_compart': int(row['Compartilhado_Carros']),
                'frz_log_compart': int(row['Compartilhado_Carros']),
                'friboi': int(row['Friboi_Carros']),
                # JAC
                'adoro': int(row['Adoro_Carros']),
                'vista_foods': int(row['Vista_Foods_Carros']),
                'mieggs': int(row['Mieggs_Carros']),
                'minerva_jac': int(row['Minerva_JAC_Carros'])
            })
        
        # === OPÇÕES PARA FILTROS ===
        dias_disponiveis = sorted(df['Dia'].unique().tolist())
        meses_disponiveis = sorted(df['Mes_Num'].unique().tolist())
        anos_disponiveis = sorted(df['Ano'].unique().tolist())
        filiais_disponiveis = df['Filial'].unique().tolist()
        
        return jsonify({
            'success': True,
            'resumo': {
                'total_carros': total_carros,
                'total_peso': total_peso,
                'media_diaria_carros': round(media_diaria_carros, 2),
                'media_diaria_peso': round(media_diaria_peso, 2),
                'dias_operacao': len(df_filtrado)
            },
            'embarcadores': embarcadores,
            'mensal': dados_mensais,
            'peso_filiais': peso_filiais,
            'evolucao_diaria': evolucao_diaria,
            'tabela': tabela,
            'filtros': {
                'dias': dias_disponiveis,
                'meses': meses_disponiveis,
                'anos': anos_disponiveis,
                'filiais': filiais_disponiveis
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

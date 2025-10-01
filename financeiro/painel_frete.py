from flask import Blueprint, render_template, request, jsonify
import sqlite3
import openpyxl
import os
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from .database import get_connection

bp = Blueprint('painel_frete', __name__, url_prefix='/frete/painel')

def get_db_connection():
    """Retorna conexão com o banco de dados usando o wrapper central."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

def extrair_dados_manifesto_real():
    """Extrai dados reais do manifesto para gráfico Frete Correto vs Despesas Gerais"""
    arquivo_manifesto = os.path.join('financeiro', 'uploads', 'Manifesto_Acumulado.xlsx')
    
    if not os.path.exists(arquivo_manifesto):
        print(f"Arquivo não encontrado: {arquivo_manifesto}")
        return None
        
    try:
        wb = openpyxl.load_workbook(arquivo_manifesto, read_only=True)
        ws = wb.active
        
        # Headers esperados
        # Col 30: Frete Correto, Col 29: Despesas Gerais, Col 3: Data
        dados_por_dia = defaultdict(lambda: {'frete_correto': 0, 'despesas_gerais': 0})
        totais_mensais = {'frete_correto': 0, 'despesas_gerais': 0}
        
        linha_inicial = 2  # Pula header
        for row in ws.iter_rows(min_row=linha_inicial, values_only=True):
            if not row or len(row) < 30:
                continue
                
            try:
                # Extrair data (Col 3) - formato datetime ou string
                data_obj = row[2] if row[2] else None
                if not data_obj:
                    continue
                    
                # Parse da data
                if hasattr(data_obj, 'day'):  # É datetime
                    dia = data_obj.day
                    mes = data_obj.month
                elif "/" in str(data_obj):  # String formato dd/mm/yyyy
                    partes = str(data_obj).split("/")
                    if len(partes) >= 2:
                        dia = int(partes[0])
                        mes = int(partes[1])
                    else:
                        continue
                elif "-" in str(data_obj):  # String formato yyyy-mm-dd
                    partes = str(data_obj).split("-")
                    if len(partes) >= 3:
                        dia = int(partes[2].split()[0])  # Remove time se houver
                        mes = int(partes[1])
                    else:
                        continue
                else:
                    continue
                
                # Extrair valores - Col 30: Frete Correto, Col 29: Despesas Gerais
                def safe_float(valor):
                    if valor is None or valor == '':
                        return 0.0
                    try:
                        return float(valor)
                    except (ValueError, TypeError):
                        return 0.0
                
                frete_correto = safe_float(row[29])  # Col 30 (index 29)
                despesas_gerais = safe_float(row[28])  # Col 29 (index 28)
                
                # Agrupar por dia
                dados_por_dia[dia]['frete_correto'] += frete_correto
                dados_por_dia[dia]['despesas_gerais'] += despesas_gerais
                
                # Totais mensais
                totais_mensais['frete_correto'] += frete_correto
                totais_mensais['despesas_gerais'] += despesas_gerais
                
            except (ValueError, IndexError, TypeError) as e:
                continue
                
        wb.close()
        
        # Organizar dados por dia (1-31)
        dados_finais = []
        for dia in range(1, 32):
            dados_finais.append({
                'dia': dia,
                'frete_correto': dados_por_dia[dia]['frete_correto'],
                'despesas_gerais': dados_por_dia[dia]['despesas_gerais']
            })
        
        return {
            'dados_diarios': dados_finais,
            'totais_mensais': totais_mensais
        }
        
    except Exception as e:
        print(f"Erro ao ler manifesto: {e}")
        return None

@bp.route('/')
def index():
    """Página principal do painel de frete - dashboard completo"""
    # Por enquanto dados simulados baseados no print
    dados_dashboard = {
        'metricas': {
            'frete_receber': 2007716.00,
            'frete_pagar': 1357920.00,
            'diferenca': 649795.00,
            'produtividade': 92.36
        },
        'filtros': {
            'mes_atual': 'ABR',
            'ano_atual': 2024,
            'perfil_selecionado': 'AGREGADO',
            'clientes_selecionados': ['ADORO', 'GOLD PAO', 'Marfrig', 'MEGGS'],
            'veiculos_selecionados': ['AMX0E01', 'ARS5C20', 'ASN5A61']
        },
        'frete_diario': gerar_dados_frete_diario(),
        'frete_mensal': gerar_dados_frete_mensal(),
        'clientes_participacao': gerar_dados_clientes()
    }
    
    return render_template('painel_frete.html', dados=dados_dashboard)

def gerar_dados_frete_diario():
    """Gera dados reais para o gráfico Frete Correto vs Despesas Gerais"""
    dados_manifesto = extrair_dados_manifesto_real()
    
    if dados_manifesto:
        # Usar dados reais do manifesto
        return {
            'dados_diarios': dados_manifesto['dados_diarios'],
            'totais_mensais': dados_manifesto['totais_mensais']
        }
    else:
        # Fallback para dados simulados se não conseguir ler o manifesto
        print("Usando dados simulados - manifesto não disponível")
        dados = []
        totais = {'frete_correto': 0, 'despesas_gerais': 0}
        
        for dia in range(1, 32):
            # Simula variação diária
            variacao = (dia * 0.02) + 0.8
            frete_correto = 65000 * variacao
            despesas_gerais = 45000 * variacao
            
            dados.append({
                'dia': dia,
                'frete_correto': frete_correto,
                'despesas_gerais': despesas_gerais
            })
            
            totais['frete_correto'] += frete_correto
            totais['despesas_gerais'] += despesas_gerais
        
        return {
            'dados_diarios': dados,
            'totais_mensais': totais
        }

def gerar_dados_frete_mensal():
    """Gera dados simulados para o gráfico mensal"""
    meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET']
    dados = []
    
    base_valores = [
        {'receber': 2224294, 'pagar': 1564138, 'produtividade': 29.7},
        {'receber': 2148782, 'pagar': 1451867, 'produtividade': 32.3},
        {'receber': 2297528, 'pagar': 1525256, 'produtividade': 33.6},
        {'receber': 2597444, 'pagar': 1701265, 'produtividade': 34.5},
        {'receber': 2571763, 'pagar': 1756192, 'produtividade': 31.7},
        {'receber': 2778534, 'pagar': 1909397, 'produtividade': 31.3},
        {'receber': 3343969, 'pagar': 2211157, 'produtividade': 33.9},
        {'receber': 2927822, 'pagar': 1888939, 'produtividade': 35.5},
        {'receber': 2007716, 'pagar': 1357920, 'produtividade': 32.4}
    ]
    
    for i, mes in enumerate(meses):
        if i < len(base_valores):
            dados.append({
                'mes': mes,
                'frete_receber': base_valores[i]['receber'],
                'frete_pagar': base_valores[i]['pagar'],
                'produtividade': base_valores[i]['produtividade']
            })
    
    return dados

def gerar_dados_clientes():
    """Gera dados de participação por cliente"""
    return [
        {'nome': 'FRZ Log', 'percentual': 31.76, 'cor': '#FF6B35'},
        {'nome': 'ADORO', 'percentual': 22.78, 'cor': '#F7931E'},
        {'nome': 'Marfrig ( BRF )', 'percentual': 19.20, 'cor': '#FFD23F'},
        {'nome': 'MINERVA', 'percentual': 14.18, 'cor': '#06D6A0'},
        {'nome': 'Friboi', 'percentual': 5.58, 'cor': '#118AB2'},
        {'nome': 'Transferência', 'percentual': 3.65, 'cor': '#073B4C'},
        {'nome': 'MEGGS', 'percentual': 2.14, 'cor': '#8B5CF6'},
        {'nome': 'GOLD PAO', 'percentual': 0.64, 'cor': '#EF4444'}
    ]

def gerar_metricas():
    """Gera métricas para os cards do dashboard"""
    import random
    
    frete_receber = random.uniform(180000, 220000)
    frete_pagar = random.uniform(150000, 180000)
    diferenca = frete_receber - frete_pagar
    produtividade = (diferenca / frete_receber) * 100
    
    return {
        'frete_receber': frete_receber,
        'frete_pagar': frete_pagar,
        'diferenca': diferenca,
        'produtividade': produtividade
    }

@bp.route('/api/dados', methods=['POST'])
def api_dados_post():
    """API endpoint para atualização dinâmica dos dados"""
    filtros = request.get_json()
    
    # Gerar dados baseados nos filtros (implementar lógica real depois)
    dados = {
        'frete_diario': gerar_dados_frete_diario(),
        'frete_mensal': gerar_dados_frete_mensal(), 
        'clientes_participacao': gerar_dados_clientes(),
        'metricas': gerar_metricas()
    }
    
    return jsonify(dados)

@bp.route('/api/dados/<tipo>')
def api_dados(tipo):
    """API para buscar dados específicos via AJAX"""
    if tipo == 'frete_diario':
        return jsonify(gerar_dados_frete_diario())
    elif tipo == 'frete_mensal':
        return jsonify(gerar_dados_frete_mensal())
    elif tipo == 'clientes':
        return jsonify(gerar_dados_clientes())
    elif tipo == 'metricas':
        return jsonify(gerar_metricas())
    else:
        return jsonify({'error': 'Tipo de dados não encontrado'}), 404
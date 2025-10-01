from flask import Blueprint, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
from .database import get_connection

bp = Blueprint('painel_frete', __name__, url_prefix='/frete/painel')

def get_db_connection():
    """Retorna conexão com o banco de dados usando o wrapper central."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

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
    """Gera dados simulados para o gráfico de frete diário"""
    dados = []
    base_receber = 2000000
    base_pagar = 1350000
    
    for dia in range(1, 32):
        # Simula variação diária
        variacao = (dia * 0.02) + 0.8
        receber = base_receber * variacao
        pagar = base_pagar * variacao
        
        dados.append({
            'dia': dia,
            'frete_receber': receber,
            'frete_pagar': pagar,
            'diferenca': receber - pagar
        })
    
    return dados

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
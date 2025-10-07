"""
Módulo de Análise de Margem Líquida e Rentabilidade
Integrado ao Sistema de Frete - FRZ LOG

Autor: Sistema FRZ
Data: Outubro 2025
"""

from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import sqlite3
import os
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json

@margem_bp.route('/api/margem/dados-gerais')
def api_dados_gerais():
    """API para dados gerais do dashboard"""
    try:
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado disponível'}), 404
        
        # Aplicar filtros se fornecidos
        tipologia = request.args.get('tipologia')
        placa = request.args.get('placa')
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        if tipologia:
            df = df[df['Tipologia'] == tipologia]
        if placa:
            df = df[df['Placa'] == placa]
        if mes:
            df = df[df['mes'] == mes]
        if ano:
            df = df[df['ano'] == ano]
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado encontrado com os filtros aplicados'}), 404int para as rotas de margem
margem_bp = Blueprint('margem_analise', __name__)

class MargemAnaliseService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'financeiro.db')
        self._cache = {}  # Cache para dados processados
        self._last_modified = None  # Timestamp do último arquivo carregado
        self._df_cache = None  # Cache do DataFrame principal
        
    def get_connection(self):
        """Conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def carregar_dados_manifesto(self):
        """Carrega dados do manifesto acumulado do arquivo Excel com cache"""
        try:
            # Caminho para o arquivo Excel
            manifesto_path = os.path.join(os.path.dirname(__file__), 'uploads', 'Manifesto_Acumulado.xlsx')
            
            if not os.path.exists(manifesto_path):
                print(f"Arquivo não encontrado: {manifesto_path}")
                return pd.DataFrame()
            
            # Verificar se o arquivo foi modificado
            current_modified = os.path.getmtime(manifesto_path)
            
            # Se já temos cache e o arquivo não foi modificado, retornar cache
            if (self._df_cache is not None and 
                self._last_modified is not None and 
                current_modified == self._last_modified):
                print("📊 Usando dados do cache (performance otimizada)")
                return self._df_cache
            
            print(f"📁 Carregando arquivo Excel... ({os.path.getsize(manifesto_path) / 1024 / 1024:.1f} MB)")
            
            # Carregar apenas as colunas necessárias para melhor performance
            colunas_necessarias = [
                'Data', 'Tipologia', 'Veículo', 'Destino', 'Cliente_Real',
                'Frete Correto', 'Despesas Gerais'
            ]
            
            df = pd.read_excel(manifesto_path, usecols=colunas_necessarias)
            
            # Verificar e mapear colunas (nomes reais do arquivo)
            colunas_mapeamento = {
                'Frete Correto': 'frete_receber',    # Receita de frete
                'Despesas Gerais': 'frete_pagar',    # Despesa/custo de frete
                'Destino': 'DESTINO',
                'Tipologia': 'Tipologia',
                'Veículo': 'Placa',                  # Usar Veículo como Placa
                'Cliente_Real': 'Cliente_Real',
                'Data': 'Data'
            }
            
            # Verificar quais colunas existem e renomear
            for col_original, col_nova in colunas_mapeamento.items():
                if col_original in df.columns and col_original != col_nova:
                    df[col_nova] = df[col_original]
            
            # Conversões e limpeza
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df['frete_receber'] = pd.to_numeric(df['frete_receber'], errors='coerce').fillna(0)
            df['frete_pagar'] = pd.to_numeric(df['frete_pagar'], errors='coerce').fillna(0)
            
            # Cálculos derivados
            df['margem_liquida'] = df['frete_receber'] - df['frete_pagar']
            df['margem_percentual'] = np.where(df['frete_receber'] > 0, 
                                             (df['margem_liquida'] / df['frete_receber']) * 100, 0)
            df['mes'] = df['Data'].dt.month
            df['ano'] = df['Data'].dt.year
            df['mes_ano'] = df['Data'].dt.strftime('%Y-%m')
            
            # Limpeza rigorosa de dados
            df = df.dropna(subset=['Data'])
            df = df[df['frete_receber'] > 10]  # Remove registros com receita muito baixa (< R$ 10)
            
            # Filtrar margens extremas (evitar distorções)
            df = df[df['margem_percentual'] >= -200]  # Remover margens abaixo de -200%
            df = df[df['margem_percentual'] <= 300]   # Remover margens acima de 300%
            
            # Salvar no cache
            self._df_cache = df
            self._last_modified = current_modified
            print(f"✅ Dados carregados e cacheados: {len(df)} registros")
            
            return df
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def calcular_metas_sugeridas(self, df):
        """Calcula metas baseadas no histórico de performance"""
        if df.empty:
            return {}
            
        try:
            # Agrupar por tipologia e calcular estatísticas
            tipologia_stats = df.groupby('Tipologia').agg({
                'margem_percentual': ['mean', 'median', 'std', 'count'],
                'margem_liquida': ['sum', 'mean']
            }).round(2)
            
            metas = {}
            for tipologia in df['Tipologia'].unique():
                if pd.isna(tipologia):
                    continue
                    
                dados_tip = df[df['Tipologia'] == tipologia]
                margem_media = dados_tip['margem_percentual'].mean()
                margem_mediana = dados_tip['margem_percentual'].median()
                
                # Meta baseada na mediana (mais conservadora)
                if margem_mediana > 0:
                    meta_sugerida = max(5, margem_mediana * 0.8)  # 80% da mediana, mínimo 5%
                else:
                    meta_sugerida = 8  # Meta padrão para tipologias com problemas
                
                metas[tipologia] = {
                    'meta_sugerida': round(meta_sugerida, 1),
                    'performance_atual': round(margem_media, 1),
                    'mediana_historica': round(margem_mediana, 1),
                    'total_operacoes': len(dados_tip)
                }
            
            return metas
            
        except Exception as e:
            print(f"Erro ao calcular metas: {e}")
            return {}
    
    def analise_por_tipologia(self, df, periodo_meses=12):
        """Análise detalhada por tipologia de veículo com cache"""
        if df.empty:
            return {}
        
        # Verificar cache
        cache_key = f"tipologia_{periodo_meses}_{len(df)}"
        if cache_key in self._cache:
            print("⚡ Usando análise de tipologia do cache")
            return self._cache[cache_key]
        
        try:
            print("🔄 Calculando análise por tipologia...")
            # Filtrar últimos N meses
            data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
            df_periodo = df[df['Data'] >= data_limite].copy()
            
            # Análise geral por tipologia
            analise = df_periodo.groupby('Tipologia').agg({
                'frete_receber': ['sum', 'count', 'mean'],
                'frete_pagar': 'sum',
                'margem_liquida': ['sum', 'mean'],
                'margem_percentual': ['mean', 'std', 'min', 'max']
            }).round(2)
            
            # Análise temporal (mês a mês)
            analise_temporal = df_periodo.groupby(['mes_ano', 'Tipologia']).agg({
                'margem_liquida': 'sum',
                'margem_percentual': 'mean',
                'frete_receber': 'sum'
            }).round(2).reset_index()
            
            # Preparar dados para gráficos
            resultado = {
                'resumo_geral': {},
                'evolucao_mensal': {},
                'ranking_performance': []
            }
            
            # Processar resumo geral
            for tipologia in analise.index:
                if pd.isna(tipologia):
                    continue
                    
                resultado['resumo_geral'][tipologia] = {
                    'receita_total': float(analise.loc[tipologia, ('frete_receber', 'sum')]),
                    'despesa_total': float(analise.loc[tipologia, ('frete_pagar', 'sum')]),
                    'margem_total': float(analise.loc[tipologia, ('margem_liquida', 'sum')]),
                    'margem_percentual_media': float(analise.loc[tipologia, ('margem_percentual', 'mean')]),
                    'total_operacoes': int(analise.loc[tipologia, ('frete_receber', 'count')]),
                    'ticket_medio': float(analise.loc[tipologia, ('frete_receber', 'mean')])
                }
            
            # Processar evolução mensal
            for tipologia in df_periodo['Tipologia'].unique():
                if pd.isna(tipologia):
                    continue
                    
                dados_tip = analise_temporal[analise_temporal['Tipologia'] == tipologia]
                resultado['evolucao_mensal'][tipologia] = {
                    'meses': dados_tip['mes_ano'].tolist(),
                    'margem_liquida': dados_tip['margem_liquida'].tolist(),
                    'margem_percentual': dados_tip['margem_percentual'].tolist(),
                    'receita': dados_tip['frete_receber'].tolist()
                }
            
            # Salvar no cache
            self._cache[cache_key] = resultado
            return resultado
            
        except Exception as e:
            print(f"Erro na análise por tipologia: {e}")
            return {}
    
    def analise_por_destino(self, df, top_n=20):
        """Análise por destino/cidade com cache"""
        if df.empty:
            return {}
        
        # Verificar cache
        cache_key = f"destino_{top_n}_{len(df)}"
        if cache_key in self._cache:
            print("⚡ Usando análise de destino do cache")
            return self._cache[cache_key]
        
        try:
            print("🔄 Calculando análise por destino...")
            # Análise por destino
            destino_analise = df.groupby('DESTINO').agg({
                'frete_receber': ['sum', 'count', 'mean'],
                'frete_pagar': 'sum',
                'margem_liquida': ['sum', 'mean'],
                'margem_percentual': ['mean', 'std']
            }).round(2)
            
            # Filtrar os top N destinos por receita
            destino_analise['receita_total'] = destino_analise[('frete_receber', 'sum')]
            top_destinos = destino_analise.nlargest(top_n, 'receita_total')
            
            resultado = {
                'top_destinos': {},
                'resumo_destinos': {
                    'total_destinos': len(destino_analise),
                    'destinos_lucrativos': len(destino_analise[destino_analise[('margem_percentual', 'mean')] > 0]),
                    'destinos_prejuizo': len(destino_analise[destino_analise[('margem_percentual', 'mean')] < 0])
                }
            }
            
            # Processar top destinos
            for destino in top_destinos.index:
                if pd.isna(destino):
                    continue
                    
                resultado['top_destinos'][destino] = {
                    'receita_total': float(top_destinos.loc[destino, ('frete_receber', 'sum')]),
                    'despesa_total': float(top_destinos.loc[destino, ('frete_pagar', 'sum')]),
                    'margem_total': float(top_destinos.loc[destino, ('margem_liquida', 'sum')]),
                    'margem_percentual': float(top_destinos.loc[destino, ('margem_percentual', 'mean')]),
                    'total_entregas': int(top_destinos.loc[destino, ('frete_receber', 'count')]),
                    'ticket_medio': float(top_destinos.loc[destino, ('frete_receber', 'mean')])
                }
            
            # Salvar no cache
            self._cache[cache_key] = resultado
            return resultado
            
        except Exception as e:
            print(f"Erro na análise por destino: {e}")
            return {}
    
    def analise_por_placa(self, df, top_n=15):
        """Análise por placa de veículo com cache"""
        if df.empty:
            return {}
        
        # Verificar cache
        cache_key = f"placa_{top_n}_{len(df)}"
        if cache_key in self._cache:
            print("⚡ Usando análise de placa do cache")
            return self._cache[cache_key]
        
        try:
            print("🔄 Calculando análise por placa...")
            # Análise por placa
            placa_analise = df.groupby(['Placa', 'Tipologia']).agg({
                'frete_receber': ['sum', 'count', 'mean'],
                'frete_pagar': 'sum',
                'margem_liquida': ['sum', 'mean'],
                'margem_percentual': ['mean', 'std']
            }).round(2)
            
            # Filtrar os top N por receita
            placa_analise['receita_total'] = placa_analise[('frete_receber', 'sum')]
            top_placas = placa_analise.nlargest(top_n, 'receita_total')
            
            resultado = {
                'top_placas': {},
                'resumo_placas': {
                    'total_placas': len(placa_analise),
                    'placas_lucrativas': len(placa_analise[placa_analise[('margem_percentual', 'mean')] > 0]),
                    'placas_prejuizo': len(placa_analise[placa_analise[('margem_percentual', 'mean')] < 0])
                }
            }
            
            # Processar top placas
            for (placa, tipologia) in top_placas.index:
                if pd.isna(placa):
                    continue
                    
                chave = f"{placa} ({tipologia})"
                resultado['top_placas'][chave] = {
                    'placa': placa,
                    'tipologia': tipologia,
                    'receita_total': float(top_placas.loc[(placa, tipologia), ('frete_receber', 'sum')]),
                    'despesa_total': float(top_placas.loc[(placa, tipologia), ('frete_pagar', 'sum')]),
                    'margem_total': float(top_placas.loc[(placa, tipologia), ('margem_liquida', 'sum')]),
                    'margem_percentual': float(top_placas.loc[(placa, tipologia), ('margem_percentual', 'mean')]),
                    'total_viagens': int(top_placas.loc[(placa, tipologia), ('frete_receber', 'count')]),
                    'ticket_medio': float(top_placas.loc[(placa, tipologia), ('frete_receber', 'mean')])
                }
            
            # Salvar no cache
            self._cache[cache_key] = resultado
            return resultado
            
        except Exception as e:
            print(f"Erro na análise por placa: {e}")
            return {}
    
    def obter_filtros_disponiveis(self, df):
        """Obtém todos os filtros disponíveis nos dados"""
        if df.empty:
            return {}
        
        try:
            filtros = {
                'tipologias': sorted([str(x) for x in df['Tipologia'].unique() if pd.notna(x)]),
                'destinos': sorted([str(x) for x in df['DESTINO'].unique() if pd.notna(x)]),
                'placas': sorted([str(x) for x in df['Placa'].unique() if pd.notna(x)]),
                'anos': sorted([int(x) for x in df['ano'].unique() if pd.notna(x)]),
                'meses': list(range(1, 13)),
                'clientes': sorted([str(x) for x in df['Cliente_Real'].unique() if pd.notna(x)])
            }
            return filtros
        except Exception as e:
            print(f"Erro ao obter filtros: {e}")
            return {}
    
    def limpar_cache(self):
        """Limpa o cache quando necessário"""
        self._cache.clear()
        self._df_cache = None
        self._last_modified = None
        print("🗑️ Cache limpo")

# Instância global do serviço
margem_service = MargemAnaliseService()

# ========== ROTAS DO BLUEPRINT ==========

@margem_bp.route('/frete/margem')
def dashboard_margem():
    """Página principal do dashboard de margem"""
    return render_template('frete/margem_dashboard.html')

@margem_bp.route('/api/margem/dados-gerais')
def api_dados_gerais():
    """API para dados gerais do dashboard"""
    try:
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado encontrado'}), 404
        
        # Cálculos gerais
        receita_total = float(df['frete_receber'].sum())
        despesa_total = float(df['frete_pagar'].sum()) 
        margem_total = float(df['margem_liquida'].sum())
        
        # Calcular margem percentual correta
        margem_percentual_geral = (margem_total / receita_total * 100) if receita_total > 0 else 0
        
        dados_gerais = {
            'periodo_analise': {
                'data_inicio': df['Data'].min().strftime('%d/%m/%Y'),
                'data_fim': df['Data'].max().strftime('%d/%m/%Y'),
                'total_registros': len(df)
            },
            'resumo_financeiro': {
                'receita_total': receita_total,
                'despesa_total': despesa_total,
                'margem_total': margem_total,
                'margem_percentual_geral': margem_percentual_geral
            },
            'kpis': {
                'total_operacoes': len(df),
                'ticket_medio': float(df['frete_receber'].mean()) if not df.empty else 0,
                'operacoes_lucro': len(df[df['margem_liquida'] > 0]),
                'operacoes_prejuizo': len(df[df['margem_liquida'] < 0]),
                'melhor_tipologia': df.groupby('Tipologia')['margem_percentual'].mean().idxmax() if not df.empty else '-',
                'pior_tipologia': df.groupby('Tipologia')['margem_percentual'].mean().idxmin() if not df.empty else '-'
            },
            'alertas': {
                'operacoes_prejuizo': int(len(df[df['margem_liquida'] < 0])),
                'operacoes_margem_baixa': int(len(df[(df['margem_percentual'] > 0) & (df['margem_percentual'] < 10)])),
                'operacoes_excelentes': int(len(df[df['margem_percentual'] > 20]))
            }
        }
        
        return jsonify(dados_gerais)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/tipologia')
def api_analise_tipologia():
    """API para análise por tipologia"""
    try:
        df = margem_service.carregar_dados_manifesto()
        analise = margem_service.analise_por_tipologia(df)
        metas = margem_service.calcular_metas_sugeridas(df)
        
        resultado = {
            'analise': analise,
            'metas_sugeridas': metas
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/destinos')
def api_analise_destinos():
    """API para análise por destinos"""
    try:
        df = margem_service.carregar_dados_manifesto()
        analise = margem_service.analise_por_destino(df)
        
        return jsonify(analise)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/placas')
def api_analise_placas():
    """API para análise por placas"""
    try:
        df = margem_service.carregar_dados_manifesto()
        analise = margem_service.analise_por_placa(df)
        
        return jsonify(analise)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/filtros')
def api_filtros():
    """API para obter filtros disponíveis"""
    try:
        df = margem_service.carregar_dados_manifesto()
        filtros = margem_service.obter_filtros_disponiveis(df)
        
        return jsonify(filtros)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/limpar-cache', methods=['POST'])
def api_limpar_cache():
    """API para limpar cache"""
    try:
        margem_service.limpar_cache()
        return jsonify({'status': 'success', 'message': 'Cache limpo com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/evolucao-anual')
def api_evolucao_anual():
    """API para evolução anual mês a mês (independente dos filtros)"""
    try:
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado disponível'}), 404
        
        # Agrupar por mês/ano
        df_mensal = df.groupby(['ano', 'mes']).agg({
            'frete_receber': 'sum',
            'frete_pagar': 'sum',
            'margem_liquida': 'sum',
            'margem_percentual': 'mean'
        }).round(2)
        
        # Preparar dados para o gráfico
        meses = []
        margens_percentuais = []
        receitas = []
        
        for (ano, mes), dados in df_mensal.iterrows():
            meses.append(f'{mes:02d}/{ano}')
            margens_percentuais.append(float(dados['margem_percentual']))
            receitas.append(float(dados['frete_receber']))
        
        resultado = {
            'meses': meses,
            'margens_percentuais': margens_percentuais,
            'receitas': receitas,
            'total_meses': len(meses)
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Erro na evolução anual: {e}")
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/filtrados')
def api_dados_filtrados():
    """API para dados filtrados"""
    try:
        # Parâmetros de filtro
        tipologia = request.args.get('tipologia')
        destino = request.args.get('destino')
        placa = request.args.get('placa')
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        df = margem_service.carregar_dados_manifesto()
        
        # Aplicar filtros
        if tipologia and tipologia != 'all':
            df = df[df['Tipologia'] == tipologia]
        if destino and destino != 'all':
            df = df[df['DESTINO'] == destino]
        if placa and placa != 'all':
            df = df[df['Placa'] == placa]
        if mes:
            df = df[df['mes'] == mes]
        if ano:
            df = df[df['ano'] == ano]
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado encontrado com os filtros aplicados'}), 404
        
        # Calcular resumo dos dados filtrados
        resumo = {
            'total_registros': len(df),
            'receita_total': float(df['frete_receber'].sum()),
            'despesa_total': float(df['frete_pagar'].sum()),
            'margem_total': float(df['margem_liquida'].sum()),
            'margem_percentual': float(df['margem_percentual'].mean()),
            'periodo': {
                'inicio': df['Data'].min().strftime('%d/%m/%Y'),
                'fim': df['Data'].max().strftime('%d/%m/%Y')
            }
        }
        
        return jsonify(resumo)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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

# Blueprint para as rotas de margem
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
                'Frete Correto', 'Despesas Gerais', 'Status_Veiculo'
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
                'Status_Veiculo': 'perfil',          # FIXO/SPOT
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
            
            # Limpeza básica de dados (manter consistência com painel_frete.py)
            df = df.dropna(subset=['Data'])
            # REMOVIDO: Filtros que causavam discrepância com o painel principal
            # Manter todos os dados para consistência entre dashboards
            
            # Salvar no cache
            self._df_cache = df
            self._last_modified = current_modified
            print(f"✅ Dados carregados e cacheados: {len(df)} registros")
            
            return df
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()

# Instância do serviço
margem_service = MargemAnaliseService()

# ROTAS DA API

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
            return jsonify({'error': 'Nenhum dado disponível'}), 404
        
        # Aplicar filtros se fornecidos
        tipologia = request.args.get('tipologia')
        perfil = request.args.get('perfil')
        placa = request.args.get('placa')
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        if tipologia:
            df = df[df['Tipologia'] == tipologia]
        if perfil:
            df = df[df['perfil'] == perfil]
        if placa:
            df = df[df['Placa'] == placa]
        if mes:
            df = df[df['mes'] == mes]
        if ano:
            df = df[df['ano'] == ano]
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado encontrado com os filtros aplicados'}), 404
        
        # Calcular estatísticas
        receita_total = float(df['frete_receber'].sum())
        despesa_total = float(df['frete_pagar'].sum())
        margem_total = receita_total - despesa_total
        margem_percentual_geral = (margem_total / receita_total * 100) if receita_total > 0 else 0
        
        resultado = {
            'periodo': {
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
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/filtros')
def api_filtros():
    """API para opções de filtros"""
    try:
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado disponível'}), 404
        
        # Extrair valores únicos para filtros
        filtros = {
            'tipologias': sorted(df['Tipologia'].dropna().unique().tolist()),
            'destinos': sorted(df['DESTINO'].dropna().unique().tolist()),
            'placas': sorted(df['Placa'].dropna().unique().tolist()),
            'perfis': sorted(df['perfil'].dropna().unique().tolist()),
            'anos': sorted(df['ano'].dropna().unique().tolist()),
            'meses': list(range(1, 13))
        }
        
        return jsonify(filtros)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@margem_bp.route('/api/margem/evolucao-anual')
def api_evolucao_anual():
    """API para evolução anual mês a mês"""
    try:
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado disponível'}), 404
        
        # Aplicar filtros se fornecidos (exceto mês)
        tipologia = request.args.get('tipologia')
        perfil = request.args.get('perfil')
        placa = request.args.get('placa')
        ano = request.args.get('ano', type=int)
        
        if tipologia:
            df = df[df['Tipologia'] == tipologia]
        if perfil:
            df = df[df['perfil'] == perfil]
        if placa:
            df = df[df['Placa'] == placa]
        if ano:
            df = df[df['ano'] == ano]
        
        if df.empty:
            return jsonify({'error': 'Nenhum dado encontrado com os filtros aplicados'}), 404
        
        # Agrupar por mês/ano
        df_mensal = df.groupby(['ano', 'mes']).agg({
            'frete_receber': 'sum',
            'frete_pagar': 'sum'
        }).round(2)
        
        # Calcular margem percentual correta (total mensal)
        df_mensal['margem_liquida'] = df_mensal['frete_receber'] - df_mensal['frete_pagar']
        df_mensal['margem_percentual'] = np.where(
            df_mensal['frete_receber'] > 0,
            (df_mensal['margem_liquida'] / df_mensal['frete_receber']) * 100,
            0
        )
        
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

@margem_bp.route('/api/margem/ranking-melhores')
def api_ranking_melhores():
    """API para Top 5 melhores rentabilidades - Adaptável por tipo de análise"""
    try:
        tipo_analise = request.args.get('tipo', 'tipologia')
        mes = request.args.get('mes', '')
        ano = request.args.get('ano', '')
        tipologia_filter = request.args.get('tipologia_filter', '')  # Filtro específico
        perfil_filter = request.args.get('perfil_filter', '')  # Filtro específico de perfil
        
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify([])
        
        # Aplicar filtros se fornecidos
        if mes and mes != 'todos':
            df = df[df['mes'] == int(mes)]
        
        if ano and ano != 'todos':
            df = df[df['ano'] == int(ano)]
        
        # Aplicar filtro específico de tipologia para o Top 5
        if tipologia_filter and tipologia_filter.strip():
            df = df[df['Tipologia'] == tipologia_filter]
        
        # Aplicar filtro específico de perfil (FIXO/SPOT) para o Top 5
        if perfil_filter and perfil_filter.strip():
            df = df[df['perfil'] == perfil_filter]
        
        if df.empty:
            return jsonify([])
        
        # Definir agrupamento e lógica baseado no tipo de análise
        if tipo_analise == 'destino':
            # Para destinos: agrupar por destino apenas
            resultado = df.groupby('DESTINO').agg({
                'frete_receber': 'sum',
                'frete_pagar': 'sum'
            }).reset_index()
            
            resultado['Margem'] = resultado['frete_receber'] - resultado['frete_pagar']
            resultado['Percentual'] = (resultado['Margem'] / resultado['frete_receber'] * 100).round(2)
            
            # Filtrar apenas valores válidos
            resultado = resultado[resultado['frete_receber'] > 0]
            
            if resultado.empty:
                return jsonify([])
            
            # Ordenar por percentual (melhor primeiro)
            resultado = resultado.sort_values('Percentual', ascending=False)
            
            # Top 5 melhores destinos
            top_5 = resultado.head(5)
            
            # Formatar dados
            ranking = []
            for _, row in top_5.iterrows():
                ranking.append({
                    'nome': f"{row['DESTINO']}",
                    'margem': f"R$ {row['Margem']:,.2f}",
                    'percentual': f"{row['Percentual']:.1f}%",
                    'receita': f"R$ {row['frete_receber']:,.2f}",
                    'tipologia': 'Destino',
                    'placa': '-'
                })
                
        elif tipo_analise == 'placa':
            # Para placas: agrupar por placa
            resultado = df.groupby(['Placa', 'Tipologia']).agg({
                'frete_receber': 'sum',
                'frete_pagar': 'sum'
            }).reset_index()
            
            resultado['Margem'] = resultado['frete_receber'] - resultado['frete_pagar']
            resultado['Percentual'] = (resultado['Margem'] / resultado['frete_receber'] * 100).round(2)
            
            # Filtrar apenas valores válidos
            resultado = resultado[resultado['frete_receber'] > 0]
            
            if resultado.empty:
                return jsonify([])
            
            # Ordenar por percentual (melhor primeiro)
            resultado = resultado.sort_values('Percentual', ascending=False)
            
            # Top 5 melhores placas
            top_5 = resultado.head(5)
            
            # Formatar dados
            ranking = []
            for _, row in top_5.iterrows():
                ranking.append({
                    'nome': f"{row['Tipologia']} - Placa {row['Placa']}",
                    'margem': f"R$ {row['Margem']:,.2f}",
                    'percentual': f"{row['Percentual']:.1f}%",
                    'receita': f"R$ {row['frete_receber']:,.2f}",
                    'tipologia': row['Tipologia'],
                    'placa': row['Placa']
                })
                
        else:
            # Para tipologia: uma placa por tipologia (lógica original)
            resultado_placas = df.groupby(['Placa', 'Tipologia']).agg({
                'frete_receber': 'sum',
                'frete_pagar': 'sum'
            }).reset_index()
            
            resultado_placas['Margem'] = resultado_placas['frete_receber'] - resultado_placas['frete_pagar']
            resultado_placas['Percentual'] = (resultado_placas['Margem'] / resultado_placas['frete_receber'] * 100).round(2)
            
            # Filtrar apenas valores válidos
            resultado_placas = resultado_placas[resultado_placas['frete_receber'] > 0]
            
            if resultado_placas.empty:
                return jsonify([])
            
            # Ordenar por percentual (melhor primeiro)
            resultado_placas = resultado_placas.sort_values('Percentual', ascending=False)
            
            # Estratégia: 1 placa por tipologia primeiro, depois completar com as melhores restantes
            ranking = []
            tipologias_usadas = set()
            
            # Primeira passada: uma placa por tipologia
            for _, row in resultado_placas.iterrows():
                if len(ranking) >= 5:
                    break
                    
                tipologia = row['Tipologia']
                if tipologia not in tipologias_usadas:
                    tipologias_usadas.add(tipologia)
                    
                    ranking.append({
                        'nome': f"{tipologia} - Placa {row['Placa']}",
                        'margem': f"R$ {row['Margem']:,.2f}",
                        'percentual': f"{row['Percentual']:.1f}%",
                        'receita': f"R$ {row['frete_receber']:,.2f}",
                        'tipologia': tipologia,
                        'placa': row['Placa']
                    })
            
            # Segunda passada: se ainda não temos 5, pegar as próximas melhores
            if len(ranking) < 5:
                placas_usadas = {item['placa'] for item in ranking}
                
                for _, row in resultado_placas.iterrows():
                    if len(ranking) >= 5:
                        break
                        
                    if row['Placa'] not in placas_usadas:
                        ranking.append({
                            'nome': f"{row['Tipologia']} - Placa {row['Placa']}",
                            'margem': f"R$ {row['Margem']:,.2f}",
                            'percentual': f"{row['Percentual']:.1f}%",
                            'receita': f"R$ {row['frete_receber']:,.2f}",
                            'tipologia': row['Tipologia'],
                            'placa': row['Placa']
                        })
        
        # Garantir exatamente 5 posições
        while len(ranking) < 5:
            ranking.append({
                'nome': f"-- Posição {len(ranking) + 1} --",
                'margem': 'R$ 0,00',
                'percentual': '0.0%',
                'receita': 'R$ 0,00',
                'tipologia': '-',
                'placa': '-'
            })
        
        return jsonify(ranking[:5])
        
    except Exception as e:
        print(f"Erro no ranking melhores: {e}")
        return jsonify([])

@margem_bp.route('/api/margem/ranking-piores')
def api_ranking_piores():
    """API para Top 5 piores rentabilidades - Adaptável por tipo de análise"""
    try:
        tipo_analise = request.args.get('tipo', 'tipologia')
        mes = request.args.get('mes', '')
        ano = request.args.get('ano', '')
        tipologia_filter = request.args.get('tipologia_filter', '')  # Filtro específico
        perfil_filter = request.args.get('perfil_filter', '')  # Filtro específico de perfil
        
        df = margem_service.carregar_dados_manifesto()
        
        if df.empty:
            return jsonify([])
        
        # Aplicar filtros se fornecidos
        if mes and mes != 'todos':
            df = df[df['mes'] == int(mes)]
        
        if ano and ano != 'todos':
            df = df[df['ano'] == int(ano)]
        
        # Aplicar filtro específico de tipologia para o Top 5
        if tipologia_filter and tipologia_filter.strip():
            df = df[df['Tipologia'] == tipologia_filter]
        
        # Aplicar filtro específico de perfil (FIXO/SPOT) para o Top 5
        if perfil_filter and perfil_filter.strip():
            df = df[df['perfil'] == perfil_filter]
        
        if df.empty:
            return jsonify([])
        
        # Definir agrupamento e lógica baseado no tipo de análise
        if tipo_analise == 'destino':
            # Para destinos: agrupar por destino apenas
            resultado = df.groupby('DESTINO').agg({
                'frete_receber': 'sum',
                'frete_pagar': 'sum'
            }).reset_index()
            
            resultado['Margem'] = resultado['frete_receber'] - resultado['frete_pagar']
            resultado['Percentual'] = (resultado['Margem'] / resultado['frete_receber'] * 100).round(2)
            
            # Filtrar apenas valores válidos
            resultado = resultado[resultado['frete_receber'] > 0]
            
            if resultado.empty:
                return jsonify([])
            
            # Ordenar por percentual (pior primeiro)
            resultado = resultado.sort_values('Percentual', ascending=True)
            
            # Top 5 piores destinos
            top_5 = resultado.head(5)
            
            # Formatar dados
            ranking = []
            for _, row in top_5.iterrows():
                ranking.append({
                    'nome': f"{row['DESTINO']}",
                    'margem': f"R$ {row['Margem']:,.2f}",
                    'percentual': f"{row['Percentual']:.1f}%",
                    'receita': f"R$ {row['frete_receber']:,.2f}",
                    'tipologia': 'Destino',
                    'placa': '-'
                })
                
        elif tipo_analise == 'placa':
            # Para placas: agrupar por placa
            resultado = df.groupby(['Placa', 'Tipologia']).agg({
                'frete_receber': 'sum',
                'frete_pagar': 'sum'
            }).reset_index()
            
            resultado['Margem'] = resultado['frete_receber'] - resultado['frete_pagar']
            resultado['Percentual'] = (resultado['Margem'] / resultado['frete_receber'] * 100).round(2)
            
            # Filtrar apenas valores válidos
            resultado = resultado[resultado['frete_receber'] > 0]
            
            if resultado.empty:
                return jsonify([])
            
            # Ordenar por percentual (pior primeiro)
            resultado = resultado.sort_values('Percentual', ascending=True)
            
            # Top 5 piores placas
            top_5 = resultado.head(5)
            
            # Formatar dados
            ranking = []
            for _, row in top_5.iterrows():
                ranking.append({
                    'nome': f"{row['Tipologia']} - Placa {row['Placa']}",
                    'margem': f"R$ {row['Margem']:,.2f}",
                    'percentual': f"{row['Percentual']:.1f}%",
                    'receita': f"R$ {row['frete_receber']:,.2f}",
                    'tipologia': row['Tipologia'],
                    'placa': row['Placa']
                })
                
        else:
            # Para tipologia: uma placa por tipologia (lógica original)
            resultado_placas = df.groupby(['Placa', 'Tipologia']).agg({
                'frete_receber': 'sum',
                'frete_pagar': 'sum'
            }).reset_index()
            
            resultado_placas['Margem'] = resultado_placas['frete_receber'] - resultado_placas['frete_pagar']
            resultado_placas['Percentual'] = (resultado_placas['Margem'] / resultado_placas['frete_receber'] * 100).round(2)
            
            # Filtrar apenas valores válidos
            resultado_placas = resultado_placas[resultado_placas['frete_receber'] > 0]
            
            if resultado_placas.empty:
                return jsonify([])
            
            # Ordenar por percentual (pior primeiro)
            resultado_placas = resultado_placas.sort_values('Percentual', ascending=True)
            
            # Estratégia: 1 placa por tipologia primeiro, depois completar com as piores restantes
            ranking = []
            tipologias_usadas = set()
            
            # Primeira passada: uma placa por tipologia (a pior de cada tipo)
            for _, row in resultado_placas.iterrows():
                if len(ranking) >= 5:
                    break
                    
                tipologia = row['Tipologia']
                if tipologia not in tipologias_usadas:
                    tipologias_usadas.add(tipologia)
                    
                    ranking.append({
                        'nome': f"{tipologia} - Placa {row['Placa']}",
                        'margem': f"R$ {row['Margem']:,.2f}",
                        'percentual': f"{row['Percentual']:.1f}%",
                        'receita': f"R$ {row['frete_receber']:,.2f}",
                        'tipologia': tipologia,
                        'placa': row['Placa']
                    })
            
            # Segunda passada: se ainda não temos 5, pegar as próximas piores
            if len(ranking) < 5:
                placas_usadas = {item['placa'] for item in ranking}
                
                for _, row in resultado_placas.iterrows():
                    if len(ranking) >= 5:
                        break
                        
                    if row['Placa'] not in placas_usadas:
                        ranking.append({
                            'nome': f"{row['Tipologia']} - Placa {row['Placa']}",
                            'margem': f"R$ {row['Margem']:,.2f}",
                            'percentual': f"{row['Percentual']:.1f}%",
                            'receita': f"R$ {row['frete_receber']:,.2f}",
                            'tipologia': row['Tipologia'],
                            'placa': row['Placa']
                        })
        
        # Garantir exatamente 5 posições
        while len(ranking) < 5:
            ranking.append({
                'nome': f"-- Posição {len(ranking) + 1} --",
                'margem': 'R$ 0,00',
                'percentual': '0.0%',
                'receita': 'R$ 0,00',
                'tipologia': '-',
                'placa': '-'
            })
        
        return jsonify(ranking[:5])
        
    except Exception as e:
        print(f"Erro no ranking piores: {e}")
        return jsonify([])

@margem_bp.route('/api/margem/limpar-cache', methods=['POST'])
def api_limpar_cache():
    """Limpar cache do serviço"""
    try:
        margem_service._cache = {}
        margem_service._df_cache = None
        margem_service._last_modified = None
        return jsonify({'status': 'success', 'message': 'Cache limpo com sucesso'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
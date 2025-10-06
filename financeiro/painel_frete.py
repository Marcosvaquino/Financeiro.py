from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import os
import numpy as np
from datetime import datetime

def convert_to_json_serializable(obj):
    """Converte tipos numpy/pandas para tipos Python nativos"""
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

painel_frete_bp = Blueprint('painel_frete', __name__)

# Caminho para o arquivo de manifesto acumulado
MANIFESTO_PATH = os.path.join(os.path.dirname(__file__), 'uploads', 'Manifesto_Acumulado.xlsx')

class PainelFreteService:
    def __init__(self):
        self.df_manifesto = None
        self.ultima_modificacao = None
        self.carregar_dados()
    
    def verificar_atualizacao_arquivo(self):
        """Verifica se o arquivo foi modificado desde a última leitura"""
        try:
            if os.path.exists(MANIFESTO_PATH):
                modificacao_atual = os.path.getmtime(MANIFESTO_PATH)
                if self.ultima_modificacao is None or modificacao_atual > self.ultima_modificacao:
                    self.ultima_modificacao = modificacao_atual
                    return True
            return False
        except Exception as e:
            print(f"Erro ao verificar modificação do arquivo: {e}")
            return False
    
    def carregar_dados(self, forcar_recarga=False):
        """Carrega dados do Excel, recarregando se necessário"""
        try:
            # Verificar se precisa recarregar
            if not forcar_recarga and not self.verificar_atualizacao_arquivo():
                return self.df_manifesto  # Dados já estão atualizados, retornar DataFrame existente
                
            if os.path.exists(MANIFESTO_PATH):
                print("🔄 Recarregando dados do manifesto...")
                self.df_manifesto = pd.read_excel(MANIFESTO_PATH)
                self.df_manifesto['Data'] = pd.to_datetime(self.df_manifesto['Data'], errors='coerce')
                self.df_manifesto['Mes'] = self.df_manifesto['Data'].dt.month
                self.df_manifesto['Ano'] = self.df_manifesto['Data'].dt.year
                self.df_manifesto['Dia'] = self.df_manifesto['Data'].dt.day
                
                self.df_manifesto['Frete Correto'] = pd.to_numeric(self.df_manifesto['Frete Correto'], errors='coerce').fillna(0)
                self.df_manifesto['Despesas Gerais'] = pd.to_numeric(self.df_manifesto['Despesas Gerais'], errors='coerce').fillna(0)
                
                print(f"✅ Dados carregados: {len(self.df_manifesto)} registros")
            else:
                print(f"❌ Arquivo não encontrado: {MANIFESTO_PATH}")
                self.df_manifesto = pd.DataFrame()
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            self.df_manifesto = pd.DataFrame()
        
        return self.df_manifesto
    
    def obter_filtros_disponiveis(self):
        # Verificar se dados precisam ser atualizados
        self.carregar_dados()
        
        if self.df_manifesto.empty:
            return {}
        
        try:
            filtros = {
                'perfis': sorted(list(set(self.df_manifesto['Status_Veiculo'].dropna().astype(str)))),
                'clientes': sorted(list(set(self.df_manifesto['Cliente_Real'].dropna().astype(str)))),
                'veiculos': sorted(list(set(self.df_manifesto['Veículo'].dropna().astype(str)))),
                'meses': sorted(list(set(self.df_manifesto['Mes'].dropna().astype(int)))),
                'anos': sorted(list(set(self.df_manifesto['Ano'].dropna().astype(int))))
            }
            return filtros
        except Exception as e:
            print(f"Erro ao obter filtros: {e}")
            return {'perfis': [], 'clientes': [], 'veiculos': [], 'meses': [], 'anos': []}
    
    def filtrar_dados(self, perfil=None, cliente=None, veiculo=None, mes=None, ano=None):
        # Verificar se dados precisam ser atualizados
        self.carregar_dados()
        
        if self.df_manifesto.empty:
            return pd.DataFrame()
        
        df_filtrado = self.df_manifesto.copy()
        
        try:
            if perfil:
                df_filtrado = df_filtrado[df_filtrado['Status_Veiculo'] == perfil]
            if cliente:
                df_filtrado = df_filtrado[df_filtrado['Cliente_Real'] == cliente]
            if veiculo:
                df_filtrado = df_filtrado[df_filtrado['Veículo'] == veiculo]
            if mes:
                df_filtrado = df_filtrado[df_filtrado['Mes'] == int(mes)]
            if ano:
                df_filtrado = df_filtrado[df_filtrado['Ano'] == int(ano)]
            
            return df_filtrado
        except Exception as e:
            print(f"Erro ao filtrar dados: {e}")
            return pd.DataFrame()

    def calcular_cards_resumo(self, df_filtrado):
        if df_filtrado.empty:
            return {
                'total_faturado': 0,
                'total_despesas': 0,
                'margem_liquida_pct': 0,
                'numero_viagens': 0,
                'ticket_medio': 0,
                'cliente_mais_rentavel': 'N/A'
            }
        
        try:
            total_faturado = df_filtrado['Frete Correto'].sum()
            total_despesas = df_filtrado['Despesas Gerais'].sum()
            margem_liquida = total_faturado - total_despesas
            margem_liquida_pct = (margem_liquida / total_faturado * 100) if total_faturado > 0 else 0
            numero_viagens = len(df_filtrado)
            ticket_medio = total_faturado / numero_viagens if numero_viagens > 0 else 0
            
            # Cliente mais rentável
            if 'Cliente_Real' in df_filtrado.columns:
                cliente_rentabilidade = df_filtrado.groupby('Cliente_Real').agg({
                    'Frete Correto': 'sum',
                    'Despesas Gerais': 'sum'
                })
                cliente_rentabilidade['margem'] = cliente_rentabilidade['Frete Correto'] - cliente_rentabilidade['Despesas Gerais']
                cliente_mais_rentavel = cliente_rentabilidade['margem'].idxmax() if not cliente_rentabilidade.empty else 'N/A'
            else:
                cliente_mais_rentavel = 'N/A'
            
            return {
                'total_faturado': float(round(total_faturado, 2)),
                'total_despesas': float(round(total_despesas, 2)),
                'margem_liquida_pct': float(round(margem_liquida_pct, 2)),
                'numero_viagens': int(numero_viagens),
                'ticket_medio': float(round(ticket_medio, 2)),
                'cliente_mais_rentavel': str(cliente_mais_rentavel)
            }
        except Exception as e:
            print(f"Erro ao calcular cards: {e}")
            return {
                'total_faturado': 0,
                'total_despesas': 0,
                'margem_liquida_pct': 0,
                'numero_viagens': 0,
                'ticket_medio': 0,
                'cliente_mais_rentavel': 'N/A'
            }

    def calcular_grafico_diario_acumulativo(self, df_filtrado):
        if df_filtrado.empty:
            return {'dias': [], 'receita_acumulada': [], 'despesa_acumulada': [], 'margem_acumulada': []}
        
        try:
            # Agrupar por dia
            dados_diarios = df_filtrado.groupby('Dia').agg({
                'Frete Correto': 'sum',
                'Despesas Gerais': 'sum'
            }).reset_index()
            
            # Calcular valores acumulativos
            dados_diarios = dados_diarios.sort_values('Dia')
            dados_diarios['receita_acumulada'] = dados_diarios['Frete Correto'].cumsum()
            dados_diarios['despesa_acumulada'] = dados_diarios['Despesas Gerais'].cumsum()
            dados_diarios['margem_acumulada'] = dados_diarios['receita_acumulada'] - dados_diarios['despesa_acumulada']
            
            return {
                'dias': dados_diarios['Dia'].tolist(),
                'receita_acumulada': dados_diarios['receita_acumulada'].round(2).tolist(),
                'despesa_acumulada': dados_diarios['despesa_acumulada'].round(2).tolist(),
                'margem_acumulada': dados_diarios['margem_acumulada'].round(2).tolist()
            }
        except Exception as e:
            print(f"Erro ao calcular gráfico diário: {e}")
            return {'dias': [], 'receita_acumulada': [], 'despesa_acumulada': [], 'margem_acumulada': []}

    def calcular_grafico_mensal_rentabilidade(self, df_filtrado):
        # Sempre retornar os 12 meses do ano
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        meses_numeros = list(range(1, 13))
        
        # Inicializar arrays com zeros para todos os meses
        frete_receber = [0.0] * 12
        frete_pagar = [0.0] * 12
        rentabilidade_pct = [0.0] * 12
        
        if not df_filtrado.empty:
            try:
                # Agrupar por mês
                dados_mensais = df_filtrado.groupby('Mes').agg({
                    'Frete Correto': 'sum',
                    'Despesas Gerais': 'sum'
                }).reset_index()
                
                # Preencher os dados para os meses que existem
                for _, row in dados_mensais.iterrows():
                    mes_idx = int(row['Mes']) - 1  # Converter para índice (0-11)
                    if 0 <= mes_idx <= 11:
                        frete_receber[mes_idx] = round(float(row['Frete Correto']), 2)
                        frete_pagar[mes_idx] = round(float(row['Despesas Gerais']), 2)
                        
                        # Calcular rentabilidade apenas se houver receita
                        if row['Frete Correto'] > 0:
                            rentabilidade = ((row['Frete Correto'] - row['Despesas Gerais']) / 
                                           row['Frete Correto'] * 100)
                            rentabilidade_pct[mes_idx] = round(float(rentabilidade), 2)
                        
            except Exception as e:
                print(f"Erro ao calcular gráfico mensal: {e}")
        
        return {
            'meses': meses_nomes,
            'frete_pagar': frete_pagar,
            'frete_receber': frete_receber,
            'rentabilidade_pct': rentabilidade_pct
        }

    def calcular_grafico_clientes(self, df_filtrado):
        if df_filtrado.empty:
            return {'clientes': [], 'receita': [], 'despesa': [], 'rentabilidade_pct': []}
        
        try:
            # Agrupar por cliente
            dados_clientes = df_filtrado.groupby('Cliente_Real').agg({
                'Frete Correto': 'sum',
                'Despesas Gerais': 'sum'
            }).reset_index()
            
            dados_clientes['rentabilidade_pct'] = (
                (dados_clientes['Frete Correto'] - dados_clientes['Despesas Gerais']) / 
                dados_clientes['Frete Correto'] * 100
            ).fillna(0)
            
            # Ordenar por rentabilidade e pegar top 10
            dados_clientes = dados_clientes.sort_values('rentabilidade_pct', ascending=False).head(10)
            
            return {
                'clientes': dados_clientes['Cliente_Real'].tolist(),
                'receita': dados_clientes['Frete Correto'].round(2).tolist(),
                'despesa': dados_clientes['Despesas Gerais'].round(2).tolist(),
                'rentabilidade_pct': dados_clientes['rentabilidade_pct'].round(2).tolist()
            }
        except Exception as e:
            print(f"Erro ao calcular gráfico de clientes: {e}")
            return {'clientes': [], 'receita': [], 'despesa': [], 'rentabilidade_pct': []}

    def calcular_grafico_veiculos(self, df_filtrado):
        if df_filtrado.empty:
            return {'veiculos': [], 'receita': [], 'despesa': [], 'rentabilidade_pct': []}
        
        try:
            # Agrupar por veículo
            dados_veiculos = df_filtrado.groupby('Veículo').agg({
                'Frete Correto': 'sum',
                'Despesas Gerais': 'sum'
            }).reset_index()
            
            dados_veiculos['rentabilidade_pct'] = (
                (dados_veiculos['Frete Correto'] - dados_veiculos['Despesas Gerais']) / 
                dados_veiculos['Frete Correto'] * 100
            ).fillna(0)
            
            # Ordenar por rentabilidade e pegar top 15
            dados_veiculos = dados_veiculos.sort_values('rentabilidade_pct', ascending=False).head(15)
            
            return {
                'veiculos': dados_veiculos['Veículo'].tolist(),
                'receita': dados_veiculos['Frete Correto'].round(2).tolist(),
                'despesa': dados_veiculos['Despesas Gerais'].round(2).tolist(),
                'rentabilidade_pct': dados_veiculos['rentabilidade_pct'].round(2).tolist()
            }
        except Exception as e:
            print(f"Erro ao calcular gráfico de veículos: {e}")
            return {'veiculos': [], 'receita': [], 'despesa': [], 'rentabilidade_pct': []}

# Instância global do serviço
painel_service = PainelFreteService()

@painel_frete_bp.route('/painel-frete')
def painel_frete():
    return render_template('painel_frete.html')

@painel_frete_bp.route('/api/painel-frete/filtros')
def api_filtros():
    try:
        filtros = painel_service.obter_filtros_disponiveis()
        return jsonify(filtros)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@painel_frete_bp.route('/api/painel-frete/dados')
def api_dados():
    try:
        perfil = request.args.get('perfil')
        cliente = request.args.get('cliente')
        veiculo = request.args.get('veiculo')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        df_filtrado = painel_service.filtrar_dados(perfil, cliente, veiculo, mes, ano)
        
        # Para o gráfico mensal, usar dados SEM filtro de mês (para mostrar todos os meses)
        df_mensal_completo = painel_service.filtrar_dados(perfil, cliente, veiculo, None, ano)
        
        dados = {
            'cards': painel_service.calcular_cards_resumo(df_filtrado),
            'grafico_diario': painel_service.calcular_grafico_diario_acumulativo(df_filtrado),
            'grafico_mensal': painel_service.calcular_grafico_mensal_rentabilidade(df_mensal_completo),
            'grafico_clientes': painel_service.calcular_grafico_clientes(df_filtrado),
            'grafico_veiculos': painel_service.calcular_grafico_veiculos(df_filtrado)
        }
        
        # Converter todos os tipos numpy para tipos Python nativos
        dados = convert_to_json_serializable(dados)
        
        return jsonify(dados)
    except Exception as e:
        print(f"Erro na API dados: {e}")
        return jsonify({'error': str(e)}), 500

@painel_frete_bp.route('/api/painel-frete/detalhes-receita')
def api_detalhes_receita():
    try:
        perfil = request.args.get('perfil')
        cliente = request.args.get('cliente')
        veiculo = request.args.get('veiculo')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        df_filtrado = painel_service.filtrar_dados(perfil, cliente, veiculo, mes, ano)
        
        if df_filtrado.empty:
            return jsonify({'error': 'Nenhum dado encontrado'})
        
        # Todos os clientes (não apenas top 5)
        top_clientes = df_filtrado.groupby('Cliente_Real').agg({
            'Frete Correto': 'sum'
        }).reset_index().sort_values('Frete Correto', ascending=False)
        
        total_faturado = df_filtrado['Frete Correto'].sum()
        top_clientes['participacao_pct'] = (top_clientes['Frete Correto'] / total_faturado * 100).round(1)
        
        # Todos os veículos (não apenas top 5)
        top_veiculos = df_filtrado.groupby('Veículo').agg({
            'Frete Correto': 'sum',
            'Manifesto': 'count'  # Número de viagens
        }).reset_index().sort_values('Frete Correto', ascending=False)
        
        # Criar tabela completa combinando cliente e veículo
        tabela_completa = df_filtrado.groupby(['Cliente_Real', 'Veículo']).agg({
            'Frete Correto': 'sum',
            'Manifesto': 'count'
        }).reset_index().sort_values('Frete Correto', ascending=False)
        
        tabela_completa['participacao_pct'] = (tabela_completa['Frete Correto'] / total_faturado * 100).round(2)

        dados = {
            'total_faturado': float(round(total_faturado, 2)),
            'meta_faturado': float(round(total_faturado * 1.15, 2)),  # Meta 15% maior
            'performance_pct': min(100, round((total_faturado / (total_faturado * 1.15)) * 100, 0)),
            'top_clientes': [
                {
                    'nome': str(row['Cliente_Real']),
                    'faturamento': float(round(row['Frete Correto'], 2)),
                    'participacao': float(row['participacao_pct'])
                }
                for _, row in top_clientes.head(10).iterrows()  # Top 10 para ter dados suficientes
            ],
            'top_veiculos': [
                {
                    'placa': str(row['Veículo']),
                    'faturamento': float(round(row['Frete Correto'], 2)),
                    'viagens': int(row['Manifesto'])
                }
                for _, row in top_veiculos.head(10).iterrows()  # Top 10 para ter dados suficientes
            ],
            'tabela_completa': [
                {
                    'cliente': str(row['Cliente_Real']),
                    'veiculo': str(row['Veículo']),
                    'faturamento': float(round(row['Frete Correto'], 2)),
                    'viagens': int(row['Manifesto']),
                    'participacao': float(row['participacao_pct'])
                }
                for _, row in tabela_completa.iterrows()
            ]
        }
        
        return jsonify(dados)
    except Exception as e:
        print(f"Erro na API detalhes receita: {e}")
        return jsonify({'error': str(e)}), 500

@painel_frete_bp.route('/api/painel-frete/detalhes-despesas')
def api_detalhes_despesas():
    try:
        perfil = request.args.get('perfil')
        cliente = request.args.get('cliente')
        veiculo = request.args.get('veiculo')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        df_filtrado = painel_service.filtrar_dados(perfil, cliente, veiculo, mes, ano)
        
        if df_filtrado.empty:
            return jsonify({'error': 'Nenhum dado encontrado'})
        
        # Todas as despesas por cliente e veículo
        top_despesas = df_filtrado.groupby(['Cliente_Real', 'Veículo']).agg({
            'Despesas Gerais': 'sum'
        }).reset_index().sort_values('Despesas Gerais', ascending=False)
        
        total_despesas = df_filtrado['Despesas Gerais'].sum()
        top_despesas['participacao_pct'] = (top_despesas['Despesas Gerais'] / total_despesas * 100).round(1)
        
        # Veículo mais usado
        veiculo_mais_usado = df_filtrado.groupby('Veículo').agg({
            'Manifesto': 'count'
        }).reset_index().sort_values('Manifesto', ascending=False).iloc[0]
        
        # Top 5 para os cards
        top_5_despesas = top_despesas.head(5)
        
        dados = {
            'total_despesas': float(round(total_despesas, 2)),
            'meta_despesas': float(round(total_despesas * 0.85, 2)),  # Meta 15% menor
            'performance_pct': min(100, round(((total_despesas * 0.85) / total_despesas) * 100, 0)),
            'maior_despesa': float(round(top_despesas.iloc[0]['Despesas Gerais'], 2)) if not top_despesas.empty else 0,
            'maior_beneficiario': str(top_despesas.iloc[0]['Cliente_Real']) if not top_despesas.empty else 'N/A',
            'veiculo_mais_usado': str(veiculo_mais_usado['Veículo']),
            'viagens_veiculo': int(veiculo_mais_usado['Manifesto']),
            'ticket_medio_pago': float(round(total_despesas / len(df_filtrado), 2)) if len(df_filtrado) > 0 else 0,
            'top_pagamentos': [
                {
                    'embarcador': str(row['Cliente_Real']),
                    'placa': str(row['Veículo']),
                    'valor': float(round(row['Despesas Gerais'], 2)),
                    'participacao': float(row['participacao_pct'])
                }
                for _, row in top_5_despesas.iterrows()
            ],
            'tabela_completa': [
                {
                    'embarcador': str(row['Cliente_Real']),
                    'placa': str(row['Veículo']),
                    'valor': float(round(row['Despesas Gerais'], 2)),
                    'participacao': float(row['participacao_pct'])
                }
                for _, row in top_despesas.iterrows()
            ]
        }
        
        return jsonify(dados)
    except Exception as e:
        print(f"Erro na API detalhes despesas: {e}")
        return jsonify({'error': str(e)}), 500

@painel_frete_bp.route('/api/painel-frete/detalhes-despesas-completo')
def api_detalhes_despesas_completo():
    """Retorna todos os registros individuais para o modal de despesas"""
    try:
        perfil = request.args.get('perfil')
        cliente = request.args.get('cliente')
        veiculo = request.args.get('veiculo')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        df_filtrado = painel_service.filtrar_dados(perfil, cliente, veiculo, mes, ano)
        
        if df_filtrado.empty:
            return jsonify({'error': 'Nenhum dado encontrado'})
        
        # Converter DataFrame para lista de dicionários
        registros = []
        for _, row in df_filtrado.iterrows():
            registro = {}
            for coluna in df_filtrado.columns:
                valor = row[coluna]
                # Converter valores para tipos JSON serializáveis
                if pd.isna(valor):
                    registro[coluna] = None
                elif isinstance(valor, (int, float)):
                    registro[coluna] = float(valor) if not pd.isna(valor) else 0.0
                else:
                    registro[coluna] = str(valor)
            registros.append(registro)
        
        return jsonify({
            'registros': registros,
            'total': len(registros)
        })
        
    except Exception as e:
        print(f"Erro na API detalhes despesas completo: {e}")
        return jsonify({'error': str(e)}), 500

@painel_frete_bp.route('/api/painel-frete/reload-data', methods=['POST'])
def reload_data():
    """Força a recarga dos dados do arquivo Excel"""
    try:
        print("🔄 API de recarga chamada - forçando reload dos dados...")
        painel_service.carregar_dados(forcar_recarga=True)
        return jsonify({
            'success': True,
            'message': 'Dados recarregados com sucesso!'
        })
    except Exception as e:
        print(f"❌ Erro ao recarregar dados: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
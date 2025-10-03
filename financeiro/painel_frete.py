from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import os
from datetime import datetime

painel_frete_bp = Blueprint('painel_frete', __name__)

# Caminho para o arquivo de manifesto acumulado
MANIFESTO_PATH = os.path.join(os.path.dirname(__file__), 'uploads', 'Manifesto_Acumulado.xlsx')

class PainelFreteService:
    def __init__(self):
        self.df_manifesto = None
        self.carregar_dados()
    
    def carregar_dados(self):
        try:
            if os.path.exists(MANIFESTO_PATH):
                self.df_manifesto = pd.read_excel(MANIFESTO_PATH)
                self.df_manifesto['Data'] = pd.to_datetime(self.df_manifesto['Data'], errors='coerce')
                self.df_manifesto['Mes'] = self.df_manifesto['Data'].dt.month
                self.df_manifesto['Ano'] = self.df_manifesto['Data'].dt.year
                self.df_manifesto['Dia'] = self.df_manifesto['Data'].dt.day
                
                self.df_manifesto['Frete Correto'] = pd.to_numeric(self.df_manifesto['Frete Correto'], errors='coerce').fillna(0)
                self.df_manifesto['Despesas Gerais'] = pd.to_numeric(self.df_manifesto['Despesas Gerais'], errors='coerce').fillna(0)
                
                print(f"Dados carregados: {len(self.df_manifesto)} registros")
            else:
                print(f"Arquivo não encontrado: {MANIFESTO_PATH}")
                self.df_manifesto = pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.df_manifesto = pd.DataFrame()
    
    def obter_filtros_disponiveis(self):
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
                'total_faturado': round(total_faturado, 2),
                'total_despesas': round(total_despesas, 2),
                'margem_liquida_pct': round(margem_liquida_pct, 2),
                'numero_viagens': numero_viagens,
                'ticket_medio': round(ticket_medio, 2),
                'cliente_mais_rentavel': cliente_mais_rentavel
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
        if df_filtrado.empty:
            return {'meses': [], 'frete_pagar': [], 'frete_receber': [], 'rentabilidade_pct': []}
        
        try:
            # Agrupar por mês
            dados_mensais = df_filtrado.groupby('Mes').agg({
                'Frete Correto': 'sum',
                'Despesas Gerais': 'sum'
            }).reset_index()
            
            dados_mensais['rentabilidade_pct'] = (
                (dados_mensais['Frete Correto'] - dados_mensais['Despesas Gerais']) / 
                dados_mensais['Frete Correto'] * 100
            ).fillna(0)
            
            # Mapear números dos meses para nomes
            meses_nomes = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            dados_mensais['mes_nome'] = dados_mensais['Mes'].map(meses_nomes)
            
            return {
                'meses': dados_mensais['mes_nome'].tolist(),
                'frete_pagar': dados_mensais['Despesas Gerais'].round(2).tolist(),
                'frete_receber': dados_mensais['Frete Correto'].round(2).tolist(),
                'rentabilidade_pct': dados_mensais['rentabilidade_pct'].round(2).tolist()
            }
        except Exception as e:
            print(f"Erro ao calcular gráfico mensal: {e}")
            return {'meses': [], 'frete_pagar': [], 'frete_receber': [], 'rentabilidade_pct': []}

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
        
        dados = {
            'cards': painel_service.calcular_cards_resumo(df_filtrado),
            'grafico_diario': painel_service.calcular_grafico_diario_acumulativo(df_filtrado),
            'grafico_mensal': painel_service.calcular_grafico_mensal_rentabilidade(df_filtrado),
            'grafico_clientes': painel_service.calcular_grafico_clientes(df_filtrado),
            'grafico_veiculos': painel_service.calcular_grafico_veiculos(df_filtrado)
        }
        
        return jsonify(dados)
    except Exception as e:
        print(f"Erro na API dados: {e}")
        return jsonify({'error': str(e)}), 500
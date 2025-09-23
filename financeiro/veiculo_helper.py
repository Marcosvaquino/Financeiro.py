"""
Módulo auxiliar para consultas de veículos no sistema de suporte.
Usado para integração com manifestos e outras funcionalidades.
"""

import sqlite3
from typing import Dict, Optional, List
import os
import sys

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from financeiro.database import get_connection
except ImportError:
    # Fallback para conexão direta se não conseguir importar
    def get_connection():
        return sqlite3.connect('financeiro.db')

class VeiculoHelper:
    """Classe para consultas otimizadas de veículos"""
    
    @staticmethod
    def buscar_veiculo_por_placa(placa: str) -> Optional[Dict]:
        """
        Busca informações de um veículo pela placa
        
        Args:
            placa (str): Placa do veículo (será normalizada)
            
        Returns:
            Dict com dados do veículo ou None se não encontrado
        """
        if not placa:
            return None
            
        # Normalizar placa (maiúscula, sem espaços)
        placa_normalizada = str(placa).upper().strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT placa, status, tipologia, data_cadastro, ativo
                FROM veiculos_suporte 
                WHERE placa = ? AND ativo = 1
            """, (placa_normalizada,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return {
                    'placa': resultado[0],
                    'status': resultado[1],
                    'tipologia': resultado[2],
                    'data_cadastro': resultado[3],
                    'ativo': bool(resultado[4]),
                    'encontrado': True
                }
            else:
                return {
                    'placa': placa_normalizada,
                    'status': None,
                    'tipologia': None,
                    'data_cadastro': None,
                    'ativo': False,
                    'encontrado': False
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar veículo {placa}: {e}")
            return None
    
    @staticmethod
    def buscar_multiplas_placas(placas: List[str]) -> Dict[str, Dict]:
        """
        Busca informações de múltiplas placas de uma vez
        
        Args:
            placas (List[str]): Lista de placas para buscar
            
        Returns:
            Dict com placa como chave e dados como valor
        """
        if not placas:
            return {}
            
        # Normalizar todas as placas
        placas_normalizadas = [str(p).upper().strip() for p in placas if p]
        
        if not placas_normalizadas:
            return {}
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Criar placeholders para query
            placeholders = ','.join(['?' for _ in placas_normalizadas])
            
            cursor.execute(f"""
                SELECT placa, status, tipologia, data_cadastro, ativo
                FROM veiculos_suporte 
                WHERE placa IN ({placeholders}) AND ativo = 1
            """, placas_normalizadas)
            
            resultados = cursor.fetchall()
            conn.close()
            
            # Criar dicionário de resposta
            dados_encontrados = {}
            for resultado in resultados:
                dados_encontrados[resultado[0]] = {
                    'placa': resultado[0],
                    'status': resultado[1],
                    'tipologia': resultado[2],
                    'data_cadastro': resultado[3],
                    'ativo': bool(resultado[4]),
                    'encontrado': True
                }
            
            # Adicionar placas não encontradas
            for placa in placas_normalizadas:
                if placa not in dados_encontrados:
                    dados_encontrados[placa] = {
                        'placa': placa,
                        'status': None,
                        'tipologia': None,
                        'data_cadastro': None,
                        'ativo': False,
                        'encontrado': False
                    }
            
            return dados_encontrados
            
        except Exception as e:
            print(f"❌ Erro ao buscar múltiplas placas: {e}")
            return {}
    
    @staticmethod
    def get_status_resumo() -> Dict:
        """
        Retorna resumo dos status de veículos
        
        Returns:
            Dict com contadores por status
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as total,
                    SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) as ativos
                FROM veiculos_suporte 
                GROUP BY status
            """)
            
            resultados = cursor.fetchall()
            conn.close()
            
            resumo = {}
            total_geral = 0
            ativos_geral = 0
            
            for resultado in resultados:
                status = resultado[0]
                total = resultado[1]
                ativos = resultado[2]
                
                resumo[status] = {
                    'total': total,
                    'ativos': ativos,
                    'inativos': total - ativos
                }
                
                total_geral += total
                ativos_geral += ativos
            
            resumo['TOTAL'] = {
                'total': total_geral,
                'ativos': ativos_geral,
                'inativos': total_geral - ativos_geral
            }
            
            return resumo
            
        except Exception as e:
            print(f"❌ Erro ao obter resumo: {e}")
            return {}

# Funções de conveniência para uso direto
def get_veiculo_status(placa: str) -> Optional[str]:
    """
    Função simples para obter apenas o status de um veículo
    
    Args:
        placa (str): Placa do veículo
        
    Returns:
        Status do veículo (FIXO/SPOT) ou None se não encontrado
    """
    veiculo = VeiculoHelper.buscar_veiculo_por_placa(placa)
    return veiculo['status'] if veiculo and veiculo['encontrado'] else None

def get_veiculo_tipologia(placa: str) -> Optional[str]:
    """
    Função simples para obter apenas a tipologia de um veículo
    
    Args:
        placa (str): Placa do veículo
        
    Returns:
        Tipologia do veículo (3/4, TRUCK, etc.) ou None se não encontrado
    """
    veiculo = VeiculoHelper.buscar_veiculo_por_placa(placa)
    return veiculo['tipologia'] if veiculo and veiculo['encontrado'] else None

def verificar_veiculo_ativo(placa: str) -> bool:
    """
    Verifica se um veículo está ativo no sistema
    
    Args:
        placa (str): Placa do veículo
        
    Returns:
        True se veículo está ativo, False caso contrário
    """
    veiculo = VeiculoHelper.buscar_veiculo_por_placa(placa)
    return veiculo['ativo'] if veiculo and veiculo['encontrado'] else False

# Exemplo de uso para manifesto
def enriquecer_manifesto_com_veiculos(placas_manifesto: List[str]) -> Dict:
    """
    Enriquece dados do manifesto com informações dos veículos
    
    Args:
        placas_manifesto (List[str]): Lista de placas do manifesto
        
    Returns:
        Dict com dados enriquecidos para cada placa
    """
    dados_veiculos = VeiculoHelper.buscar_multiplas_placas(placas_manifesto)
    
    resultado = {
        'veiculos_encontrados': 0,
        'veiculos_nao_encontrados': 0,
        'status_fixo': 0,
        'status_spot': 0,
        'dados': dados_veiculos
    }
    
    for placa, dados in dados_veiculos.items():
        if dados['encontrado']:
            resultado['veiculos_encontrados'] += 1
            if dados['status'] == 'FIXO':
                resultado['status_fixo'] += 1
            elif dados['status'] == 'SPOT':
                resultado['status_spot'] += 1
        else:
            resultado['veiculos_nao_encontrados'] += 1
    
    return resultado

if __name__ == "__main__":
    # Teste rápido
    print("=== TESTE DO VEICULO HELPER ===")
    
    # Testar busca individual
    print("\n1. Teste busca individual:")
    veiculo_teste = VeiculoHelper.buscar_veiculo_por_placa("AXR4A69")
    print(f"Veiculo AXR4A69: {veiculo_teste}")
    
    # Testar busca múltipla
    print("\n2. Teste busca múltipla:")
    placas_teste = ["AXR4A69", "CDL3807", "PLACA_INEXISTENTE"]
    resultado_multiplo = VeiculoHelper.buscar_multiplas_placas(placas_teste)
    for placa, dados in resultado_multiplo.items():
        status = "✅ ENCONTRADO" if dados['encontrado'] else "❌ NÃO ENCONTRADO"
        print(f"  {placa}: {status} - Status: {dados['status']}")
    
    # Testar resumo
    print("\n3. Resumo dos status:")
    resumo = VeiculoHelper.get_status_resumo()
    for status, dados in resumo.items():
        print(f"  {status}: {dados['ativos']} ativos de {dados['total']} total")
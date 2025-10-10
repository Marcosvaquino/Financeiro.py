"""
Adaptador para Módulo Logística
===============================

Este módulo fornece uma interface simplificada para acessar
dados do banco logistica.db, mantendo compatibilidade com o código existente.
"""

from .database_manager import db_manager
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class LogisticaDB:
    """Adaptador para operações no banco logistica.db"""
    
    @staticmethod
    def get_connection():
        """Retorna conexão com o banco logística (compatibilidade)"""
        return db_manager.get_connection('logistica')
    
    @staticmethod
    def save_monitoring_data(data: List[Dict], status: str = "success") -> bool:
        """
        Salva dados de monitoramento
        
        Args:
            data: Lista de registros do monitoramento
            status: Status da operação
        """
        try:
            query = """
                INSERT INTO logistica_monitoring (data, status, registros_processados)
                VALUES (?, ?, ?)
            """
            params = (
                json.dumps(data, ensure_ascii=False) if data else None,
                status,
                len(data) if data else 0
            )
            
            db_manager.execute_query('logistica', query, params, fetch='none')
            return True
            
        except Exception as e:
            print(f"Erro ao salvar dados de monitoramento: {e}")
            return False
    
    @staticmethod
    def get_latest_monitoring_data() -> Optional[Dict]:
        """Obtém os dados mais recentes do monitoramento"""
        try:
            query = """
                SELECT data, timestamp, registros_processados
                FROM logistica_monitoring 
                WHERE status = 'success'
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            
            result = db_manager.execute_query('logistica', query, fetch='one')
            
            if result:
                return {
                    'data': json.loads(result[0]) if result[0] else [],
                    'timestamp': result[1],
                    'registros_processados': result[2]
                }
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter dados de monitoramento: {e}")
            return None
    
    @staticmethod
    def get_monitoring_history(limit: int = 100) -> List[Dict]:
        """Obtém histórico do monitoramento"""
        try:
            query = """
                SELECT timestamp, data, status, registros_processados
                FROM logistica_monitoring 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            
            rows = db_manager.execute_query('logistica', query, (limit,), fetch='all')
            
            historico = []
            for row in rows:
                data_parsed = None
                if row[1]:
                    try:
                        data_parsed = json.loads(row[1])
                    except:
                        pass
                
                historico.append({
                    'timestamp': row[0],
                    'data': data_parsed,
                    'status': row[2],
                    'registros_processados': row[3]
                })
            
            return historico
            
        except Exception as e:
            print(f"Erro ao obter histórico: {e}")
            return []
    
    @staticmethod
    def add_veiculo_operacional(placa: str, tipologia: str, perfil: str = None) -> bool:
        """Adiciona veículo operacional"""
        try:
            query = """
                INSERT OR REPLACE INTO veiculos_operacionais 
                (placa, tipologia, perfil, data_atualizacao)
                VALUES (?, ?, ?, ?)
            """
            params = (placa, tipologia, perfil, datetime.now())
            
            db_manager.execute_query('logistica', query, params, fetch='none')
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar veículo operacional: {e}")
            return False
    
    @staticmethod
    def get_veiculo_info(placa: str) -> Optional[Dict]:
        """Busca informações de um veículo operacional"""
        try:
            query = """
                SELECT placa, tipologia, perfil, status_operacional
                FROM veiculos_operacionais 
                WHERE placa = ?
            """
            
            result = db_manager.execute_query('logistica', query, (placa,), fetch='one')
            
            if result:
                return {
                    'placa': result[0],
                    'tipologia': result[1], 
                    'perfil': result[2],
                    'status_operacional': result[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar veículo: {e}")
            return None
    
    @staticmethod
    def create_alerta(tipo: str, titulo: str, descricao: str, severidade: str = 'media',
                     placa: str = None, viagem_id: int = None) -> bool:
        """Cria um alerta operacional"""
        try:
            query = """
                INSERT INTO alertas_operacionais 
                (tipo_alerta, titulo, descricao, severidade, placa, viagem_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (tipo, titulo, descricao, severidade, placa, viagem_id)
            
            db_manager.execute_query('logistica', query, params, fetch='none')
            return True
            
        except Exception as e:
            print(f"Erro ao criar alerta: {e}")
            return False
    
    @staticmethod
    def get_alertas_ativos() -> List[Dict]:
        """Obtém alertas ativos"""
        try:
            query = """
                SELECT id, tipo_alerta, titulo, descricao, severidade, 
                       placa, data_criacao
                FROM alertas_operacionais 
                WHERE status_alerta = 'ativo'
                ORDER BY 
                    CASE severidade 
                        WHEN 'critica' THEN 1
                        WHEN 'alta' THEN 2
                        WHEN 'media' THEN 3
                        WHEN 'baixa' THEN 4
                    END,
                    data_criacao DESC
            """
            
            rows = db_manager.execute_query('logistica', query, fetch='all')
            
            alertas = []
            for row in rows:
                alertas.append({
                    'id': row[0],
                    'tipo_alerta': row[1],
                    'titulo': row[2],
                    'descricao': row[3],
                    'severidade': row[4],
                    'placa': row[5],
                    'data_criacao': row[6]
                })
            
            return alertas
            
        except Exception as e:
            print(f"Erro ao obter alertas: {e}")
            return []

# Função de compatibilidade para código legado
def init_monitoring_db():
    """Inicializa tabelas de monitoramento (compatibilidade)"""
    pass  # As tabelas já são criadas pelo schema

def get_db_path():
    """Retorna caminho do banco logística (compatibilidade)"""
    return db_manager.get_db_path('logistica')
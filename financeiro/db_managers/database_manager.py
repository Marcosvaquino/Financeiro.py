"""
Sistema de Gerenciamento de Bancos de Dados Modular
===================================================

Este módulo gerencia múltiplos bancos SQLite de forma independente,
evitando travamentos e melhorando a performance.

Estrutura:
- core.db: Usuários, autenticação, sessões
- logistica.db: Monitoramento, rotas, entregas, veículos operacionais  
- manifesto.db: Dados de manifesto, cargas, fretes
- suporte.db: Clientes, veículos de suporte, configurações
- margem.db: Análises financeiras, custos, rentabilidade
"""

import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import Optional, Dict, Any

class DatabaseManager:
    """Gerenciador central de bancos de dados modulares"""
    
    # Mapeamento de módulos para bancos
    DB_MAPPING = {
        'core': 'core.db',
        'logistica': 'logistica.db', 
        'manifesto': 'manifesto.db',
        'suporte': 'suporte.db',
        'margem': 'margem.db'
    }
    
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', 'databases')
        self.connections = {}
        self.locks = {db: threading.Lock() for db in self.DB_MAPPING.keys()}
        
        # Garantir que o diretório existe
        os.makedirs(self.base_dir, exist_ok=True)
        
    def get_db_path(self, module: str) -> str:
        """Retorna o caminho completo para o banco do módulo"""
        if module not in self.DB_MAPPING:
            raise ValueError(f"Módulo '{module}' não encontrado. Módulos disponíveis: {list(self.DB_MAPPING.keys())}")
        
        return os.path.join(self.base_dir, self.DB_MAPPING[module])
    
    @contextmanager
    def get_connection(self, module: str, timeout: int = 30):
        """
        Context manager para obter conexão segura com um banco específico
        
        Args:
            module: Nome do módulo (core, logistica, manifesto, suporte, margem)
            timeout: Timeout em segundos para operações de banco
            
        Usage:
            with db_manager.get_connection('logistica') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM monitoring")
        """
        db_path = self.get_db_path(module)
        
        with self.locks[module]:
            conn = None
            try:
                # Criar conexão com configurações otimizadas
                conn = sqlite3.connect(db_path, timeout=timeout)
                conn.row_factory = sqlite3.Row
                
                # Configurações para melhor performance e concorrência
                conn.execute('PRAGMA journal_mode=WAL;')
                conn.execute(f'PRAGMA busy_timeout = {timeout * 1000};')
                conn.execute('PRAGMA synchronous = NORMAL;')
                conn.execute('PRAGMA cache_size = 10000;')
                conn.execute('PRAGMA temp_store = memory;')
                
                yield conn
                
            except Exception as e:
                if conn:
                    conn.rollback()
                raise e
            finally:
                if conn:
                    conn.close()
    
    def execute_query(self, module: str, query: str, params: tuple = (), fetch: str = 'all') -> Any:
        """
        Executa uma query de forma segura
        
        Args:
            module: Nome do módulo
            query: Query SQL
            params: Parâmetros da query
            fetch: 'all', 'one', 'none' (para INSERT/UPDATE/DELETE)
        """
        with self.get_connection(module) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch == 'all':
                return cursor.fetchall()
            elif fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'none':
                conn.commit()
                return cursor.rowcount
            else:
                raise ValueError("fetch deve ser 'all', 'one' ou 'none'")
    
    def init_database(self, module: str, schema_sql: str):
        """Inicializa um banco de dados com o schema fornecido"""
        with self.get_connection(module) as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            conn.commit()
            print(f"✅ Banco {module}.db inicializado com sucesso!")
    
    def migrate_data(self, source_db_path: str, module: str, table_mappings: Dict[str, str]):
        """
        Migra dados de um banco existente para o novo banco modular
        
        Args:
            source_db_path: Caminho do banco original
            module: Módulo de destino
            table_mappings: Mapeamento {tabela_origem: tabela_destino}
        """
        print(f"🔄 Migrando dados para {module}.db...")
        
        # Conectar ao banco original
        source_conn = sqlite3.connect(source_db_path)
        source_conn.row_factory = sqlite3.Row
        
        try:
            with self.get_connection(module) as dest_conn:
                for source_table, dest_table in table_mappings.items():
                    try:
                        # Verificar se a tabela existe no banco origem
                        source_cursor = source_conn.cursor()
                        source_cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                            (source_table,)
                        )
                        
                        if not source_cursor.fetchone():
                            print(f"⚠️  Tabela {source_table} não encontrada no banco origem")
                            continue
                        
                        # Obter dados da tabela origem
                        source_cursor.execute(f"SELECT * FROM {source_table}")
                        rows = source_cursor.fetchall()
                        
                        if not rows:
                            print(f"ℹ️  Tabela {source_table} está vazia")
                            continue
                        
                        # Obter colunas da primeira linha
                        columns = list(rows[0].keys())
                        
                        # Preparar query de inserção
                        placeholders = ','.join(['?' for _ in columns])
                        insert_query = f"INSERT OR REPLACE INTO {dest_table} ({','.join(columns)}) VALUES ({placeholders})"
                        
                        # Inserir dados
                        dest_cursor = dest_conn.cursor()
                        for row in rows:
                            dest_cursor.execute(insert_query, tuple(row))
                        
                        dest_conn.commit()
                        print(f"✅ {len(rows)} registros migrados de {source_table} para {dest_table}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao migrar tabela {source_table}: {e}")
                        continue
                        
        finally:
            source_conn.close()
    
    def health_check(self) -> Dict[str, bool]:
        """Verifica a saúde de todos os bancos"""
        status = {}
        
        for module in self.DB_MAPPING.keys():
            try:
                with self.get_connection(module) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    status[module] = True
            except Exception as e:
                print(f"❌ Erro no banco {module}: {e}")
                status[module] = False
        
        return status

# Instância global do gerenciador
db_manager = DatabaseManager()
"""
Manager Central de Bancos de Dados Modulares
Gerencia conexões para cada módulo específico
"""
import sqlite3
import os
from pathlib import Path

class DatabaseManager:
    """Manager central para todos os bancos modulares"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.databases_dir = self.base_dir / "databases"
        self.databases_dir.mkdir(exist_ok=True)
        
        # Configuração dos bancos por módulo
        self.db_configs = {
            'core': {
                'file': 'core.db',
                'description': 'Usuários, autenticação, configurações centrais'
            },
            'logistica': {
                'file': 'logistica.db', 
                'description': 'Monitoramento, rotas, entregas'
            },
            'manifesto': {
                'file': 'manifesto.db',
                'description': 'Dados de manifesto e cargas'
            },
            'suporte': {
                'file': 'suporte.db',
                'description': 'Clientes, veículos, configurações de suporte'
            },
            'margem': {
                'file': 'margem.db',
                'description': 'Análises de margem e custos'
            }
        }
    
    def get_db_path(self, module_name):
        """Retorna o caminho para o banco de um módulo específico"""
        if module_name not in self.db_configs:
            raise ValueError(f"Módulo '{module_name}' não configurado")
        
        return self.databases_dir / self.db_configs[module_name]['file']
    
    def get_connection(self, module_name, timeout=30):
        """Cria conexão otimizada para um módulo específico"""
        db_path = self.get_db_path(module_name)
        
        # Conexão com timeout e otimizações
        conn = sqlite3.connect(str(db_path), timeout=timeout)
        conn.row_factory = sqlite3.Row
        
        # Configurações de performance e concorrência
        try:
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('PRAGMA busy_timeout = 30000;')
            conn.execute('PRAGMA synchronous = NORMAL;')
            conn.execute('PRAGMA cache_size = 10000;')
            conn.execute('PRAGMA temp_store = MEMORY;')
        except Exception:
            pass
            
        return conn
    
    def initialize_all_databases(self):
        """Inicializa todos os bancos modulares"""
        for module_name in self.db_configs:
            self._create_database_if_not_exists(module_name)
    
    def _create_database_if_not_exists(self, module_name):
        """Cria um banco se não existir"""
        db_path = self.get_db_path(module_name)
        if not db_path.exists():
            # Criar banco vazio
            conn = sqlite3.connect(str(db_path))
            conn.execute('SELECT 1;')  # Testa se banco foi criado
            conn.close()
            print(f"✅ Banco {module_name}.db criado")
    
    def backup_module(self, module_name, backup_suffix="backup"):
        """Cria backup de um módulo específico"""
        db_path = self.get_db_path(module_name)
        if db_path.exists():
            backup_path = db_path.with_suffix(f'.{backup_suffix}.db')
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backup criado: {backup_path}")
            return backup_path
        return None
    
    def get_status(self):
        """Retorna status de todos os bancos"""
        status = {}
        for module_name, config in self.db_configs.items():
            db_path = self.get_db_path(module_name)
            status[module_name] = {
                'exists': db_path.exists(),
                'size': db_path.stat().st_size if db_path.exists() else 0,
                'description': config['description']
            }
        return status

# Instância global do manager
db_manager = DatabaseManager()
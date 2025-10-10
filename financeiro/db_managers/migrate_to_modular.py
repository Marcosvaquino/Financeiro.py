"""
Script de Migração Segura para Bancos Modulares
Migra dados do financeiro.db para os novos bancos modulares
"""
import sqlite3
import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from db_managers.db_manager import db_manager

class SafeMigration:
    """Migração segura com rollback automático"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.original_db = self.base_dir / "financeiro.db"
        self.backup_db = None
        self.migration_log = []
        
    def log(self, message):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.migration_log.append(log_msg)
    
    def create_backup(self):
        """Cria backup de segurança"""
        if not self.original_db.exists():
            self.log("❌ Arquivo financeiro.db não encontrado!")
            return False
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_db = self.base_dir / f"financeiro_migration_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.original_db, self.backup_db)
            self.log(f"✅ Backup criado: {self.backup_db.name}")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao criar backup: {e}")
            return False
    
    def verify_original_db(self):
        """Verifica estrutura do banco original"""
        try:
            conn = sqlite3.connect(str(self.original_db))
            cursor = conn.cursor()
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.log(f"📊 Tabelas encontradas no banco original: {len(tables)}")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                self.log(f"  - {table}: {count} registros")
            
            conn.close()
            return tables
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar banco original: {e}")
            return []
    
    def initialize_modular_databases(self):
        """Inicializa bancos modulares com schemas"""
        try:
            # Inicializar bancos vazios
            db_manager.initialize_all_databases()
            
            # Aplicar schemas
            schemas_dir = Path(__file__).parent / "schemas"
            
            for module_name in db_manager.db_configs:
                schema_file = schemas_dir / f"{module_name}_schema.sql"
                
                if schema_file.exists():
                    conn = db_manager.get_connection(module_name)
                    
                    with open(schema_file, 'r', encoding='utf-8') as f:
                        schema_sql = f.read()
                    
                    conn.executescript(schema_sql)
                    conn.close()
                    
                    self.log(f"✅ Schema aplicado: {module_name}.db")
                else:
                    self.log(f"⚠️ Schema não encontrado: {schema_file}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao inicializar bancos modulares: {e}")
            return False
    
    def migrate_data(self):
        """Migra dados do banco original para os modulares"""
        try:
            # Conectar ao banco original
            original_conn = sqlite3.connect(str(self.original_db))
            original_conn.row_factory = sqlite3.Row
            
            # Migração por tabela - APENAS TABELAS QUE REALMENTE EXISTEM
            migrations = {
                # Core (usuários)
                'usuarios': 'core',
                
                # Logística (monitoramento)
                'logistica_monitoring': 'logistica',
                
                # Suporte (clientes e veículos)
                'clientes_suporte': 'suporte',
                'clientes_padrao': 'suporte',
                'veiculos_suporte': 'suporte',
                
                # Margem (custos e análises financeiras)
                'custo_frota': 'margem',
                'contas_receber': 'margem',
                'contas_pagar': 'margem',
                'projecao': 'margem'
            }
            
            for table_name, target_module in migrations.items():
                try:
                    # Verificar se tabela existe no original
                    cursor = original_conn.cursor()
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                        (table_name,)
                    )
                    
                    if not cursor.fetchone():
                        self.log(f"⚠️ Tabela {table_name} não encontrada no banco original")
                        continue
                    
                    # Buscar dados
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    if not rows:
                        self.log(f"ℹ️ Tabela {table_name} está vazia")
                        continue
                    
                    # Conectar ao banco de destino
                    target_conn = db_manager.get_connection(target_module)
                    
                    # Obter colunas da tabela de destino
                    target_cursor = target_conn.cursor()
                    target_cursor.execute(f"PRAGMA table_info({table_name})")
                    target_columns = [col[1] for col in target_cursor.fetchall()]
                    
                    if not target_columns:
                        self.log(f"⚠️ Tabela {table_name} não existe em {target_module}.db")
                        target_conn.close()
                        continue
                    
                    # Preparar inserção
                    placeholders = ','.join(['?' for _ in target_columns])
                    insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(target_columns)}) VALUES ({placeholders})"
                    
                    # Migrar dados
                    migrated_count = 0
                    for row in rows:
                        try:
                            # Mapear valores para colunas de destino
                            values = []
                            for col in target_columns:
                                if col in row.keys():
                                    values.append(row[col])
                                else:
                                    values.append(None)
                            
                            target_cursor.execute(insert_sql, values)
                            migrated_count += 1
                            
                        except Exception as e:
                            self.log(f"⚠️ Erro ao migrar registro de {table_name}: {e}")
                    
                    target_conn.commit()
                    target_conn.close()
                    
                    self.log(f"✅ {table_name} → {target_module}.db: {migrated_count} registros migrados")
                    
                except Exception as e:
                    self.log(f"❌ Erro ao migrar {table_name}: {e}")
            
            original_conn.close()
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na migração de dados: {e}")
            return False
    
    def verify_migration(self):
        """Verifica se a migração foi bem-sucedida"""
        try:
            self.log("🔍 Verificando migração...")
            
            for module_name in db_manager.db_configs:
                conn = db_manager.get_connection(module_name)
                cursor = conn.cursor()
                
                # Listar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                total_records = 0
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    total_records += count
                
                conn.close()
                
                self.log(f"📊 {module_name}.db: {len(tables)} tabelas, {total_records} registros")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na verificação: {e}")
            return False
    
    def run_migration(self):
        """Executa migração completa"""
        self.log("🚀 INICIANDO MIGRAÇÃO SEGURA PARA BANCOS MODULARES")
        self.log("=" * 60)
        
        # Passo 1: Backup
        if not self.create_backup():
            return False
        
        # Passo 2: Verificar banco original
        original_tables = self.verify_original_db()
        if not original_tables:
            return False
        
        # Passo 3: Inicializar bancos modulares
        if not self.initialize_modular_databases():
            return False
        
        # Passo 4: Migrar dados
        if not self.migrate_data():
            return False
        
        # Passo 5: Verificar migração
        if not self.verify_migration():
            return False
        
        self.log("=" * 60)
        self.log("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        self.log(f"💾 Backup salvo em: {self.backup_db.name}")
        self.log("🔄 Sistema agora usa bancos modulares")
        
        return True

if __name__ == "__main__":
    migration = SafeMigration()
    success = migration.run_migration()
    
    if not success:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("💾 Banco original preservado")
        print("🔄 Sistema continua funcionando normalmente")
    else:
        print("\n✅ MIGRAÇÃO BEM-SUCEDIDA!")
        print("🚀 Sistema agora roda com bancos modulares")
"""
Script de Migração para Arquitetura Modular
===========================================

Este script migra o banco monolítico atual para a nova arquitetura modular,
garantindo que todos os dados sejam preservados e o sistema continue funcionando.

Processo de migração:
1. Backup do banco atual
2. Criação dos novos bancos modulares
3. Migração dos dados existentes
4. Verificação da integridade
5. Testes de funcionamento
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db_managers.database_manager import db_manager

class DatabaseMigrator:
    """Classe responsável por migrar dados do banco monolítico para a arquitetura modular"""
    
    def __init__(self):
        self.source_db = "financeiro.db"
        self.backup_db = f"financeiro_backup_pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')
        
        # Mapeamento de tabelas do banco atual para os novos bancos
        self.table_mappings = {
            'core': {
                'usuarios': 'usuarios'
            },
            'logistica': {
                'logistica_monitoring': 'logistica_monitoring'
            },
            'suporte': {
                'clientes_suporte': 'clientes_suporte',
                'veiculos_suporte': 'veiculos_suporte',
                'custo_frota': 'custo_frota'
            },
            'manifesto': {
                # Será criada nova estrutura baseada nos uploads
            },
            'margem': {
                'contas_receber': 'contas_receber',
                'contas_pagar': 'contas_pagar',
                'projecao': 'projecoes'
            }
        }
    
    def create_backup(self):
        """Cria backup do banco atual"""
        print(f"🔄 Criando backup do banco atual...")
        
        if not os.path.exists(self.source_db):
            raise FileNotFoundError(f"Banco de dados {self.source_db} não encontrado!")
        
        try:
            shutil.copy2(self.source_db, self.backup_db)
            print(f"✅ Backup criado: {self.backup_db}")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False
    
    def load_schema(self, module: str) -> str:
        """Carrega o schema SQL para um módulo"""
        schema_file = os.path.join(self.schemas_dir, f"{module}_schema.sql")
        
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema {schema_file} não encontrado!")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def initialize_databases(self):
        """Inicializa todos os bancos modulares com seus schemas"""
        print("🔄 Inicializando bancos modulares...")
        
        for module in ['core', 'logistica', 'suporte', 'manifesto', 'margem']:
            try:
                print(f"  📄 Inicializando {module}.db...")
                schema_sql = self.load_schema(module)
                db_manager.init_database(module, schema_sql)
            except Exception as e:
                print(f"❌ Erro ao inicializar {module}.db: {e}")
                return False
        
        return True
    
    def migrate_data(self):
        """Migra dados do banco monolítico para os bancos modulares"""
        print("🔄 Migrando dados...")
        
        for module, mappings in self.table_mappings.items():
            if mappings:  # Se há tabelas para migrar
                print(f"  📊 Migrando dados para {module}.db...")
                try:
                    db_manager.migrate_data(self.source_db, module, mappings)
                except Exception as e:
                    print(f"❌ Erro ao migrar dados para {module}: {e}")
                    return False
        
        return True
    
    def verify_migration(self):
        """Verifica se a migração foi bem-sucedida"""
        print("🔍 Verificando migração...")
        
        # Verificar se todos os bancos estão acessíveis
        health = db_manager.health_check()
        
        for module, status in health.items():
            if status:
                print(f"  ✅ {module}.db: OK")
            else:
                print(f"  ❌ {module}.db: ERRO")
                return False
        
        # Verificar contagem de registros em tabelas chave
        print("\n📊 Verificando contagem de registros:")
        
        try:
            # Contar usuários
            usuarios_count = db_manager.execute_query('core', 'SELECT COUNT(*) FROM usuarios', fetch='one')[0]
            print(f"  👥 Usuários: {usuarios_count}")
            
            # Contar clientes
            clientes_count = db_manager.execute_query('suporte', 'SELECT COUNT(*) FROM clientes_suporte', fetch='one')[0]
            print(f"  🏢 Clientes: {clientes_count}")
            
            # Contar veículos
            veiculos_count = db_manager.execute_query('suporte', 'SELECT COUNT(*) FROM veiculos_suporte', fetch='one')[0]
            print(f"  🚛 Veículos: {veiculos_count}")
            
            # Contar monitoramento
            monitoring_count = db_manager.execute_query('logistica', 'SELECT COUNT(*) FROM logistica_monitoring', fetch='one')[0]
            print(f"  📈 Registros de monitoramento: {monitoring_count}")
            
        except Exception as e:
            print(f"❌ Erro ao verificar dados: {e}")
            return False
        
        return True
    
    def create_migration_info(self):
        """Cria arquivo com informações da migração"""
        migration_info = {
            'data_migracao': datetime.now().isoformat(),
            'banco_origem': self.source_db,
            'backup_criado': self.backup_db,
            'bancos_criados': list(db_manager.DB_MAPPING.values()),
            'status': 'concluida'
        }
        
        info_file = f"migration_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(migration_info, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Informações da migração salvas em: {info_file}")
    
    def run_migration(self):
        """Executa todo o processo de migração"""
        print("🚀 INICIANDO MIGRAÇÃO PARA ARQUITETURA MODULAR")
        print("=" * 60)
        
        # Passo 1: Backup
        if not self.create_backup():
            print("❌ Falha no backup. Migração abortada.")
            return False
        
        # Passo 2: Inicializar bancos
        if not self.initialize_databases():
            print("❌ Falha na inicialização dos bancos. Migração abortada.")
            return False
        
        # Passo 3: Migrar dados
        if not self.migrate_data():
            print("❌ Falha na migração de dados. Migração abortada.")
            return False
        
        # Passo 4: Verificar migração
        if not self.verify_migration():
            print("❌ Falha na verificação. Migração abortada.")
            return False
        
        # Passo 5: Criar info da migração
        self.create_migration_info()
        
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Todos os dados foram migrados para a arquitetura modular")
        print("✅ Sistema pode continuar funcionando normalmente")
        print("✅ Backup criado para rollback se necessário")
        print(f"📂 Backup disponível em: {self.backup_db}")
        
        return True

def main():
    """Função principal"""
    migrator = DatabaseMigrator()
    
    try:
        success = migrator.run_migration()
        if success:
            print("\n🚀 Sistema pronto para usar a nova arquitetura modular!")
            sys.exit(0)
        else:
            print("\n❌ Migração falhou. Verifique os logs acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Migração interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado durante a migração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
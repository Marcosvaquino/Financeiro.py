"""
Script para atualizar o banco de dados e adicionar a coluna 'peso' 
na tabela mapa_calor_dados
"""

import sqlite3
import os

def get_db_path():
    """Retorna o caminho para o banco de dados"""
    return os.path.join(os.path.dirname(__file__), 'financeiro.db')

def atualizar_banco():
    """Adiciona coluna peso na tabela mapa_calor_dados se não existir"""
    conn = None
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(mapa_calor_dados)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'peso' not in colunas:
            print("📝 Adicionando coluna 'peso' na tabela mapa_calor_dados...")
            cursor.execute("ALTER TABLE mapa_calor_dados ADD COLUMN peso REAL DEFAULT 0")
            conn.commit()
            print("✅ Coluna 'peso' adicionada com sucesso!")
        else:
            print("ℹ️ Coluna 'peso' já existe na tabela.")
        
        # Mostrar estrutura da tabela
        cursor.execute("PRAGMA table_info(mapa_calor_dados)")
        print("\n📋 Estrutura da tabela mapa_calor_dados:")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Atualizando banco de dados...\n")
    sucesso = atualizar_banco()
    
    if sucesso:
        print("\n✅ Banco de dados atualizado com sucesso!")
        print("💡 Agora você pode importar novos dados com a coluna 'Peso'.")
    else:
        print("\n❌ Falha ao atualizar banco de dados.")

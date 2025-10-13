import sqlite3
import sys
import os

# Configurar o path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar as funções do sistema
from financeiro.database import init_db, get_connection

def testar_filtro_real():
    """Testa o filtro real com logs detalhados"""
    print("=" * 60)
    print("🔍 TESTE REAL DO FILTRO DE MENUS")
    print("=" * 60)
    
    # Verificar usuários existentes
    print("\n1️⃣ USUÁRIOS NO SISTEMA:")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, perfil FROM usuarios")
    usuarios = cursor.fetchall()
    
    for user in usuarios:
        print(f"   ID: {user[0]} | Username: {user[1]} | Perfil: {user[2]}")
    
    # Testar função get_user_menus diretamente
    print("\n2️⃣ TESTANDO FUNÇÃO get_user_menus:")
    
    # Importar a função
    from financeiro.main import get_user_menus
    
    for user in usuarios:
        user_id = user[0]
        print(f"\n   📋 USUÁRIO: {user[1]} (ID: {user_id})")
        
        # Buscar menus para este usuário
        menus = get_user_menus(user_id)
        
        print(f"   📊 TOTAL DE CATEGORIAS: {len(menus)}")
        
        for categoria, itens in menus.items():
            print(f"      🗂️ {categoria}: {len(itens)} itens")
            for item in itens:
                print(f"         • {item['nome']} -> {item['rota']}")
    
    # Verificar permissões específicas
    print("\n3️⃣ PERMISSÕES NO BANCO:")
    cursor.execute("""
        SELECT u.email, p.categoria, p.menu_item, p.permitido
        FROM user_permissions p
        JOIN usuarios u ON p.user_id = u.id
        ORDER BY u.email, p.categoria, p.menu_item
    """)
    
    permissions = cursor.fetchall()
    
    current_user = None
    for perm in permissions:
        if perm[0] != current_user:
            current_user = perm[0]
            print(f"\n   👤 {current_user}:")
        
        status = "✅" if perm[3] else "❌"
        print(f"      {status} {perm[1]}.{perm[2]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_filtro_real()
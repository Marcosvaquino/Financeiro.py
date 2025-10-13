import sqlite3
import sys
import os

# Configurar o path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar as funções do sistema
from financeiro.database import get_connection

def configurar_permissoes_junior():
    """Configura permissões básicas para o usuário junior"""
    print("=" * 60)
    print("🔧 CONFIGURANDO PERMISSÕES PARA JUNIOR")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar ID do junior
    cursor.execute("SELECT id FROM usuarios WHERE email = 'junior@friozer.com.br'")
    junior = cursor.fetchone()
    
    if not junior:
        print("❌ Usuário junior não encontrado!")
        conn.close()
        return
    
    junior_id = junior[0]
    print(f"✅ Junior encontrado - ID: {junior_id}")
    
    # Buscar alguns menus para dar permissão
    cursor.execute("SELECT id, nome, categoria FROM menus_sistema WHERE categoria IN ('financeiro', 'frete') LIMIT 5")
    menus = cursor.fetchall()
    
    print(f"\n🗂️ Configurando permissões para {len(menus)} menus:")
    
    for menu in menus:
        menu_id = menu[0]
        
        # Verificar se já existe permissão
        cursor.execute("SELECT id FROM usuario_permissoes WHERE usuario_id = ? AND menu_id = ?", (junior_id, menu_id))
        existing = cursor.fetchone()
        
        if not existing:
            # Criar permissão
            cursor.execute("""
                INSERT INTO usuario_permissoes (usuario_id, menu_id, pode_acessar)
                VALUES (?, ?, 1)
            """, (junior_id, menu_id))
            print(f"   ✅ {menu[2]}.{menu[1]} - ADICIONADO")
        else:
            # Atualizar permissão
            cursor.execute("""
                UPDATE usuario_permissoes 
                SET pode_acessar = 1 
                WHERE usuario_id = ? AND menu_id = ?
            """, (junior_id, menu_id))
            print(f"   🔄 {menu[2]}.{menu[1]} - ATUALIZADO")
    
    conn.commit()
    
    # Verificar resultado
    cursor.execute("""
        SELECT m.categoria, m.nome, up.pode_acessar
        FROM usuario_permissoes up
        JOIN menus_sistema m ON up.menu_id = m.id
        WHERE up.usuario_id = ?
        ORDER BY m.categoria, m.nome
    """, (junior_id,))
    
    permissoes = cursor.fetchall()
    
    print(f"\n📋 PERMISSÕES ATUAIS DO JUNIOR ({len(permissoes)} total):")
    current_cat = None
    for perm in permissoes:
        if perm[0] != current_cat:
            current_cat = perm[0]
            print(f"\n   🗂️ {current_cat.upper()}:")
        
        status = "✅" if perm[2] else "❌"
        print(f"      {status} {perm[1]}")
    
    conn.close()
    
    print(f"\n" + "=" * 60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA")
    print("💡 Agora faça login como junior para testar!")

if __name__ == "__main__":
    configurar_permissoes_junior()
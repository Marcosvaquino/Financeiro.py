#!/usr/bin/env python3
"""
Script para remover permissão de Admin do Junior Reis
"""
import sqlite3

def remover_admin_junior():
    """Remove permissão de Admin do Junior Reis"""
    try:
        conn = sqlite3.connect('financeiro.db')
        cursor = conn.cursor()
        
        # Encontrar ID do menu Admin (Gestão de Usuários)
        cursor.execute('SELECT id FROM menus_sistema WHERE categoria = "admin"')
        admin_menu = cursor.fetchone()
        
        if admin_menu:
            admin_menu_id = admin_menu[0]
            # Remover permissão de Admin do Junior Reis (ID 2)
            cursor.execute('DELETE FROM usuario_permissoes WHERE usuario_id = 2 AND menu_id = ?', (admin_menu_id,))
            print('✅ Permissão de Admin removida do Junior Reis')
            conn.commit()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    remover_admin_junior()
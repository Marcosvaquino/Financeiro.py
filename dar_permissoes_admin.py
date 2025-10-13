#!/usr/bin/env python3
"""
Script para dar todas as permissões ao usuário admin
"""
import sqlite3
import os

def dar_permissoes_admin():
    """Concede todas as permissões ao usuário admin"""
    db_path = 'financeiro.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Encontrar o usuário admin
        cursor.execute('SELECT id, nome FROM usuarios WHERE perfil = "admin" LIMIT 1')
        admin = cursor.fetchone()
        
        if not admin:
            print("❌ Usuário admin não encontrado!")
            return
        
        admin_id, admin_nome = admin
        print(f"✅ Admin encontrado: {admin_nome} (ID: {admin_id})")
        
        # Buscar todos os menus ativos
        cursor.execute('SELECT id, nome, categoria FROM menus_sistema WHERE ativo = 1')
        menus = cursor.fetchall()
        
        if not menus:
            print("❌ Nenhum menu encontrado!")
            return
        
        print(f"📋 Encontrados {len(menus)} menus para conceder permissões:")
        
        # Dar todas as permissões para o admin
        permissoes_concedidas = 0
        for menu_id, menu_nome, categoria in menus:
            cursor.execute('''
                INSERT OR REPLACE INTO usuario_permissoes (usuario_id, menu_id, pode_acessar)
                VALUES (?, ?, 1)
            ''', (admin_id, menu_id))
            print(f"  ✅ {categoria} → {menu_nome}")
            permissoes_concedidas += 1
        
        conn.commit()
        print(f"\n🎉 {permissoes_concedidas} permissões concedidas ao admin {admin_nome}!")
        
        # Verificar se as permissões foram salvas
        cursor.execute('''
            SELECT COUNT(*) FROM usuario_permissoes 
            WHERE usuario_id = ? AND pode_acessar = 1
        ''', (admin_id,))
        total_permissoes = cursor.fetchone()[0]
        print(f"✅ Verificação: {total_permissoes} permissões ativas no banco")
        
    except Exception as e:
        print(f"❌ Erro ao conceder permissões: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    dar_permissoes_admin()
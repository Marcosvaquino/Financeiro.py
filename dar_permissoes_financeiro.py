#!/usr/bin/env python3
"""
Script para dar permissões apenas de Financeiro para o Junior Reis
"""
import sqlite3
import os

def dar_permissoes_financeiro():
    """Dar apenas permissões de Financeiro para Junior Reis"""
    db_path = 'financeiro.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Encontrar o Junior Reis
        cursor.execute('SELECT id, nome FROM usuarios WHERE nome LIKE "%Junior%" OR nome LIKE "%Reis%"')
        user = cursor.fetchone()
        
        if not user:
            print("❌ Junior Reis não encontrado!")
            return
        
        user_id, user_name = user
        print(f"✅ Usuário encontrado: {user_name} (ID: {user_id})")
        
        # Limpar permissões antigas do usuário
        cursor.execute('DELETE FROM usuario_permissoes WHERE usuario_id = ?', (user_id,))
        
        # Buscar apenas menus da categoria 'financeiro'
        cursor.execute('SELECT id, nome FROM menus_sistema WHERE categoria = "financeiro" AND ativo = 1')
        menus_financeiro = cursor.fetchall()
        
        print(f"📋 Concedendo acesso apenas aos menus de FINANCEIRO:")
        for menu_id, menu_nome in menus_financeiro:
            cursor.execute('''
                INSERT INTO usuario_permissoes (usuario_id, menu_id, pode_acessar)
                VALUES (?, ?, 1)
            ''', (user_id, menu_id))
            print(f"  ✅ {menu_nome}")
        
        conn.commit()
        print(f"\n🎉 {len(menus_financeiro)} permissões de Financeiro concedidas ao {user_name}!")
        
        # Verificar permissões finais
        cursor.execute('''
            SELECT m.categoria, m.nome
            FROM usuario_permissoes up
            JOIN menus_sistema m ON up.menu_id = m.id
            WHERE up.usuario_id = ? AND up.pode_acessar = 1
            ORDER BY m.categoria, m.ordem
        ''', (user_id,))
        
        permissoes = cursor.fetchall()
        print(f"\n📊 Verificação - {user_name} pode acessar:")
        for categoria, nome in permissoes:
            print(f"  🔸 {categoria.upper()}: {nome}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    dar_permissoes_financeiro()
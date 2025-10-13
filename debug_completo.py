#!/usr/bin/env python3
"""
Debug completo do sistema de login e menus
"""
import sqlite3

def debug_completo():
    """Debug completo do sistema"""
    try:
        conn = sqlite3.connect('financeiro.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔍 DEBUG COMPLETO DO SISTEMA DE USUÁRIOS E MENUS\n")
        
        # 1. Verificar todos os usuários
        print("1️⃣ USUÁRIOS NO SISTEMA:")
        cursor.execute('SELECT * FROM usuarios ORDER BY id')
        usuarios = cursor.fetchall()
        for user in usuarios:
            print(f"   ID: {user['id']} | Nome: {user['nome']} | Email: {user['email']} | Perfil: {user['perfil']}")
        
        # 2. Verificar todas as permissões
        print(f"\n2️⃣ PERMISSÕES POR USUÁRIO:")
        for user in usuarios:
            user_id = user['id']
            user_name = user['nome']
            user_perfil = user['perfil']
            
            cursor.execute('''
                SELECT m.categoria, m.nome, up.pode_acessar
                FROM usuario_permissoes up
                JOIN menus_sistema m ON up.menu_id = m.id
                WHERE up.usuario_id = ? AND up.pode_acessar = 1
                ORDER BY m.categoria, m.nome
            ''', (user_id,))
            
            permissoes = cursor.fetchall()
            print(f"   👤 {user_name} ({user_perfil}): {len(permissoes)} permissões")
            
            categorias = {}
            for perm in permissoes:
                cat = perm['categoria']
                if cat not in categorias:
                    categorias[cat] = []
                categorias[cat].append(perm['nome'])
            
            for cat, itens in categorias.items():
                print(f"      📁 {cat}: {itens}")
        
        # 3. Simular login de cada usuário
        print(f"\n3️⃣ SIMULAÇÃO DE LOGIN E MENU:")
        for user in usuarios:
            user_id = user['id']
            user_name = user['nome']
            user_perfil = user['perfil']
            
            print(f"\n   🔐 SIMULANDO LOGIN: {user_name}")
            
            # Simular função get_user_menus
            if user_perfil == 'admin':
                cursor.execute("""
                    SELECT nome, rota, categoria, ordem
                    FROM menus_sistema 
                    WHERE ativo = 1
                    ORDER BY categoria, ordem, nome
                """)
                print("      🔑 ADMIN - Carregando TODOS os menus")
            else:
                cursor.execute("""
                    SELECT m.nome, m.rota, m.categoria, m.ordem
                    FROM menus_sistema m
                    JOIN usuario_permissoes up ON m.id = up.menu_id
                    WHERE up.usuario_id = ? AND up.pode_acessar = 1 AND m.ativo = 1
                    ORDER BY m.categoria, m.ordem, m.nome
                """, (user_id,))
                print("      👥 USER - Carregando menus por permissão")
            
            menus = cursor.fetchall()
            
            # Agrupar por categoria
            menus_por_categoria = {}
            for menu in menus:
                categoria = menu['categoria']
                if categoria not in menus_por_categoria:
                    menus_por_categoria[categoria] = []
                menus_por_categoria[categoria].append(menu['nome'])
            
            print(f"      📊 RESULTADO: {len(menus)} menus em {len(menus_por_categoria)} categorias")
            for cat, itens in menus_por_categoria.items():
                print(f"         📁 {cat}: {itens}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_completo()
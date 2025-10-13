#!/usr/bin/env python3
"""
Script para testar o sistema de menus filtrados por usuário
"""
import sqlite3
import os

def testar_filtro_menus():
    """Testa se o filtro de menus está funcionando"""
    db_path = 'financeiro.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acessar por nome da coluna
        cursor = conn.cursor()
        
        print("🧪 TESTANDO SISTEMA DE FILTRO DE MENUS\n")
        
        # Buscar todos os usuários
        cursor.execute('SELECT id, nome, perfil FROM usuarios ORDER BY id')
        usuarios = cursor.fetchall()
        
        for user in usuarios:
            user_id = user['id']
            user_name = user['nome']
            user_perfil = user['perfil']
            
            print(f"👤 USUÁRIO: {user_name} (ID: {user_id}, Perfil: {user_perfil})")
            
            if user_perfil == 'admin':
                # Admin vê todos os menus
                cursor.execute("""
                    SELECT nome, rota, categoria, ordem
                    FROM menus_sistema 
                    WHERE ativo = 1
                    ORDER BY categoria, ordem, nome
                """)
                print("   🔑 ADMIN - Deve ver TODOS os menus:")
            else:
                # Usuário comum vê apenas menus com permissão
                cursor.execute("""
                    SELECT m.nome, m.rota, m.categoria, m.ordem
                    FROM menus_sistema m
                    JOIN usuario_permissoes up ON m.id = up.menu_id
                    WHERE up.usuario_id = ? AND up.pode_acessar = 1 AND m.ativo = 1
                    ORDER BY m.categoria, m.ordem, m.nome
                """, (user_id,))
                print("   👥 USUÁRIO - Menus baseados em permissões:")
            
            menus = cursor.fetchall()
            
            # Agrupar por categoria
            menus_por_categoria = {}
            for menu in menus:
                categoria = menu['categoria']
                if categoria not in menus_por_categoria:
                    menus_por_categoria[categoria] = []
                menus_por_categoria[categoria].append(menu['nome'])
            
            if menus_por_categoria:
                for categoria, itens in menus_por_categoria.items():
                    print(f"      📁 {categoria.upper()}: {len(itens)} itens")
                    for item in itens:
                        print(f"         - {item}")
            else:
                print("      ❌ NENHUM MENU ENCONTRADO!")
            
            print()
        
        # Verificar se há problema nas permissões
        print("🔍 DIAGNÓSTICO DE PERMISSÕES:\n")
        
        cursor.execute('''
            SELECT u.nome, COUNT(up.menu_id) as total_permissoes
            FROM usuarios u
            LEFT JOIN usuario_permissoes up ON u.id = up.usuario_id AND up.pode_acessar = 1
            GROUP BY u.id, u.nome
        ''')
        
        diagnostico = cursor.fetchall()
        for diag in diagnostico:
            nome = diag['nome']
            total = diag['total_permissoes']
            print(f"   👤 {nome}: {total} permissões ativas")
        
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    testar_filtro_menus()
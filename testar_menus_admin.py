#!/usr/bin/env python3
"""
Script para testar os menus do usuário admin
"""
import sqlite3
import os

def testar_menus_admin():
    """Testa se os menus estão sendo carregados corretamente para o admin"""
    db_path = 'financeiro.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acessar por nome da coluna
        cursor = conn.cursor()
        
        # Encontrar o usuário admin
        cursor.execute('SELECT id, nome FROM usuarios WHERE perfil = "admin" LIMIT 1')
        admin = cursor.fetchone()
        
        if not admin:
            print("❌ Usuário admin não encontrado!")
            return
        
        admin_id = admin['id']
        print(f"✅ Admin encontrado: {admin['nome']} (ID: {admin_id})")
        
        # Simular a função get_user_menus
        cursor.execute("""
            SELECT nome, rota, icone, categoria, ordem
            FROM menus_sistema 
            WHERE ativo = 1
            ORDER BY categoria, ordem, nome
        """)
        
        menus = cursor.fetchall()
        
        if not menus:
            print("❌ Nenhum menu encontrado!")
            return
        
        # Agrupar por categoria
        menus_por_categoria = {}
        for menu in menus:
            categoria = menu['categoria']
            if categoria not in menus_por_categoria:
                menus_por_categoria[categoria] = []
            menus_por_categoria[categoria].append({
                'nome': menu['nome'],
                'rota': menu['rota'],
                'icone': menu['icone'],
                'ordem': menu['ordem']
            })
        
        print(f"\n📋 Estrutura de menus por categoria:")
        for categoria, itens in menus_por_categoria.items():
            print(f"\n🏷️ {categoria.upper()}:")
            for item in itens:
                print(f"  📄 {item['nome']} → {item['rota']} ({item['icone']})")
        
        print(f"\n✅ Total: {len(menus)} menus em {len(menus_por_categoria)} categorias")
        
        # Verificar sessão simulada
        print(f"\n🔧 Dados que seriam passados para o template:")
        print(f"user_menus = {menus_por_categoria}")
        
    except Exception as e:
        print(f"❌ Erro ao testar menus: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    testar_menus_admin()
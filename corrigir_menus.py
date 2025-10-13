#!/usr/bin/env python3
"""
Script para corrigir a estrutura de menus no banco de dados
para refletir exatamente o menu do sistema
"""
import sqlite3
import os

def corrigir_menus():
    """Corrige a estrutura de menus para bater com o menu real"""
    db_path = 'financeiro.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpar menus existentes
        cursor.execute('DELETE FROM usuario_permissoes')
        cursor.execute('DELETE FROM menus_sistema')
        
        # Menus exatamente como estão no template
        menus = [
            # === FINANCEIRO ===
            (1, 'Painel', '/planejamento', 'fas fa-chart-line', 'financeiro', 1, 1),
            (2, 'Planejamento FRZ', '/planejamento_frz', 'fas fa-chart-line', 'financeiro', 2, 1),
            (3, 'Projeção', '/projecao', 'fas fa-chart-area', 'financeiro', 3, 1),
            (4, 'Dashboard', '/dashboard', 'fas fa-tachometer-alt', 'financeiro', 4, 1),
            (5, 'Resumo', '/resumo', 'fas fa-file-alt', 'financeiro', 5, 1),
            (6, 'Consolidação', '/consolidacao', 'fas fa-compress-alt', 'financeiro', 6, 1),
            (7, 'Importação', '/importacao', 'fas fa-upload', 'financeiro', 7, 1),
            (8, 'FRZ LOG', '/frz_log', 'fas fa-truck', 'financeiro', 8, 1),
            
            # === FRETE ===
            (9, 'Painel Frete', '/painel_frete', 'fas fa-truck-loading', 'frete', 1, 1),
            (10, 'Análise de Margem', '/margem_analise', 'fas fa-percentage', 'frete', 2, 1),
            (11, 'Importação Frete', '/upload_sistema', 'fas fa-upload', 'frete', 3, 1),
            (12, 'Suporte', '/suporte', 'fas fa-wrench', 'frete', 4, 1),
            (13, 'Custo Frota', '/custo_frota', 'fas fa-calculator', 'frete', 5, 1),
            
            # === ARMAZEM ===
            (14, 'Armazem', '/armazem', 'fas fa-warehouse', 'armazem', 1, 1),
            
            # === LOGISTICA ===
            (15, 'Logistica', '/logistica', 'fas fa-route', 'logistica', 1, 1),
            (16, 'Monitoramento', '/logistica/monitoramento', 'fas fa-eye', 'logistica', 2, 1),
            
            # === ADMIN ===
            (17, 'Gestão de Usuários', '/admin/usuarios', 'fas fa-users-cog', 'admin', 1, 1),
        ]
        
        # Inserir menus
        cursor.executemany('''
            INSERT INTO menus_sistema (id, nome, rota, icone, categoria, ordem, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', menus)
        
        print(f"✅ {len(menus)} menus inseridos com sucesso!")
        
        # Dar todas as permissões para o admin
        cursor.execute('SELECT id FROM usuarios WHERE perfil = "admin" LIMIT 1')
        admin = cursor.fetchone()
        
        if admin:
            admin_id = admin[0]
            for menu_id, _, _, _, _, _, _ in menus:
                cursor.execute('''
                    INSERT INTO usuario_permissoes (usuario_id, menu_id, pode_acessar)
                    VALUES (?, ?, 1)
                ''', (admin_id, menu_id))
            print(f"✅ Permissões concedidas ao admin para todos os {len(menus)} menus!")
        
        conn.commit()
        print("🎉 Estrutura de menus corrigida com sucesso!")
        
        # Mostrar a estrutura final
        cursor.execute('''
            SELECT categoria, nome, rota, ordem
            FROM menus_sistema 
            WHERE ativo = 1 
            ORDER BY categoria, ordem
        ''')
        
        menus_result = cursor.fetchall()
        print(f"\n📋 Estrutura final ({len(menus_result)} menus):")
        categoria_atual = None
        for categoria, nome, rota, ordem in menus_result:
            if categoria != categoria_atual:
                print(f"\n🏷️ {categoria.upper()}:")
                categoria_atual = categoria
            print(f"  {ordem}. {nome} → {rota}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    corrigir_menus()
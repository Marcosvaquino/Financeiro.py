#!/usr/bin/env python3
"""
Script para corrigir o perfil do Junior Reis
"""
import sqlite3

def corrigir_perfil_junior():
    """Altera Junior Reis de admin para user"""
    try:
        conn = sqlite3.connect('financeiro.db')
        cursor = conn.cursor()
        
        # Alterar Junior Reis de admin para user
        cursor.execute('UPDATE usuarios SET perfil = "user" WHERE nome LIKE "%Junior%"')
        print('✅ Junior Reis alterado para perfil "user"')
        
        # Verificar a mudança
        cursor.execute('SELECT nome, perfil FROM usuarios')
        usuarios = cursor.fetchall()
        for nome, perfil in usuarios:
            print(f'   👤 {nome}: {perfil}')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_perfil_junior()
"""
Script para criar tabela de clientes e importar dados iniciais
"""

import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

# Dados dos clientes do print fornecido
clientes_dados = [
    ("Adoro Frango", "ADORO"),
    ("Adoro Varzea Paulista", "ADORO"),
    ("Adoro Vista Foods", "ADORO"),
    ("ALIBEM", "ALIBEM"),
    ("BRF ( SADIA )", "BRF"),
    ("COLETA SP", "COLETA SP"),
    ("Friboi", "FRIBOI"),
    ("COMPARTILHADO", "FRZ LOG"),
    ("ENTREGAS FROZEN", "FRZ LOG"),
    ("FRZ Log", "FRZ LOG"),
    ("GOLD PAO", "GOLD PAO"),
    ("GTFoods - Frangos Canção", "GT FOODS"),
    ("GTFoods", "GT FOODS"),
    ("GUAIRA", "GUAIRA"),
    ("Marfrig ( BRF )", "MARFRIG"),
    ("MEGGS", "MEGGS"),
    ("MINERVA", "MINERVA"),
    ("PERNOITE", "PERNOITE"),
    ("SAUDALI", "SAUDALI"),
    ("SAUDALI MG", "SAUDALI MG"),
    ("Transferência", "TRANSFERENCIA"),
    ("Valendo", "VALENDO")
]

def criar_tabela_clientes():
    """Cria a tabela de clientes se não existir"""
    try:
        conn = sqlite3.connect('financeiro.db')
        cursor = conn.cursor()
        
        # Criar tabela
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes_suporte (
                nome_real TEXT PRIMARY KEY,
                nome_ajustado TEXT NOT NULL,
                data_cadastro DATETIME NOT NULL,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        print("✅ Tabela clientes_suporte criada/verificada com sucesso!")
        
        # Verificar se já tem dados
        cursor.execute("SELECT COUNT(*) FROM clientes_suporte")
        total_existente = cursor.fetchone()[0]
        
        if total_existente > 0:
            print(f"📊 Tabela já possui {total_existente} clientes cadastrados")
            resposta = input("Deseja limpar e reimportar? (s/n): ").lower().strip()
            if resposta == 's':
                cursor.execute("DELETE FROM clientes_suporte")
                print("🗑️ Tabela limpa!")
            else:
                print("⏭️ Mantendo dados existentes")
                conn.close()
                return
        
        # Inserir dados dos clientes
        print("\n🔄 Importando clientes...")
        data_atual = datetime.now()
        
        for nome_real, nome_ajustado in clientes_dados:
            cursor.execute('''
                INSERT OR REPLACE INTO clientes_suporte 
                (nome_real, nome_ajustado, data_cadastro, ativo)
                VALUES (?, ?, ?, ?)
            ''', (nome_real, nome_ajustado, data_atual, True))
            print(f"  ✅ {nome_real} → {nome_ajustado}")
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM clientes_suporte")
        total_inserido = cursor.fetchone()[0]
        
        print(f"\n🎉 Importação concluída!")
        print(f"📊 Total de clientes cadastrados: {total_inserido}")
        
        # Mostrar resumo por nome ajustado
        cursor.execute('''
            SELECT nome_ajustado, COUNT(*) as qtd 
            FROM clientes_suporte 
            GROUP BY nome_ajustado 
            ORDER BY qtd DESC, nome_ajustado
        ''')
        
        print(f"\n📈 Distribuição por nome ajustado:")
        for nome_aj, qtd in cursor.fetchall():
            print(f"  {nome_aj}: {qtd} cliente(s)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        if 'conn' in locals():
            conn.close()

def verificar_dados():
    """Verifica os dados cadastrados"""
    try:
        conn = sqlite3.connect('financeiro.db')
        cursor = conn.cursor()
        
        print("\n🔍 VERIFICAÇÃO DOS DADOS CADASTRADOS:")
        print("="*60)
        
        cursor.execute('''
            SELECT nome_real, nome_ajustado, data_cadastro, ativo 
            FROM clientes_suporte 
            ORDER BY nome_real
        ''')
        
        clientes = cursor.fetchall()
        
        for cliente in clientes:
            nome_real, nome_ajustado, data_cadastro, ativo = cliente
            status = "✅ ATIVO" if ativo else "❌ INATIVO"
            data_fmt = data_cadastro[:19] if data_cadastro else ""
            print(f"{nome_real:<25} → {nome_ajustado:<15} | {data_fmt} | {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")

if __name__ == "__main__":
    print("🏢 CONFIGURAÇÃO DA TABELA DE CLIENTES")
    print("="*50)
    
    criar_tabela_clientes()
    verificar_dados()
    
    print(f"\n✨ Sistema de clientes pronto para uso!")
    print(f"📱 Acesse: http://127.0.0.1:5000/frete/suporte/clientes")
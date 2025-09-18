#!/usr/bin/env python3
"""Debug da página Painel"""

import os
import sys
sys.path.append('.')
sys.path.append('financeiro')

from financeiro.database import get_connection

def test_planejamento():
    print("🔍 TESTANDO FUNÇÃO PAINEL")
    print("=" * 50)
    
    try:
        # Testa conexão básica
        conn = get_connection()
        cur = conn.cursor()
        
        # Verifica tabelas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cur.fetchall()]
        print(f"📊 Tabelas encontradas: {tabelas}")
        
        # Verifica dados básicos
        cur.execute("SELECT COUNT(*) FROM contas_receber")
        total_receber = cur.fetchone()[0]
        print(f"📈 Total contas_receber: {total_receber}")
        
        cur.execute("SELECT COUNT(*) FROM contas_pagar")
        total_pagar = cur.fetchone()[0]
        print(f"📉 Total contas_pagar: {total_pagar}")
        
        # Testa query específica que pode estar dando erro
        mes = "09"  # setembro atual
        ano = "2025"
        
        print(f"\n🔍 Testando queries para {mes}/{ano}:")
        
        # Query 1: contas a receber
        clientes_filtro = ['MINERVA S A', 'ADORO']
        placeholders = ','.join(['?' for _ in clientes_filtro])
        query1 = f"""
            SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0) 
            FROM contas_receber 
            WHERE status = 'Recebido'
            AND vencimento LIKE ?
            AND cliente IN ({placeholders})
        """
        
        print(f"📋 Query 1: {query1}")
        cur.execute(query1, (f"%/{mes}/{ano}%",) + tuple(clientes_filtro))
        result1 = cur.fetchone()
        print(f"✅ Resultado 1: {result1}")
        
        # Query 2: contas a pagar
        query2 = """
            SELECT COUNT(*), COALESCE(SUM(CAST(valor_principal AS REAL)), 0.0) 
            FROM contas_pagar 
            WHERE status != 'Pago'
            AND strftime('%m', vencimento) = ? 
            AND strftime('%Y', vencimento) = ?
        """
        
        print(f"📋 Query 2: {query2}")
        cur.execute(query2, (mes, ano))
        result2 = cur.fetchone()
        print(f"✅ Resultado 2: {result2}")
        
        # Query 3: projeção
        query3 = """
            SELECT COALESCE(SUM(CAST(valor AS REAL)), 0.0), COUNT(*) 
            FROM projecao 
            WHERE mes = ? AND ano = ?
        """
        
        print(f"📋 Query 3: {query3}")
        cur.execute(query3, (int(mes), int(ano)))
        result3 = cur.fetchone()
        print(f"✅ Resultado 3: {result3}")
        
        conn.close()
        print("\n✅ Todos os testes passaram!")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_planejamento()
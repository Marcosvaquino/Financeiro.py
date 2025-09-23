#!/usr/bin/env python3
import sqlite3
import os

backup_path = os.path.join('backups', 'financeiro.db.20250917_084833')
print(f"🔍 Testando backup: {backup_path}")

if os.path.exists(backup_path):
    try:
        conn = sqlite3.connect(backup_path)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM contas_receber")
        count = cur.fetchone()[0]
        print(f"📊 Registros no backup: {count:,}")
        
        if count > 0:
            # Verificar MINERVA
            cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE cliente LIKE '%MINERVA%'")
            minerva = cur.fetchone()
            print(f"🔍 MINERVA no backup: {minerva[0]:,} registros - R$ {minerva[1] or 0:,.2f}")
            
            # Verificar status
            cur.execute("SELECT DISTINCT status, COUNT(*) FROM contas_receber GROUP BY status")
            status = cur.fetchall()
            print(f"📊 Status no backup: {dict(status)}")
            
        conn.close()
    except Exception as e:
        print(f"❌ ERRO: {e}")
else:
    print("❌ Backup não encontrado!")
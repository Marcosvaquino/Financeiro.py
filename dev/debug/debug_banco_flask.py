#!/usr/bin/env python3
"""
Script para verificar qual banco o Flask está usando na prática
"""
import sys
import os

# Adicionar financeiro ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'financeiro'))

from database import get_connection, DB_NAME
import sqlite3

print("🔍 VERIFICANDO CONFIGURAÇÃO DO BANCO NO FLASK")
print("=" * 60)

# Mostrar caminho configurado
print(f"📍 Caminho configurado no database.py: {DB_NAME}")
print(f"📁 Arquivo existe?: {'✅' if os.path.exists(DB_NAME) else '❌'}")

if os.path.exists(DB_NAME):
    print(f"📏 Tamanho do arquivo: {os.path.getsize(DB_NAME):,} bytes")

print("\n🔗 Testando conexão...")
try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar dados no banco que o Flask está usando
    cur.execute("SELECT COUNT(*) FROM contas_receber")
    total = cur.fetchone()[0]
    print(f"📊 Total registros contas_receber: {total:,}")
    
    if total > 0:
        # Verificar MINERVA especificamente
        cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE cliente LIKE '%MINERVA%'")
        minerva_count, minerva_valor = cur.fetchone()
        print(f"🔍 MINERVA: {minerva_count:,} registros - R$ {minerva_valor or 0:,.2f}")
        
        # Verificar status 'Recebido'
        cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE status = 'Recebido'")
        recebido_count, recebido_valor = cur.fetchone()
        print(f"✅ Status 'Recebido': {recebido_count:,} registros - R$ {recebido_valor or 0:,.2f}")
        
        # Verificar agosto/2025
        cur.execute("SELECT COUNT(*), SUM(valor_principal) FROM contas_receber WHERE vencimento LIKE '%/08/2025%'")
        agosto_count, agosto_valor = cur.fetchone()
        print(f"📅 Agosto/2025: {agosto_count:,} registros - R$ {agosto_valor or 0:,.2f}")
    
    conn.close()
    print("✅ Conexão testada com sucesso!")
    
except Exception as e:
    print(f"❌ Erro na conexão: {e}")

print("\n" + "=" * 60)
print("🔍 COMPARANDO COM OUTROS BANCOS EXISTENTES")
print("=" * 60)

# Verificar outros bancos
bancos_encontrados = []
for arquivo in ['financeiro.db', 'financeiro/financeiro.db']:
    if os.path.exists(arquivo):
        bancos_encontrados.append(arquivo)
        conn = sqlite3.connect(arquivo)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM contas_receber")
        count = cur.fetchone()[0]
        size = os.path.getsize(arquivo)
        print(f"📄 {arquivo}: {count:,} registros ({size:,} bytes)")
        conn.close()

print(f"\n📋 Bancos encontrados: {bancos_encontrados}")
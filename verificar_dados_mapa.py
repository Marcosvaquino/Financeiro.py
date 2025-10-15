import sqlite3
import pandas as pd

conn = sqlite3.connect(r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro\financeiro.db')
cursor = conn.cursor()

# Verificar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('📋 Tabelas:', [t[0] for t in cursor.fetchall()])

# Verificar se existe mapa_calor_uploads
cursor.execute("SELECT COUNT(*) FROM mapa_calor_uploads")
total = cursor.fetchone()[0]
print(f'\n📊 Total de uploads: {total}')

if total > 0:
    # Pegar último upload
    cursor.execute('''
        SELECT id, nome_arquivo, data_upload, total_locais 
        FROM mapa_calor_uploads 
        ORDER BY data_upload DESC 
        LIMIT 1
    ''')
    upload = cursor.fetchone()
    print(f'\n✅ Último upload:')
    print(f'   ID: {upload[0]}')
    print(f'   Arquivo: {upload[1]}')
    print(f'   Data: {upload[2]}')
    print(f'   Total de locais: {upload[3]}')
    
    # Pegar dados do upload
    cursor.execute('''
        SELECT cidade, latitude, longitude, valor
        FROM mapa_calor_dados
        WHERE upload_id = ?
        LIMIT 10
    ''', (upload[0],))
    
    print(f'\n📍 Primeiros 10 dados:')
    for row in cursor.fetchall():
        print(f'   {row[0]}: [{row[1]}, {row[2]}] - Valor: {row[3]}')

conn.close()

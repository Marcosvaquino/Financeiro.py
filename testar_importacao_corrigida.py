#!/usr/bin/env python3
"""
Script para testar importação com as correções
"""
import os
import sys

# Adicionar a pasta financeiro ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'financeiro'))

from importacao import salvar_contas_receber

# Verificar se existem arquivos CSV de contas a receber
uploads_dir = 'financeiro/uploads'
arquivos_csv = []

if os.path.exists(uploads_dir):
    for arquivo in os.listdir(uploads_dir):
        if 'receber' in arquivo.lower() and arquivo.endswith('.csv'):
            arquivos_csv.append(os.path.join(uploads_dir, arquivo))

print(f"📁 Arquivos encontrados: {arquivos_csv}")

if not arquivos_csv:
    print("❌ Nenhum arquivo de contas a receber encontrado!")
    print("💡 Verifique se você fez upload dos arquivos pelo sistema")
    exit(1)

# Pegar o arquivo mais recente
arquivo_mais_recente = max(arquivos_csv, key=os.path.getmtime)
print(f"🎯 Usando arquivo: {arquivo_mais_recente}")

try:
    print("=" * 60)
    print("🚀 INICIANDO IMPORTAÇÃO COM LOGS DETALHADOS")
    print("=" * 60)
    
    salvar_contas_receber(arquivo_mais_recente)
    
    print("=" * 60)
    print("✅ IMPORTAÇÃO CONCLUÍDA!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Erro na importação: {e}")
    import traceback
    traceback.print_exc()
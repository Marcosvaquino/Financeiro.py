#!/usr/bin/env python3
"""
Script para importar veículos em massa do CSV para o banco de dados
"""

import os
import sys
import pandas as pd
import sqlite3
from datetime import datetime

# Adiciona o diretório do projeto ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Importa o módulo de database do projeto
from financeiro.database import get_connection

def mapear_status(status_csv):
    """Mapeia o status do CSV para o formato do banco"""
    if status_csv == 'AGREGADO':
        return 'SPOT'  # AGREGADO vira SPOT
    elif status_csv == 'FIXO':
        return 'FIXO'
    else:
        return 'SPOT'  # fallback

def mapear_tipologia(tipologia_csv):
    """Mapeia a tipologia do CSV para o formato do banco"""
    mapeamento = {
        '-': '3/4',        # tipologia vazia vira 3/4
        '3/4': '3/4',
        'FIORINO': 'VUC',  # FIORINO vira VUC
        'TOCO': 'TOCO',
        'VAN': 'VUC',      # VAN vira VUC
        'VUC': 'VUC',
        'BITRUCK': 'TRUCK', # BITRUCK vira TRUCK
        'TRUCADO': 'TRUCK', # TRUCADO vira TRUCK
        'TRUCK': 'TRUCK'
    }
    return mapeamento.get(tipologia_csv, '3/4')  # fallback para 3/4

def importar_veiculos_csv(csv_path):
    """Importa veículos do CSV para o banco de dados"""
    
    print(f"🚚 Iniciando importação de veículos do arquivo: {csv_path}")
    
    # Lê o CSV
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        print(f"📊 Arquivo carregado: {len(df)} registros encontrados")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return False
    
    # Remove linhas vazias
    df = df.dropna(subset=['PLACA'])
    print(f"📋 Após limpeza: {len(df)} registros válidos")
    
    # Conecta ao banco
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Cria a tabela se não existir
        cur.execute('''
            CREATE TABLE IF NOT EXISTS veiculos_suporte (
                placa TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                tipologia TEXT NOT NULL,
                data_cadastro TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Verifica quantos já existem
        cur.execute("SELECT COUNT(*) FROM veiculos_suporte")
        antes = cur.fetchone()[0]
        print(f"📊 Veículos no banco antes: {antes}")
        
        # Processa cada linha
        inseridos = 0
        atualizados = 0
        erros = 0
        
        for idx, row in df.iterrows():
            placa = str(row['PLACA']).strip().upper()
            status_original = str(row['STATUS']).strip()
            tipologia_original = str(row['TIPOLOGIA']).strip()
            
            # Mapeia os valores
            status = mapear_status(status_original)
            tipologia = mapear_tipologia(tipologia_original)
            
            try:
                # Tenta inserir primeiro
                cur.execute('''
                    INSERT OR REPLACE INTO veiculos_suporte 
                    (placa, status, tipologia, data_cadastro, ativo)
                    VALUES (?, ?, ?, ?, ?)
                ''', (placa, status, tipologia, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), True))
                
                if cur.rowcount > 0:
                    inseridos += 1
                    if inseridos % 50 == 0:
                        print(f"📥 Processados: {inseridos} registros...")
                
            except Exception as e:
                erros += 1
                print(f"⚠️ Erro ao inserir {placa}: {e}")
        
        # Commit das mudanças
        conn.commit()
        
        # Verifica quantos ficaram
        cur.execute("SELECT COUNT(*) FROM veiculos_suporte")
        depois = cur.fetchone()[0]
        
        conn.close()
        
        print(f"\n✅ Importação concluída!")
        print(f"📊 Registros no banco depois: {depois}")
        print(f"➕ Registros inseridos: {inseridos}")
        print(f"❌ Erros: {erros}")
        
        # Mostra alguns exemplos de mapeamento
        print(f"\n📋 Exemplos de mapeamento aplicado:")
        print(f"   AGREGADO → SPOT")
        print(f"   FIORINO → VUC")
        print(f"   VAN → VUC")
        print(f"   BITRUCK → TRUCK")
        print(f"   TRUCADO → TRUCK")
        print(f"   - (vazio) → 3/4")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

if __name__ == "__main__":
    # Caminho para o CSV fornecido
    csv_path = r"d:\placas cadastro.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        print("Certifique-se de que o arquivo está no local correto.")
        sys.exit(1)
    
    # Executa a importação
    sucesso = importar_veiculos_csv(csv_path)
    
    if sucesso:
        print(f"\n🎉 Importação concluída com sucesso!")
        print(f"Agora você pode acessar a página de veículos para ver todos os registros.")
    else:
        print(f"\n💥 Importação falhou!")
        sys.exit(1)
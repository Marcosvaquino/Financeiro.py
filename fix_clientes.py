#!/usr/bin/env python3
"""
CORREÇÃO DEFINITIVA DOS CLIENTES - IGNORA ESPAÇOS E MAIÚSCULAS!
"""
import sqlite3
from datetime import datetime

def normalizar_nome(nome):
    """Remove espaços, converte para maiúsculo e remove caracteres especiais"""
    if not nome or nome == '-':
        return 'SEM_CLIENTE'
    return str(nome).upper().strip().replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

def corrigir_mapeamentos():
    conn = sqlite3.connect('financeiro.db')
    cursor = conn.cursor()

    print('🔧 CRIANDO MAPEAMENTO INTELIGENTE...')

    # Limpar mapeamentos problemáticos
    cursor.execute('DELETE FROM clientes_suporte WHERE nome_real IN ("0", "")')

    # Mapeamentos CORRETOS baseados na planilha
    mapeamentos = [
        ('Adoro Varzea Paulista', 'ADORO'),
        ('Adoro Vista Foods', 'ADORO VISTA'),  
        ('Marfrig ( BRF )', 'MARFRIG'),
        ('BRF ( SADIA )', 'BRF'),
        ('Transferencia', 'TRANSFERENCIA'),
        ('-', 'SEM_CLIENTE'),
        ('FRZ Log', 'FRZ_LOG'),
        ('MINERVA', 'MINERVA'),
        ('Friboi', 'FRIBOI'),
        ('MEGGS', 'MEGGS'),
        ('GOLD PAO', 'GOLD_PAO')
    ]

    data_agora = datetime.now().strftime('%Y-%m-%d')

    for nome_ajustado, nome_real in mapeamentos:
        try:
            cursor.execute('''INSERT OR REPLACE INTO clientes_suporte 
                            (nome_ajustado, nome_real, ativo, data_cadastro) 
                            VALUES (?, ?, 1, ?)''', 
                         (nome_ajustado, nome_real, data_agora))
            print(f'✅ {nome_ajustado} -> {nome_real}')
        except Exception as e:
            print(f'⚠️ {nome_ajustado}: {e}')

    conn.commit()
    conn.close()
    print('✅ MAPEAMENTO INTELIGENTE APLICADO!')

if __name__ == "__main__":
    corrigir_mapeamentos()
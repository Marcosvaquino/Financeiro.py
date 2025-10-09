import sqlite3
from pathlib import Path

def get_db_path():
    return 'financeiro.db'

def get_veiculo_info(placa):
    """Busca informações completas do veículo no banco de dados local"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Buscar tipologia e perfil (status) da placa na tabela veiculos_suporte
        cursor.execute('''
            SELECT tipologia, status FROM veiculos_suporte 
            WHERE placa = ? AND ativo = 1
        ''', (placa,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        print(f"DEBUG: Placa '{placa}' -> Resultado: {resultado}")
        
        if resultado:
            return {
                'tipologia': resultado[0],
                'perfil': resultado[1]
            }
        else:
            return {
                'tipologia': None,
                'perfil': None
            }
            
    except Exception as e:
        print(f"❌ Erro ao buscar informações da placa {placa}: {e}")
        return {
            'tipologia': None,
            'perfil': None
        }

# Teste
placa_teste = 'EFT3I02'
resultado = get_veiculo_info(placa_teste)
print(f"Resultado: {resultado}")
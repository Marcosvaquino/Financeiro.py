import sqlite3
import sys, os
import unicodedata
import re
root = r'D:\OneDrive\PROJETOFINANCEIRO.PY'
sys.path.insert(0, root)

from financeiro.database import get_connection

def normalizar_nome(nome):
    """Normaliza nome removendo acentos, espaços extras e caracteres especiais"""
    if not nome:
        return ""
    
    # Converter para string e upper
    nome = str(nome).upper().strip()
    
    # Remover acentos
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(c for c in nome if unicodedata.category(c) != 'Mn')
    
    # Remover caracteres especiais exceto espaços
    nome = re.sub(r'[^A-Z0-9\s]', '', nome)
    
    # Normalizar espaços múltiplos
    nome = re.sub(r'\s+', ' ', nome).strip()
    
    return nome

# Ver que clientes estão no banco
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT nome_real, nome_ajustado FROM clientes_suporte WHERE ativo = 1 ORDER BY nome_real")
clientes_banco = cursor.fetchall()

print(f"CLIENTES NO BANCO ({len(clientes_banco)} total):")
for nome_real, nome_ajustado in clientes_banco:
    print(f"  Real: '{nome_real}' -> Ajustado: '{nome_ajustado}'")

print("\nCLIENTES DO MANIFESTO:")
clientes_manifesto = ['ADORO VARZEA PAULISTA', 'MINERVA', 'GOLD PAO', 'MARFRIG ( BRF )', 'TRANSFERENCIA', 'SEARA ( JBS )', 'POLISHOP', 'SOSSEGAO ADORO', 'BRASIL FOODS JBS']

# Criar mapeamento melhorado
mapeamento = {}
for cliente_manifesto in clientes_manifesto:
    cliente_norm = normalizar_nome(cliente_manifesto)
    print(f"  Manifesto: '{cliente_manifesto}' -> Normalizado: '{cliente_norm}'")
    
    # Buscar matches mais flexíveis
    melhor_match = None
    melhor_score = 0
    
    for nome_real, nome_ajustado in clientes_banco:
        banco_norm = normalizar_nome(nome_ajustado)
        
        # Match exato
        if cliente_norm == banco_norm:
            melhor_match = (nome_real, nome_ajustado)
            melhor_score = 100
            break
        
        # Match parcial por palavras
        palavras_manifesto = set(cliente_norm.split())
        palavras_banco = set(banco_norm.split())
        
        if palavras_manifesto and palavras_banco:
            intersecao = len(palavras_manifesto.intersection(palavras_banco))
            uniao = len(palavras_manifesto.union(palavras_banco))
            score = (intersecao / uniao) * 100
            
            if score > melhor_score and score >= 50:  # Pelo menos 50% de similaridade
                melhor_match = (nome_real, nome_ajustado)
                melhor_score = score
    
    if melhor_match:
        print(f"    MATCH ({melhor_score:.1f}%): {melhor_match}")
        mapeamento[cliente_manifesto.upper().strip()] = melhor_match[0]
    else:
        print(f"    NAO ENCONTRADO")
        mapeamento[cliente_manifesto.upper().strip()] = '0'

print(f"\nMAPEAMENTO FINAL:")
for orig, mapeado in mapeamento.items():
    print(f"'{orig}' -> '{mapeado}'")

conn.close()
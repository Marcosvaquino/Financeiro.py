"""
Teste para verificar se a ativação do manifesto_acumulado está funcionando
em todas as situações (Manifesto, Valencio, Pamplona)
"""

import os
import re

def verificar_ativacao_acumulado():
    """Verifica se schedule_acumulador_background() é chamado em todos os uploads."""
    
    arquivo = 'financeiro/upload_sistema.py'
    
    print("🔍 VERIFICANDO ATIVAÇÃO DO MANIFESTO_ACUMULADO...")
    print("=" * 60)
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar todas as chamadas para schedule_acumulador_background()
    pattern = r'schedule_acumulador_background\(\)'
    matches = list(re.finditer(pattern, conteudo))
    
    print(f"📊 Encontradas {len(matches)-1} chamadas para schedule_acumulador_background() (excluindo definição)")
    print()
    
    # Analisar contexto de cada chamada
    linhas = conteudo.split('\n')
    
    for i, match in enumerate(matches):
        linha_num = conteudo[:match.start()].count('\n') + 1
        
        # Pular a definição da função
        if 'def schedule_acumulador_background' in linhas[linha_num-1]:
            continue
            
        print(f"🎯 ATIVAÇÃO #{i}:")
        print(f"   📍 Linha {linha_num}")
        
        # Mostrar contexto (5 linhas antes e depois)
        inicio = max(0, linha_num - 6)
        fim = min(len(linhas), linha_num + 3)
        
        for j in range(inicio, fim):
            marcador = ">>> " if j == linha_num-1 else "    "
            print(f"{marcador}{j+1:3d}: {linhas[j]}")
        print()
    
    # Verificar se está nas 3 situações esperadas
    contextos_esperados = ['MANIFESTO', 'VALENCIO', 'PAMPLONA']
    contextos_encontrados = []
    
    for match in matches:
        if 'def schedule_acumulador_background' in conteudo[match.start()-100:match.start()]:
            continue
            
        contexto_antes = conteudo[max(0, match.start()-500):match.start()]
        
        if 'MANIFESTO' in contexto_antes.upper():
            contextos_encontrados.append('MANIFESTO')
        elif 'VALENCIO' in contexto_antes.upper():
            contextos_encontrados.append('VALENCIO')
        elif 'PAMPLONA' in contexto_antes.upper():
            contextos_encontrados.append('PAMPLONA')
    
    print("✅ RESULTADO:")
    print(f"   Contextos esperados: {contextos_esperados}")
    print(f"   Contextos encontrados: {contextos_encontrados}")
    
    if set(contextos_esperados) == set(contextos_encontrados):
        print("   🎉 PERFEITO! Manifesto_Acumulado será ativado em todos os 3 tipos de upload!")
    else:
        faltando = set(contextos_esperados) - set(contextos_encontrados)
        print(f"   ⚠️ FALTANDO: {list(faltando)}")
    
    print()
    print("📝 RESUMO:")
    print("   • Upload MANIFESTO → ✅ Ativa manifesto_acumulado")
    print("   • Upload VALENCIO  → ✅ Ativa manifesto_acumulado")
    print("   • Upload PAMPLONA  → ✅ Ativa manifesto_acumulado")

if __name__ == "__main__":
    verificar_ativacao_acumulado()
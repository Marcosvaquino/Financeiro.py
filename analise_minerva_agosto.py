import csv
import re

# Lê o arquivo CSV e busca MINERVA S A com vencimento em agosto e status Recebido
arquivo_csv = 'uploads/lancamentos-a-receber_16-09-2025_13-53.csv'

total_valor = 0
contador = 0
registros = []

print("=== ANÁLISE MINERVA S A - AGOSTO 2025 - STATUS RECEBIDO ===\n")

with open(arquivo_csv, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)  # Pula o cabeçalho
    
    for linha in reader:
        if len(linha) >= 23:  # Garante que tem todas as colunas
            cliente = linha[3].strip()
            vencimento = linha[8].strip() 
            valor_principal = linha[11].strip()
            status = linha[21].strip()
            
            # Verifica se é MINERVA S A com vencimento em agosto e status Recebido
            if ("MINERVA S A" in cliente and 
                "/08/" in vencimento and 
                "2025" in vencimento and 
                status == "Recebido"):
                
                # Converte valor brasileiro para float
                valor_limpo = valor_principal.replace('.', '').replace(',', '.')
                try:
                    valor = float(valor_limpo)
                    total_valor += valor
                    contador += 1
                    
                    registros.append({
                        'cliente': cliente,
                        'vencimento': vencimento,
                        'valor': valor,
                        'status': status,
                        'sequencia': linha[4] if len(linha) > 4 else ''
                    })
                    
                except ValueError:
                    print(f"Erro ao converter valor: {valor_principal}")

# Mostra os resultados
print(f"Total de registros encontrados: {contador}")
print(f"Valor total: R$ {total_valor:,.2f}")
print(f"Valor médio por registro: R$ {total_valor/contador if contador > 0 else 0:,.2f}")

print("\n=== PRIMEIROS 10 REGISTROS ===")
for i, reg in enumerate(registros[:10]):
    print(f"{i+1:2d}. {reg['sequencia']} - {reg['vencimento']} - R$ {reg['valor']:8.2f}")

print(f"\n... e mais {len(registros)-10} registros" if len(registros) > 10 else "")

print(f"\n=== VERIFICAÇÃO: {contador} registros vs 213 esperados ===")
if contador == 213:
    print("✓ CONTAGEM CONFERE!")
else:
    print(f"✗ DIVERGÊNCIA: Encontrados {contador}, esperados 213")
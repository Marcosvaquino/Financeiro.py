"""
Exemplo de integração completa: Manifesto + Veículos + Clientes
Demonstra como enriquecer manifestos com dados completos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financeiro.veiculo_helper import VeiculoHelper
from financeiro.cliente_helper import ClienteHelper

def processar_manifesto_completo(dados_manifesto):
    """
    Processa um manifesto completo enriquecendo com dados de veículos e clientes
    
    Args:
        dados_manifesto: Lista de dicts com dados do manifesto
        Exemplo: [
            {"id": 1, "placa": "ABC1234", "cliente": "ADORO", "destino": "SP", "peso": 1500},
            {"id": 2, "placa": "DEF5678", "cliente": "MINERVA", "destino": "RJ", "peso": 2000}
        ]
    
    Returns:
        Lista enriquecida com dados de veículos e clientes
    """
    
    if not dados_manifesto:
        return []
    
    print("🚛 PROCESSAMENTO COMPLETO DO MANIFESTO")
    print("=" * 60)
    
    # 1. Extrair placas e clientes únicos
    placas = list(set([item.get('placa', '') for item in dados_manifesto if item.get('placa')]))
    clientes = list(set([item.get('cliente', '') for item in dados_manifesto if item.get('cliente')]))
    
    print(f"📊 ANÁLISE INICIAL:")
    print(f"  • Total de registros no manifesto: {len(dados_manifesto)}")
    print(f"  • Placas únicas: {len(placas)}")
    print(f"  • Clientes únicos: {len(clientes)}")
    
    # 2. Buscar dados dos veículos
    print(f"\n🚚 BUSCANDO DADOS DOS VEÍCULOS...")
    dados_veiculos = VeiculoHelper.buscar_multiplas_placas(placas)
    veiculos_encontrados = sum(1 for v in dados_veiculos.values() if v.get('encontrado', False))
    print(f"  ✅ Veículos encontrados: {veiculos_encontrados}/{len(placas)}")
    
    # 3. Buscar dados dos clientes
    print(f"\n👥 BUSCANDO DADOS DOS CLIENTES...")
    dados_clientes = ClienteHelper.buscar_multiplos_nomes_ajustados(clientes)
    clientes_encontrados = sum(1 for c in dados_clientes.values() if c.get('encontrado', False))
    print(f"  ✅ Clientes encontrados: {clientes_encontrados}/{len(clientes)}")
    
    # 4. Enriquecer dados do manifesto
    print(f"\n🔄 ENRIQUECENDO DADOS DO MANIFESTO...")
    manifesto_enriquecido = []
    
    for item in dados_manifesto:
        item_enriquecido = item.copy()
        
        # Dados do veículo
        placa = item.get('placa', '').upper().strip()
        if placa and placa in dados_veiculos:
            veiculo = dados_veiculos[placa]
            item_enriquecido.update({
                'veiculo_status': veiculo.get('status'),
                'veiculo_tipologia': veiculo.get('tipologia'),
                'veiculo_encontrado': veiculo.get('encontrado', False)
            })
        else:
            item_enriquecido.update({
                'veiculo_status': None,
                'veiculo_tipologia': None,
                'veiculo_encontrado': False
            })
        
        # Dados do cliente
        cliente = item.get('cliente', '').upper().strip()
        if cliente and cliente in dados_clientes:
            cliente_dados = dados_clientes[cliente]
            item_enriquecido.update({
                'cliente_nome_real': cliente_dados.get('nome_real'),
                'cliente_encontrado': cliente_dados.get('encontrado', False)
            })
        else:
            item_enriquecido.update({
                'cliente_nome_real': None,
                'cliente_encontrado': False
            })
        
        manifesto_enriquecido.append(item_enriquecido)
    
    # 5. Gerar relatório detalhado
    print(f"\n📋 RELATÓRIO DETALHADO:")
    print("-" * 60)
    
    for item in manifesto_enriquecido:
        id_registro = item.get('id', 'N/A')
        placa = item.get('placa', 'N/A')
        cliente = item.get('cliente', 'N/A')
        
        # Status dos dados
        veiculo_status = "✅" if item.get('veiculo_encontrado') else "❌"
        cliente_status = "✅" if item.get('cliente_encontrado') else "❌"
        
        # Informações enriquecidas
        v_status = item.get('veiculo_status') or 'N/A'
        v_tipo = item.get('veiculo_tipologia') or 'N/A'
        c_nome = item.get('cliente_nome_real') or 'N/A'
        
        print(f"ID {id_registro:<3} | {veiculo_status} {placa:<8} ({v_status:<4}/{v_tipo:<4}) | {cliente_status} {cliente:<12} ({c_nome})")
    
    # 6. Estatísticas e insights
    print(f"\n📈 ESTATÍSTICAS E INSIGHTS:")
    print("-" * 60)
    
    total_registros = len(manifesto_enriquecido)
    registros_completos = sum(1 for item in manifesto_enriquecido 
                             if item.get('veiculo_encontrado') and item.get('cliente_encontrado'))
    
    veiculos_fixo = sum(1 for item in manifesto_enriquecido 
                       if item.get('veiculo_status') == 'FIXO')
    veiculos_spot = sum(1 for item in manifesto_enriquecido 
                       if item.get('veiculo_status') == 'SPOT')
    
    print(f"📊 Completude dos dados:")
    print(f"  • Registros com dados completos: {registros_completos}/{total_registros} ({registros_completos/total_registros*100:.1f}%)")
    print(f"  • Veículos encontrados: {veiculos_encontrados}/{len(placas)} ({veiculos_encontrados/len(placas)*100:.1f}%)")
    print(f"  • Clientes encontrados: {clientes_encontrados}/{len(clientes)} ({clientes_encontrados/len(clientes)*100:.1f}%)")
    
    print(f"\n🚛 Análise da frota:")
    print(f"  • Veículos FIXO: {veiculos_fixo}")
    print(f"  • Veículos SPOT: {veiculos_spot}")
    print(f"  • Não identificados: {total_registros - veiculos_fixo - veiculos_spot}")
    
    # Agrupamento por cliente
    clientes_agrupados = {}
    for item in manifesto_enriquecido:
        cliente = item.get('cliente', 'DESCONHECIDO')
        if cliente not in clientes_agrupados:
            clientes_agrupados[cliente] = 0
        clientes_agrupados[cliente] += 1
    
    print(f"\n👥 Top 5 clientes no manifesto:")
    top_clientes = sorted(clientes_agrupados.items(), key=lambda x: x[1], reverse=True)[:5]
    for cliente, qtd in top_clientes:
        status_cliente = "✅" if dados_clientes.get(cliente, {}).get('encontrado', False) else "❌"
        print(f"  {status_cliente} {cliente}: {qtd} registros")
    
    return manifesto_enriquecido

def calcular_custos_manifesto_completo(manifesto_enriquecido, distancia_media_km=150):
    """
    Calcula custos estimados baseado nos dados enriquecidos
    """
    print(f"\n💰 CÁLCULO DE CUSTOS (Distância média: {distancia_media_km}km)")
    print("=" * 60)
    
    # Custos por km
    custo_fixo_km = 2.50
    custo_spot_km = 3.20
    custo_desconhecido_km = 3.50  # Maior custo para veículos não identificados
    
    veiculos_fixo = 0
    veiculos_spot = 0
    veiculos_desconhecidos = 0
    
    for item in manifesto_enriquecido:
        if item.get('veiculo_encontrado'):
            if item.get('veiculo_status') == 'FIXO':
                veiculos_fixo += 1
            elif item.get('veiculo_status') == 'SPOT':
                veiculos_spot += 1
        else:
            veiculos_desconhecidos += 1
    
    custo_fixo_total = veiculos_fixo * custo_fixo_km * distancia_media_km
    custo_spot_total = veiculos_spot * custo_spot_km * distancia_media_km
    custo_desconhecido_total = veiculos_desconhecidos * custo_desconhecido_km * distancia_media_km
    custo_total = custo_fixo_total + custo_spot_total + custo_desconhecido_total
    
    print(f"🚛 Breakdown de custos:")
    print(f"  • FIXO: {veiculos_fixo} veículos x R${custo_fixo_km}/km = R${custo_fixo_total:.2f}")
    print(f"  • SPOT: {veiculos_spot} veículos x R${custo_spot_km}/km = R${custo_spot_total:.2f}")
    print(f"  • DESCONHECIDOS: {veiculos_desconhecidos} veículos x R${custo_desconhecido_km}/km = R${custo_desconhecido_total:.2f}")
    print(f"  🎯 CUSTO TOTAL ESTIMADO: R${custo_total:.2f}")
    
    # Economia potencial
    economia_se_todos_fixo = (veiculos_spot * (custo_spot_km - custo_fixo_km) + 
                             veiculos_desconhecidos * (custo_desconhecido_km - custo_fixo_km)) * distancia_media_km
    
    if economia_se_todos_fixo > 0:
        print(f"  💡 Economia se todos fossem FIXO: R${economia_se_todos_fixo:.2f}")
    
    return {
        'custo_total': custo_total,
        'custo_fixo': custo_fixo_total,
        'custo_spot': custo_spot_total,
        'custo_desconhecido': custo_desconhecido_total,
        'economia_potencial': economia_se_todos_fixo
    }

def exemplo_manifesto_real():
    """Simula um manifesto real com dados variados"""
    
    # Dados de exemplo que simulam um manifesto real
    manifesto_exemplo = [
        {"id": 1, "placa": "AXR4A69", "cliente": "ADORO", "destino": "São Paulo", "peso": 1500},
        {"id": 2, "placa": "CDL3807", "cliente": "MINERVA", "destino": "Rio de Janeiro", "peso": 2000},
        {"id": 3, "placa": "CFY3C64", "cliente": "FRZ LOG", "destino": "Belo Horizonte", "peso": 1200},
        {"id": 4, "placa": "NOVA123", "cliente": "CLIENTE_NOVO", "destino": "Salvador", "peso": 1800},
        {"id": 5, "placa": "CPI4J76", "cliente": "GT FOODS", "destino": "Brasília", "peso": 1600},
        {"id": 6, "placa": "TEST456", "cliente": "ADORO", "destino": "Fortaleza", "peso": 1400},
        {"id": 7, "placa": "DFU0477", "cliente": "BRF", "destino": "Recife", "peso": 1700}
    ]
    
    print("🚛 EXEMPLO DE PROCESSAMENTO COMPLETO")
    print("=" * 80)
    
    # Processar manifesto
    resultado = processar_manifesto_completo(manifesto_exemplo)
    
    # Calcular custos
    custos = calcular_custos_manifesto_completo(resultado, 180)  # 180km de média
    
    print(f"\n✨ RESUMO EXECUTIVO:")
    print(f"  📊 {len(resultado)} registros processados")
    print(f"  💰 Custo total estimado: R${custos['custo_total']:.2f}")
    print(f"  💡 Economia potencial: R${custos['economia_potencial']:.2f}")
    
    return resultado

if __name__ == "__main__":
    exemplo_manifesto_real()
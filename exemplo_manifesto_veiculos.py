"""
Exemplo de integração do sistema de veículos com manifesto
Mostra como enriquecer dados do manifesto com informações dos veículos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financeiro.veiculo_helper import (
    VeiculoHelper, 
    get_veiculo_status, 
    get_veiculo_tipologia,
    enriquecer_manifesto_com_veiculos
)

def processar_manifesto_com_veiculos(placas_do_manifesto):
    """
    Exemplo de como processar um manifesto enriquecendo com dados dos veículos
    
    Args:
        placas_do_manifesto (list): Lista de placas vindas do manifesto
    """
    print("🚛 PROCESSANDO MANIFESTO COM DADOS DE VEÍCULOS")
    print("=" * 60)
    
    # 1. Enriquecer dados do manifesto
    dados_enriquecidos = enriquecer_manifesto_com_veiculos(placas_do_manifesto)
    
    print(f"📊 RESUMO:")
    print(f"  • Total de placas no manifesto: {len(placas_do_manifesto)}")
    print(f"  • Veículos encontrados no sistema: {dados_enriquecidos['veiculos_encontrados']}")
    print(f"  • Veículos NÃO encontrados: {dados_enriquecidos['veiculos_nao_encontrados']}")
    print(f"  • Status FIXO: {dados_enriquecidos['status_fixo']}")
    print(f"  • Status SPOT: {dados_enriquecidos['status_spot']}")
    
    print(f"\n📋 DETALHAMENTO POR PLACA:")
    print("-" * 60)
    
    for placa, dados in dados_enriquecidos['dados'].items():
        if dados['encontrado']:
            print(f"✅ {placa:<10} | {dados['status']:<4} | {dados['tipologia']:<6} | Cadastrado em {dados['data_cadastro'][:10]}")
        else:
            print(f"❌ {placa:<10} | ----  | ------  | NÃO ENCONTRADO NO SISTEMA")
    
    print("\n" + "=" * 60)
    
    # 2. Sugestões de ação baseadas nos dados
    print("💡 SUGESTÕES DE AÇÃO:")
    
    if dados_enriquecidos['veiculos_nao_encontrados'] > 0:
        print(f"⚠️  {dados_enriquecidos['veiculos_nao_encontrados']} veículos do manifesto não estão cadastrados no sistema")
        print("   → Considere cadastrar estes veículos ou verificar se as placas estão corretas")
    
    if dados_enriquecidos['status_fixo'] > 0:
        print(f"🟢 {dados_enriquecidos['status_fixo']} veículos com status FIXO (operação própria)")
        print("   → Estes veículos têm custos e planejamento diferentes")
    
    if dados_enriquecidos['status_spot'] > 0:
        print(f"🟡 {dados_enriquecidos['status_spot']} veículos com status SPOT (terceirizado)")
        print("   → Estes veículos podem ter variação de custos")
    
    return dados_enriquecidos

def exemplo_uso_simples():
    """Exemplo de uso das funções mais simples"""
    print("\n🔍 EXEMPLOS DE USO SIMPLES:")
    print("=" * 40)
    
    # Exemplo 1: Verificar status de um veículo
    placa_teste = "AXR4A69"
    status = get_veiculo_status(placa_teste)
    tipologia = get_veiculo_tipologia(placa_teste)
    
    print(f"Placa {placa_teste}:")
    print(f"  Status: {status}")
    print(f"  Tipologia: {tipologia}")
    
    # Exemplo 2: Como usar em validações
    placas_para_validar = ["AXR4A69", "CDL3807", "INEXISTENTE123"]
    
    print(f"\nValidação de placas:")
    for placa in placas_para_validar:
        status = get_veiculo_status(placa)
        if status:
            print(f"  ✅ {placa}: {status}")
        else:
            print(f"  ❌ {placa}: Não encontrado")

def simulacao_manifesto_real():
    """Simula o processamento de um manifesto real"""
    print("\n" + "="*80)
    print("🚚 SIMULAÇÃO: PROCESSAMENTO DE MANIFESTO REAL")
    print("="*80)
    
    # Simular placas vindas de um manifesto (mix de existentes e não existentes)
    placas_manifesto = [
        "AXR4A69",   # Existe - SPOT 3/4
        "CDL3807",   # Existe - SPOT 3/4  
        "CFY3C64",   # Existe - SPOT 3/4
        "NOVA123",   # Não existe
        "TEST456",   # Não existe
        "CPI4J76",   # Existe - SPOT 3/4
        "DFU0477",   # Existe - SPOT 3/4
    ]
    
    # Processar manifesto
    resultado = processar_manifesto_com_veiculos(placas_manifesto)
    
    # Exemplo de como usar os dados para lógica de negócio
    print("\n💰 EXEMPLO DE APLICAÇÃO - CÁLCULO DE CUSTOS:")
    print("-" * 50)
    
    custo_fixo_por_km = 2.50   # Veículos próprios
    custo_spot_por_km = 3.20   # Veículos terceirizados
    distancia_km = 150         # Exemplo: 150km de viagem
    
    custo_total_fixo = resultado['status_fixo'] * custo_fixo_por_km * distancia_km
    custo_total_spot = resultado['status_spot'] * custo_spot_por_km * distancia_km
    custo_total = custo_total_fixo + custo_total_spot
    
    print(f"Distância da viagem: {distancia_km}km")
    print(f"Veículos FIXO: {resultado['status_fixo']} x R${custo_fixo_por_km}/km = R${custo_total_fixo:.2f}")
    print(f"Veículos SPOT: {resultado['status_spot']} x R${custo_spot_por_km}/km = R${custo_total_spot:.2f}")
    print(f"CUSTO TOTAL ESTIMADO: R${custo_total:.2f}")
    
    economia_se_todos_fixo = resultado['status_spot'] * (custo_spot_por_km - custo_fixo_por_km) * distancia_km
    if economia_se_todos_fixo > 0:
        print(f"💡 Economia se todos fossem FIXO: R${economia_se_todos_fixo:.2f}")

if __name__ == "__main__":
    # Executar exemplos
    exemplo_uso_simples()
    simulacao_manifesto_real()
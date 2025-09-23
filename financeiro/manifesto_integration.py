"""
Integração pronta para usar no sistema de manifesto.
Funções prontas para enriquecer manifestos com dados de veículos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financeiro.veiculo_helper import VeiculoHelper, get_veiculo_status, get_veiculo_tipologia

def processar_manifesto(manifestos_data):
    """
    Função principal para enriquecer dados do manifesto com informações de veículos
    
    Args:
        manifestos_data: Pode ser:
            - Lista de placas: ["ABC1234", "DEF5678"]
            - Lista de dicts: [{"placa": "ABC1234", "outros_dados": "..."}, ...]
            - DataFrame pandas com coluna 'placa'
    
    Returns:
        Lista enriquecida com dados dos veículos
    """
    
    # Extrair placas dos dados de entrada
    placas = extrair_placas(manifestos_data)
    
    if not placas:
        return manifestos_data
    
    # Buscar dados dos veículos
    dados_veiculos = VeiculoHelper.buscar_multiplas_placas(placas)
    
    # Enriquecer dados originais
    resultado = enriquecer_dados_originais(manifestos_data, dados_veiculos)
    
    return resultado

def extrair_placas(data):
    """Extrai placas de diferentes formatos de entrada"""
    placas = []
    
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                # Lista simples de placas
                placas.append(item)
            elif isinstance(item, dict) and 'placa' in item:
                # Lista de dicionários com chave 'placa'
                placas.append(item['placa'])
    
    # Se for pandas DataFrame
    elif hasattr(data, 'columns') and 'placa' in data.columns:
        placas = data['placa'].tolist()
    
    return [str(p).upper().strip() for p in placas if p]

def enriquecer_dados_originais(dados_originais, dados_veiculos):
    """Enriquece os dados originais com informações dos veículos"""
    
    if isinstance(dados_originais, list):
        if not dados_originais:
            return []
            
        # Lista de strings (placas)
        if isinstance(dados_originais[0], str):
            resultado = []
            for placa in dados_originais:
                placa_normalizada = str(placa).upper().strip()
                veiculo_info = dados_veiculos.get(placa_normalizada, {})
                
                item_enriquecido = {
                    'placa': placa,
                    'placa_normalizada': placa_normalizada,
                    'veiculo_status': veiculo_info.get('status'),
                    'veiculo_tipologia': veiculo_info.get('tipologia'),
                    'veiculo_ativo': veiculo_info.get('ativo', False),
                    'veiculo_encontrado': veiculo_info.get('encontrado', False),
                    'veiculo_data_cadastro': veiculo_info.get('data_cadastro')
                }
                resultado.append(item_enriquecido)
            return resultado
        
        # Lista de dicionários
        elif isinstance(dados_originais[0], dict):
            resultado = []
            for item in dados_originais:
                item_enriquecido = item.copy()
                placa = str(item.get('placa', '')).upper().strip()
                
                if placa:
                    veiculo_info = dados_veiculos.get(placa, {})
                    item_enriquecido.update({
                        'veiculo_status': veiculo_info.get('status'),
                        'veiculo_tipologia': veiculo_info.get('tipologia'),
                        'veiculo_ativo': veiculo_info.get('ativo', False),
                        'veiculo_encontrado': veiculo_info.get('encontrado', False),
                        'veiculo_data_cadastro': veiculo_info.get('data_cadastro')
                    })
                
                resultado.append(item_enriquecido)
            return resultado
    
    # Se for pandas DataFrame
    elif hasattr(dados_originais, 'columns'):
        df_resultado = dados_originais.copy()
        
        # Adicionar colunas de veículo
        df_resultado['veiculo_status'] = None
        df_resultado['veiculo_tipologia'] = None
        df_resultado['veiculo_ativo'] = False
        df_resultado['veiculo_encontrado'] = False
        df_resultado['veiculo_data_cadastro'] = None
        
        for index, row in df_resultado.iterrows():
            placa = str(row.get('placa', '')).upper().strip()
            if placa in dados_veiculos:
                veiculo_info = dados_veiculos[placa]
                df_resultado.at[index, 'veiculo_status'] = veiculo_info.get('status')
                df_resultado.at[index, 'veiculo_tipologia'] = veiculo_info.get('tipologia')
                df_resultado.at[index, 'veiculo_ativo'] = veiculo_info.get('ativo', False)
                df_resultado.at[index, 'veiculo_encontrado'] = veiculo_info.get('encontrado', False)
                df_resultado.at[index, 'veiculo_data_cadastro'] = veiculo_info.get('data_cadastro')
        
        return df_resultado
    
    return dados_originais

def gerar_relatorio_manifesto_veiculos(dados_enriquecidos):
    """Gera relatório resumido do manifesto enriquecido"""
    
    if not dados_enriquecidos:
        return {"erro": "Nenhum dado fornecido"}
    
    # Contar estatísticas
    total_itens = len(dados_enriquecidos)
    veiculos_encontrados = 0
    status_fixo = 0
    status_spot = 0
    
    tipologias = {}
    veiculos_nao_encontrados = []
    
    for item in dados_enriquecidos:
        if isinstance(item, dict):
            encontrado = item.get('veiculo_encontrado', False)
            if encontrado:
                veiculos_encontrados += 1
                status = item.get('veiculo_status', '')
                tipologia = item.get('veiculo_tipologia', '')
                
                if status == 'FIXO':
                    status_fixo += 1
                elif status == 'SPOT':
                    status_spot += 1
                
                if tipologia:
                    tipologias[tipologia] = tipologias.get(tipologia, 0) + 1
            else:
                placa = item.get('placa', item.get('placa_normalizada', 'Desconhecida'))
                veiculos_nao_encontrados.append(placa)
    
    relatorio = {
        'resumo': {
            'total_registros': total_itens,
            'veiculos_encontrados': veiculos_encontrados,
            'veiculos_nao_encontrados': len(veiculos_nao_encontrados),
            'percentual_encontrado': round((veiculos_encontrados / total_itens * 100), 2) if total_itens > 0 else 0
        },
        'status': {
            'fixo': status_fixo,
            'spot': status_spot
        },
        'tipologias': tipologias,
        'veiculos_nao_encontrados': veiculos_nao_encontrados,
        'alertas': []
    }
    
    # Gerar alertas
    if len(veiculos_nao_encontrados) > 0:
        relatorio['alertas'].append(f"⚠️ {len(veiculos_nao_encontrados)} veículos não encontrados no sistema")
    
    if veiculos_encontrados > 0:
        percentual_spot = round((status_spot / veiculos_encontrados * 100), 2)
        if percentual_spot > 70:
            relatorio['alertas'].append(f"📊 Alto percentual de veículos SPOT ({percentual_spot}%)")
    
    return relatorio

# Funções de conveniência específicas para manifesto
def validar_placas_manifesto(placas):
    """Valida se todas as placas do manifesto existem no sistema"""
    dados_veiculos = VeiculoHelper.buscar_multiplas_placas(placas)
    
    placas_validas = []
    placas_invalidas = []
    
    for placa in placas:
        placa_norm = str(placa).upper().strip()
        if dados_veiculos.get(placa_norm, {}).get('encontrado', False):
            placas_validas.append(placa)
        else:
            placas_invalidas.append(placa)
    
    return {
        'validas': placas_validas,
        'invalidas': placas_invalidas,
        'total': len(placas),
        'percentual_valido': round((len(placas_validas) / len(placas) * 100), 2) if placas else 0
    }

def calcular_custos_manifesto(dados_enriquecidos, distancia_km, custo_fixo_km=2.50, custo_spot_km=3.20):
    """Calcula custos estimados do manifesto baseado nos tipos de veículo"""
    
    veiculos_fixo = 0
    veiculos_spot = 0
    
    for item in dados_enriquecidos:
        if isinstance(item, dict) and item.get('veiculo_encontrado', False):
            status = item.get('veiculo_status', '')
            if status == 'FIXO':
                veiculos_fixo += 1
            elif status == 'SPOT':
                veiculos_spot += 1
    
    custo_fixo_total = veiculos_fixo * custo_fixo_km * distancia_km
    custo_spot_total = veiculos_spot * custo_spot_km * distancia_km
    custo_total = custo_fixo_total + custo_spot_total
    
    return {
        'distancia_km': distancia_km,
        'veiculos_fixo': veiculos_fixo,
        'veiculos_spot': veiculos_spot,
        'custo_fixo_total': round(custo_fixo_total, 2),
        'custo_spot_total': round(custo_spot_total, 2),
        'custo_total': round(custo_total, 2),
        'economia_se_todos_fixo': round(veiculos_spot * (custo_spot_km - custo_fixo_km) * distancia_km, 2)
    }

if __name__ == "__main__":
    print("🚛 TESTE DA INTEGRAÇÃO MANIFESTO + VEÍCULOS")
    print("="*60)
    
    # Teste 1: Lista simples de placas
    print("\n1️⃣ Teste com lista de placas:")
    placas_teste = ["AXR4A69", "CDL3807", "INEXISTENTE"]
    resultado1 = processar_manifesto(placas_teste)
    
    for item in resultado1:
        status = "✅" if item['veiculo_encontrado'] else "❌"
        print(f"  {status} {item['placa']}: {item['veiculo_status']} | {item['veiculo_tipologia']}")
    
    # Teste 2: Lista de dicionários (simulando dados de manifesto real)
    print("\n2️⃣ Teste com dados de manifesto:")
    manifesto_teste = [
        {"id": 1, "placa": "AXR4A69", "destino": "São Paulo", "peso": 1500},
        {"id": 2, "placa": "CDL3807", "destino": "Rio de Janeiro", "peso": 2000},
        {"id": 3, "placa": "NOVA123", "destino": "Belo Horizonte", "peso": 1200}
    ]
    
    resultado2 = processar_manifesto(manifesto_teste)
    
    for item in resultado2:
        status = "✅" if item['veiculo_encontrado'] else "❌"
        print(f"  {status} ID {item['id']}: {item['placa']} → {item['destino']} | Status: {item['veiculo_status']}")
    
    # Teste 3: Relatório
    print("\n3️⃣ Relatório do manifesto:")
    relatorio = gerar_relatorio_manifesto_veiculos(resultado2)
    print(f"  Total: {relatorio['resumo']['total_registros']}")
    print(f"  Encontrados: {relatorio['resumo']['veiculos_encontrados']} ({relatorio['resumo']['percentual_encontrado']}%)")
    print(f"  Status FIXO: {relatorio['status']['fixo']}")
    print(f"  Status SPOT: {relatorio['status']['spot']}")
    
    for alerta in relatorio['alertas']:
        print(f"  {alerta}")
    
    # Teste 4: Cálculo de custos
    print("\n4️⃣ Cálculo de custos (150km):")
    custos = calcular_custos_manifesto(resultado2, 150)
    print(f"  Veículos FIXO: {custos['veiculos_fixo']} = R$ {custos['custo_fixo_total']}")
    print(f"  Veículos SPOT: {custos['veiculos_spot']} = R$ {custos['custo_spot_total']}")
    print(f"  TOTAL: R$ {custos['custo_total']}")
    if custos['economia_se_todos_fixo'] > 0:
        print(f"  💰 Economia potencial: R$ {custos['economia_se_todos_fixo']}")
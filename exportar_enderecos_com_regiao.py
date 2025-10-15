"""
Script para exportar o arquivo 'endereço clientes.xlsx' com coluna de Macro-Região
Baseado no sistema de classificação do Mapa de Calor
"""
import pandas as pd
import os
from datetime import datetime

# Caminho do arquivo original
ARQUIVO_ORIGINAL = r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro\uploads\endereço clientes.xlsx'

# Dicionário de coordenadas das cidades (baseado no sistema do mapa de calor)
COORDENADAS_CIDADES = {
    # Vale do Paraíba
    'SÃO JOSÉ DOS CAMPOS': [-23.2237, -45.9009],
    'TAUBATÉ': [-23.0205, -45.5555],
    'JACAREÍ': [-23.2995, -45.9658],
    'PINDAMONHANGABA': [-22.9244, -45.4618],
    'GUARATINGUETÁ': [-22.8161, -45.1931],
    'APARECIDA': [-22.8458, -45.2306],
    'LORENA': [-22.7309, -45.1173],
    'CAÇAPAVA': [-23.1058, -45.7058],
    'CRUZEIRO': [-22.5767, -44.9606],
    'CUNHA': [-23.0747, -44.9597],
    'CAMPOS DO JORDÃO': [-22.7399, -45.5917],
    'SANTA BRANCA': [-23.3977, -45.8863],
    'SILVEIRAS': [-22.7997, -44.8705],
    'LAGOINHA': [-23.1158, -45.1758],
    'MONTEIRO LOBATO': [-22.9579, -45.8376],
    'POTIM': [-22.8358, -45.2458],
    'QUELUZ': [-22.5328, -44.7758],
    'ROSEIRA': [-22.9044, -45.3008],
    'TREMEMBÉ': [-22.9558, -45.5458],
    'REDENÇÃO DA SERRA': [-23.2658, -45.5458],
    'SÃO LUIZ DO PARAITINGA': [-23.2258, -45.3158],
    'NATIVIDADE DA SERRA': [-23.5358, -45.4558],
    'PARAIBUNA': [-23.3858, -45.6658],
    
    # Litoral Norte
    'CARAGUATATUBA': [-23.6204, -45.4130],
    'SÃO SEBASTIÃO': [-23.8129, -45.4044],
    'UBATUBA': [-23.4336, -45.0838],
    
    # Litoral Sul
    'SANTOS': [-23.9618, -46.3322],
    'GUARUJÁ': [-24.0139, -46.2564],
    'CUBATÃO': [-23.8950, -46.4253],
    'SÃO VICENTE': [-23.9633, -46.3922],
    'PERUÍBE': [-24.3200, -46.9978],
    'BERTIOGA': [-23.8543, -46.1376],
    'MONGAGUÁ': [-24.0889, -46.6119],
    'ITANHAÉM': [-24.1833, -46.7889],
    
    # SP Capital e RM
    'SÃO PAULO': [-23.5505, -46.6333],
    'GUARULHOS': [-23.4538, -46.5333],
    'MOGI DAS CRUZES': [-23.5228, -46.1883],
    'ARUJÁ': [-23.3964, -46.3200],
    'ITAQUAQUECETUBA': [-23.4864, -46.3489],
    'FRANCO DA ROCHA': [-23.3289, -46.7272],
    'SANTA ISABEL': [-23.3158, -46.2208],
    'MAIRIPORÃ': [-23.3189, -46.5872],
    'SUZANO': [-23.5426, -46.3116],
    
    # ABC Paulista
    'SANTO ANDRÉ': [-23.6633, -46.5333],
    'SÃO BERNARDO DO CAMPO': [-23.6914, -46.5646],
    'DIADEMA': [-23.6861, -46.6208],
    'MAUÁ': [-23.6700, -46.4611],
    'OSASCO': [-23.5329, -46.7918],
    'SÃO CAETANO DO SUL': [-23.6228, -46.5547],
    'RIBEIRÃO PIRES': [-23.7133, -46.4133],
    
    # Campinas e Região
    'CAMPINAS': [-22.9056, -47.0608],
    'AMERICANA': [-22.7394, -47.3311],
    'INDAIATUBA': [-23.0920, -47.2181],
    'HORTOLÂNDIA': [-22.8583, -47.2200],
    'SUMARÉ': [-22.8219, -47.2669],
    'VINHEDO': [-23.0297, -46.9753],
    'JUNDIAÍ': [-23.1864, -46.8842],
    'ATIBAIA': [-23.1169, -46.5533],
    'BRAGANÇA PAULISTA': [-22.9519, -46.5425],
    'VÁRZEA PAULISTA': [-23.2114, -46.8294],
    'LOUVEIRA': [-23.0847, -46.9486],
    'VALINHOS': [-22.9706, -46.9956],
    'ITATIBA': [-23.0058, -46.8386],
    
    # Sorocaba e Região
    'SOROCABA': [-23.5015, -47.4526],
    
    # Interior SP
    'RIBEIRÃO PRETO': [-21.1775, -47.8208],
    'FRANCA': [-20.5386, -47.4008],
    'SÃO JOÃO DA BOA VISTA': [-21.9697, -46.7972],
    'ITUVERAVA': [-20.3397, -47.7797],
    'MOCOCA': [-21.4672, -47.0050],
    'SÃO JOAQUIM DA BARRA': [-20.5825, -47.8586],
    
    # Outras cidades SP
    'PIRACICABA': [-22.7253, -47.6492],
    'BARUERI': [-23.5106, -46.8767],
    'TABOÃO DA SERRA': [-23.6088, -46.7575],
    'ITAPECERICA DA SERRA': [-23.7172, -46.8489],
    'SOCORRO': [-22.5919, -46.5297],
    'SÃO BENTO DO SAPUCAÍ': [-22.6859, -45.7253],
    'VARGEM': [-22.8858, -46.4058],
    'EMBU DAS ARTES': [-23.6489, -46.8522],
    'COTIA': [-23.6039, -46.9189],
    'CARAPICUÍBA': [-23.5225, -46.8356],
    'FERRAZ DE VASCONCELOS': [-23.5411, -46.3689],
    'POÁ': [-23.5281, -46.3450],
    'JUQUITIBA': [-23.9294, -47.0647],
    'EMBU-GUAÇU': [-23.8328, -46.8111],
    
    # Outras Capitais
    'RIO DE JANEIRO': [-22.9068, -43.1729],
    'BELO HORIZONTE': [-19.9167, -43.9345],
    'BRASÍLIA': [-15.7942, -47.8822],
    'SALVADOR': [-12.9714, -38.5014],
    'FORTALEZA': [-3.7319, -38.5267],
    'RECIFE': [-8.0476, -34.8770],
    'PORTO ALEGRE': [-30.0346, -51.2177],
    'CURITIBA': [-25.4244, -49.2654],
    'GUARATUBA': [-25.8833, -48.5761],
}

def classificar_macro_regiao(cidade, lat, lng):
    """
    Classifica uma cidade em uma macro-região baseado em suas coordenadas
    Mesma lógica do mapa_calor.html
    """
    if not lat or not lng:
        return 'Não Classificada'
    
    cidade_upper = str(cidade).upper().strip()
    
    # Outras Capitais (fora de SP)
    outras_capitais = ['RIO DE JANEIRO', 'BELO HORIZONTE', 'BRASÍLIA', 'SALVADOR', 
                       'FORTALEZA', 'RECIFE', 'PORTO ALEGRE', 'CURITIBA', 'GUARATUBA']
    if cidade_upper in outras_capitais:
        return 'Outras Capitais'
    
    # Vale do Paraíba
    if lat >= -23.4 and lat <= -22.5 and lng >= -46.0 and lng <= -44.7:
        return 'Vale do Paraíba'
    
    # Litoral Norte
    if lat < -23.3 and lng >= -46.0 and lng <= -44.7:
        return 'Litoral Norte'
    
    # Litoral Sul
    if lat < -23.8 and lng > -47.0:
        return 'Litoral Sul'
    
    # ABC Paulista
    if lat >= -23.8 and lat <= -23.5 and lng >= -46.8 and lng <= -46.3:
        return 'ABC Paulista'
    
    # SP Capital e Região Metropolitana
    if lat >= -23.8 and lat <= -23.1 and lng >= -46.9 and lng <= -46.0:
        return 'SP Capital e Região Metropolitana'
    
    # Campinas e Região
    if lat >= -23.3 and lat <= -22.5 and lng >= -47.5 and lng <= -46.3:
        return 'Campinas e Região'
    
    # Sorocaba e Região
    if lat >= -23.8 and lat <= -23.3 and lng >= -47.8 and lng <= -47.2:
        return 'Sorocaba e Região'
    
    # Interior SP
    if lat >= -25.0 and lat <= -19.0 and lng >= -52.0 and lng <= -44.0:
        return 'Interior SP'
    
    # Outras Regiões (fora de SP)
    return 'Outras Regiões'

def normalizar_nome_cidade(cidade):
    """Normaliza o nome da cidade para match com o dicionário"""
    if not cidade or pd.isna(cidade):
        return None
    
    cidade = str(cidade).strip().upper()
    
    # Correções específicas
    correcoes = {
        'SAO PAULO': 'SÃO PAULO',
        'SAO JOSE DOS CAMPOS': 'SÃO JOSÉ DOS CAMPOS',
        'SAO BERNARDO DO CAMPO': 'SÃO BERNARDO DO CAMPO',
        'SAO CAETANO DO SUL': 'SÃO CAETANO DO SUL',
        'SAO VICENTE': 'SÃO VICENTE',
        'SAO SEBASTIAO': 'SÃO SEBASTIÃO',
        'RIBEIRAO PRETO': 'RIBEIRÃO PRETO',
        'RIBEIRAO PIRES': 'RIBEIRÃO PIRES',
        'GUARATINGUETA': 'GUARATINGUETÁ',
        'HORTOLANDIA': 'HORTOLÂNDIA',
        'SUMARE': 'SUMARÉ',
        'MONGAGUA': 'MONGAGUÁ',
        'ITANHAEM': 'ITANHAÉM',
        'BRASILIA': 'BRASÍLIA',
        'VARZEA PAULISTA': 'VÁRZEA PAULISTA',
        'MAIRIPRA': 'MAIRIPORÃ',
        'CARAPICUIBA': 'CARAPICUÍBA',
        'EMBU-GUACU': 'EMBU-GUAÇU',
        'SAO BENTO DO SAPUCAI': 'SÃO BENTO DO SAPUCAÍ',
        'SAO LUIZ DO PARAITINGA': 'SÃO LUIZ DO PARAITINGA',
        'SAO JOAO DA BOA VISTA': 'SÃO JOÃO DA BOA VISTA',
        'SAO JOAQUIM DA BARRA': 'SÃO JOAQUIM DA BARRA',
        'REDENCAO DA SERRA': 'REDENÇÃO DA SERRA',
        'TREMEBE': 'TREMEMBÉ',
        'CACAPAVA': 'CAÇAPAVA',
    }
    
    for errado, correto in correcoes.items():
        if cidade == errado:
            return correto
    
    return cidade

def processar_arquivo():
    """
    Processa o arquivo de endereços e adiciona coluna de Macro-Região
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(ARQUIVO_ORIGINAL):
            print(f"❌ Arquivo não encontrado: {ARQUIVO_ORIGINAL}")
            return None
        
        print(f"📂 Lendo arquivo: {os.path.basename(ARQUIVO_ORIGINAL)}")
        
        # Ler o arquivo Excel
        df = pd.read_excel(ARQUIVO_ORIGINAL)
        
        print(f"✅ Arquivo lido com sucesso!")
        print(f"📊 Total de linhas: {len(df)}")
        print(f"📋 Colunas: {df.columns.tolist()}")
        
        # Adicionar colunas novas
        df['Latitude'] = None
        df['Longitude'] = None
        df['Macro_Regiao'] = None
        
        # Processar cada linha
        cidades_classificadas = 0
        cidades_nao_encontradas = set()
        
        print(f"\n🔄 Processando {len(df)} registros...")
        
        for idx, row in df.iterrows():
            cidade = normalizar_nome_cidade(row['Cidade'])
            
            if cidade and cidade in COORDENADAS_CIDADES:
                lat, lng = COORDENADAS_CIDADES[cidade]
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lng
                
                # Classificar macro-região
                macro_regiao = classificar_macro_regiao(cidade, lat, lng)
                df.at[idx, 'Macro_Regiao'] = macro_regiao
                
                cidades_classificadas += 1
            else:
                if cidade:
                    cidades_nao_encontradas.add(cidade)
                df.at[idx, 'Macro_Regiao'] = 'Não Classificada'
            
            # Mostrar progresso a cada 500 registros
            if (idx + 1) % 500 == 0:
                print(f"   Processados: {idx + 1}/{len(df)} ({((idx + 1)/len(df)*100):.1f}%)")
        
        print(f"\n✅ Processamento concluído!")
        print(f"   ✓ {cidades_classificadas} cidades classificadas")
        print(f"   ⚠️ {len(cidades_nao_encontradas)} cidades não encontradas no dicionário")
        
        if cidades_nao_encontradas and len(cidades_nao_encontradas) <= 20:
            print(f"\n📍 Cidades não encontradas:")
            for cidade in sorted(cidades_nao_encontradas):
                print(f"   - {cidade}")
        
        # Estatísticas por região
        print(f"\n📊 Estatísticas por Macro-Região:")
        regioes_count = df['Macro_Regiao'].value_counts()
        for regiao, count in regioes_count.items():
            percentual = (count / len(df)) * 100
            print(f"   {regiao}: {count} clientes ({percentual:.1f}%)")
        
        # Salvar arquivo exportado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'endereço_clientes_COM_REGIOES_{timestamp}.xlsx'
        output_path = os.path.join(
            r'Z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro\uploads',
            output_file
        )
        
        print(f"\n💾 Salvando arquivo exportado...")
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        print(f"\n🎉 SUCESSO! Arquivo exportado:")
        print(f"📁 {output_path}")
        print(f"\n✨ O arquivo agora contém as colunas adicionais:")
        print(f"   ✓ Latitude")
        print(f"   ✓ Longitude")
        print(f"   ✓ Macro_Regiao")
        print(f"\n💡 Total de colunas: {len(df.columns)}")
        print(f"   Colunas: {df.columns.tolist()}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("=" * 70)
    print("🗺️  EXPORTADOR DE ENDEREÇOS COM MACRO-REGIÕES")
    print("=" * 70)
    print()
    
    arquivo_exportado = processar_arquivo()
    
    if arquivo_exportado:
        print("\n" + "=" * 70)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print(f"\n📋 Arquivo disponível em:")
        print(f"   {arquivo_exportado}")
        print(f"\n🎯 Use este arquivo para análises por região!")
    else:
        print("\n" + "=" * 70)
        print("❌ PROCESSO FINALIZADO COM ERROS")
        print("=" * 70)

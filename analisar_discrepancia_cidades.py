import requests

try:
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados', timeout=5)
    data = response.json()
    
    if data.get('data'):
        # Filtrar apenas tipologia 3/4
        dados_filtrados = [item for item in data['data'] if item.get('Tipologia') == '3/4']
        
        print(f"📊 Total de registros com tipologia 3/4: {len(dados_filtrados)}")
        
        # Análise do CARD (cidades únicas)
        cidades_todas = [item.get('Cidade', '').strip() for item in dados_filtrados if item.get('Cidade', '').strip()]
        cidades_unicas = list(set(cidades_todas))
        
        print(f"\n🏙️ CARD - Total de cidades únicas: {len(cidades_unicas)}")
        
        # Coordenadas definidas no sistema (copiadas do código)
        coordenadas_cidades = {
            'SÃO PAULO', 'TAUBATÉ', 'RIO DE JANEIRO', 'BELO HORIZONTE', 'BRASÍLIA', 
            'SALVADOR', 'FORTALEZA', 'RECIFE', 'PORTO ALEGRE', 'CURITIBA', 
            'CAMPINAS', 'SANTOS', 'SÃO JOSÉ DOS CAMPOS', 'SOROCABA', 'RIBEIRÃO PRETO',
            'SÃO BERNARDO DO CAMPO', 'GUARULHOS', 'OSASCO', 'SÃO CAETANO DO SUL',
            'DIADEMA', 'MAUÁ', 'SUZANO', 'JACAREÍ', 'CAÇAPAVA', 'SÃO SEBASTIÃO',
            'CARAGUATATUBA', 'UBATUBA', 'GUARATINGUETÁ', 'APARECIDA', 'LORENA',
            'CACHOEIRA PAULISTA', 'CRUZEIRO', 'QUELUZ', 'LAVRINHAS', 'SÃO LUIZ DO PARAITINGA'
        }
        
        # Verificar quais cidades têm coordenadas
        cidades_com_coordenadas = []
        cidades_sem_coordenadas = []
        
        for cidade in cidades_unicas:
            cidade_upper = cidade.upper().strip()
            if cidade_upper in coordenadas_cidades:
                cidades_com_coordenadas.append(cidade)
            else:
                cidades_sem_coordenadas.append(cidade)
        
        print(f"🗺️ MAPA - Cidades com coordenadas: {len(cidades_com_coordenadas)}")
        print(f"❌ Cidades SEM coordenadas: {len(cidades_sem_coordenadas)}")
        
        print(f"\n✅ Cidades que aparecem no MAPA:")
        for cidade in sorted(cidades_com_coordenadas):
            count = cidades_todas.count(cidade)
            print(f"  • {cidade}: {count} registros")
        
        print(f"\n❌ Cidades que NÃO aparecem no MAPA (só no card):")
        for cidade in sorted(cidades_sem_coordenadas):
            count = cidades_todas.count(cidade)
            print(f"  • {cidade}: {count} registros")
        
        print(f"\n🔍 EXPLICAÇÃO DA DISCREPÂNCIA:")
        print(f"  - Card conta TODAS as cidades únicas: {len(cidades_unicas)}")
        print(f"  - Mapa só mostra cidades com coordenadas: {len(cidades_com_coordenadas)}")
        print(f"  - Diferença: {len(cidades_sem_coordenadas)} cidades sem coordenadas definidas")
        
except Exception as e:
    print(f"Erro: {e}")
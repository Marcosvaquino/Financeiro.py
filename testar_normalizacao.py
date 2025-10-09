import requests

try:
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados', timeout=5)
    data = response.json()
    
    if data.get('data'):
        # Filtrar apenas tipologia 3/4
        dados_filtrados = [item for item in data['data'] if item.get('Tipologia') == '3/4']
        
        print(f"📊 Total de registros com tipologia 3/4: {len(dados_filtrados)}")
        
        # Simular normalização (mesma lógica do JavaScript)
        def normalizar_nome_cidade(cidade):
            if not cidade or cidade.strip() == '':
                return ''
            
            correcoes = {
                'SÃ£o': 'São',
                'SÃ¡o': 'São', 
                'TaubatÃ©': 'Taubaté',
                'CaÃ§apava': 'Caçapava',
                'SÃ£o JosÃ© dos Campos': 'São José dos Campos',
                'SÃ£o Paulo': 'São Paulo',
                'SÃ£o Sebastiao': 'São Sebastião',
                'SÃ£o Joao da Boa Vista': 'São João da Boa Vista',
                'SÃ£o Joaquim da Barra': 'São Joaquim da Barra'
            }
            
            cidade_normalizada = cidade.strip()
            
            # Aplicar correções de encoding
            for errado, correto in correcoes.items():
                cidade_normalizada = cidade_normalizada.replace(errado, correto)
            
            # Capitalização padronizada
            preposicoes = ['de', 'da', 'das', 'do', 'dos', 'e']
            palavras = cidade_normalizada.lower().split(' ')
            palavras_capitalizadas = []
            
            for palavra in palavras:
                if palavra in preposicoes:
                    palavras_capitalizadas.append(palavra)
                else:
                    palavras_capitalizadas.append(palavra.capitalize())
            
            return ' '.join(palavras_capitalizadas)
        
        # Aplicar normalização
        cidades_antes = [item.get('Cidade', '').strip() for item in dados_filtrados if item.get('Cidade', '').strip()]
        cidades_normalizadas = [normalizar_nome_cidade(cidade) for cidade in cidades_antes if cidade]
        
        cidades_unicas_antes = set(cidades_antes)
        cidades_unicas_depois = set(cidades_normalizadas)
        
        print(f"\n🏙️ ANTES da normalização: {len(cidades_unicas_antes)} cidades únicas")
        print(f"🏙️ DEPOIS da normalização: {len(cidades_unicas_depois)} cidades únicas")
        print(f"✅ Redução: {len(cidades_unicas_antes) - len(cidades_unicas_depois)} duplicatas eliminadas")
        
        print(f"\n📋 Cidades normalizadas (ordenadas):")
        for i, cidade in enumerate(sorted(cidades_unicas_depois), 1):
            count = cidades_normalizadas.count(cidade)
            print(f"  {i:2d}. {cidade}: {count} registros")
        
        # Verificar quantas têm coordenadas agora
        coordenadas_cidades = {
            'SÃO PAULO', 'TAUBATÉ', 'RIO DE JANEIRO', 'BELO HORIZONTE', 'BRASÍLIA', 
            'SALVADOR', 'FORTALEZA', 'RECIFE', 'PORTO ALEGRE', 'CURITIBA', 
            'CAMPINAS', 'SANTOS', 'SÃO JOSÉ DOS CAMPOS', 'SOROCABA', 'RIBEIRÃO PRETO',
            'SÃO BERNARDO DO CAMPO', 'GUARULHOS', 'OSASCO', 'SÃO CAETANO DO SUL',
            'DIADEMA', 'MAUÁ', 'SUZANO', 'JACAREÍ', 'CAÇAPAVA', 'SÃO SEBASTIÃO',
            'CARAGUATATUBA', 'UBATUBA', 'GUARATINGUETÁ', 'APARECIDA', 'LORENA',
            'CACHOEIRA PAULISTA', 'CRUZEIRO', 'QUELUZ', 'LAVRINHAS', 'SÃO LUIZ DO PARAITINGA',
            'AGUAI', 'CANAS', 'FRANCA', 'GUARÁ', 'ITAQUAQUECETUBA', 'ITUVERAVA',
            'LAGOINHA', 'PINDAMONHANGABA', 'PERUÍBE', 'PIQUETE', 'ROSEIRA',
            'SANTA ISABEL', 'SANTO ANTÔNIO DE POSSE', 'SOCORRO', 
            'SÃO JOÃO DA BOA VISTA', 'SÃO JOAQUIM DA BARRA', 'VARGEM'
        }
        
        cidades_com_coordenadas = 0
        cidades_sem_coordenadas = []
        
        for cidade in cidades_unicas_depois:
            cidade_upper = cidade.upper()
            if cidade_upper in coordenadas_cidades:
                cidades_com_coordenadas += 1
            else:
                cidades_sem_coordenadas.append(cidade)
        
        print(f"\n🗺️ Cidades com coordenadas: {cidades_com_coordenadas}")
        print(f"❌ Cidades ainda sem coordenadas: {len(cidades_sem_coordenadas)}")
        
        if cidades_sem_coordenadas:
            print("\nCidades que ainda precisam de coordenadas:")
            for cidade in sorted(cidades_sem_coordenadas):
                count = cidades_normalizadas.count(cidade)
                print(f"  • {cidade}: {count} registros")
        
except Exception as e:
    print(f"Erro: {e}")
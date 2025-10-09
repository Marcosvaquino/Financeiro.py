import requests

try:
    # Buscar dados com filtro 3/4
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados?tipologia=3/4', timeout=5)
    data = response.json()
    
    if data.get('data'):
        dados_filtrados = data['data']
        
        print(f"📊 Total de registros com tipologia 3/4: {len(dados_filtrados)}")
        
        # Função de normalização igual ao frontend
        def normalizar_nome_cidade(cidade):
            if not cidade or cidade.strip() == '':
                return ''
            
            correcoes = {
                'SÃ£o': 'São',
                'SÃ¡o': 'São',
                'JosÃ©': 'José',
                'TaubatÃ©': 'Taubaté',
                'CaÃ§apava': 'Caçapava',
                'BraganÃ§a': 'Bragança',
                'SebastÃ£o': 'Sebastião',
                'Ã¡': 'á',
                'Ã ': 'à',
                'Ã¢': 'â',
                'Ã£': 'ã',
                'Ã©': 'é',
                'Ãª': 'ê',
                'Ã­': 'í',
                'Ã³': 'ó',
                'Ã´': 'ô',
                'Ãµ': 'õ',
                'Ãº': 'ú',
                'Ã§': 'ç',
                'Ã±': 'ñ',
                'São Josã©': 'São José',
                'Braganã§a': 'Bragança',
                'São JosÃ© dos Campos': 'São José dos Campos',
                'São Paulo': 'São Paulo',
                'São Sebastiao': 'São Sebastião',
                'São Joao da Boa Vista': 'São João da Boa Vista',
                'São Joaquim da Barra': 'São Joaquim da Barra',
                # Correções de acentos faltantes
                'Jacarei': 'Jacareí',
                'Guaratingueta': 'Guaratinguetá',
                'Aruja': 'Arujá',
                'Jundiai': 'Jundiaí',
                'Ribeirao Preto': 'Ribeirão Preto',
                'Guaruja': 'Guarujá',
                'Peruibe': 'Peruíbe',
                'Campos do Jordao': 'Campos do Jordão',
                'Hortolandia': 'Hortolândia',
                'Mongagua': 'Mongaguá',
                'Varzea Paulista': 'Várzea Paulista',
                'Cubatao': 'Cubatão',
                'São Bento do Sapucai': 'São Bento do Sapucaí',
                'Sumare': 'Sumaré'
            }
            
            cidade_normalizada = cidade.strip()
            
            for errado, correto in correcoes.items():
                cidade_normalizada = cidade_normalizada.replace(errado, correto)
            
            preposicoes = ['de', 'da', 'das', 'do', 'dos', 'e']
            palavras = cidade_normalizada.lower().split(' ')
            palavras_capitalizadas = []
            
            for palavra in palavras:
                if palavra in preposicoes:
                    palavras_capitalizadas.append(palavra)
                else:
                    palavras_capitalizadas.append(palavra.capitalize())
            
            return ' '.join(palavras_capitalizadas)
        
        # Coletar e normalizar cidades
        cidades_normalizadas = []
        for item in dados_filtrados:
            cidade_original = item.get('Cidade', '').strip()
            if cidade_original:
                cidade_normalizada = normalizar_nome_cidade(cidade_original)
                cidades_normalizadas.append(cidade_normalizada)
        
        # Contar cidades únicas
        cidades_unicas = set(cidades_normalizadas)
        
        print(f"🏙️ Cidades únicas encontradas: {len(cidades_unicas)}")
        print(f"\n📋 Lista de todas as cidades:")
        
        contagem_cidades = {}
        for cidade in cidades_normalizadas:
            contagem_cidades[cidade] = contagem_cidades.get(cidade, 0) + 1
        
        cidades_ordenadas = sorted(contagem_cidades.items(), key=lambda x: x[1], reverse=True)
        
        # Coordenadas do mapa (atualizada com todas as cidades)
        coordenadas_cidades = {
            'São José dos Campos': [-23.2237, -45.9009],
            'Taubaté': [-23.0205, -45.5555],
            'Jacareí': [-23.3056, -45.9658],
            'Pindamonhangaba': [-22.9244, -45.4618],
            'Aparecida': [-22.8458, -45.2306],
            'Caraguatatuba': [-23.6204, -45.4130],
            'Ubatuba': [-23.4336, -45.0838],
            'São Sebastião': [-23.8129, -45.4044],
            'Mogi das Cruzes': [-23.5228, -46.1883],
            'Guaratinguetá': [-22.8161, -45.1931],
            'Paraty': [-23.2176, -44.7146],
            'Bragança Paulista': [-22.9519, -46.5425],
            'Bertioga': [-23.8543, -46.1376],
            'Lorena': [-22.7309, -45.1173],
            'São Paulo': [-23.5505, -46.6333],
            'Caçapava': [-23.1058, -45.7058],
            'Santa Isabel': [-23.3158, -46.2208],
            'Itaquaquecetuba': [-23.4864, -46.3489],
            'Arujá': [-23.3964, -46.3200],
            'Atibaia': [-23.1169, -46.5533],
            'Guarulhos': [-23.4538, -46.5333],
            'Jundiaí': [-23.1864, -46.8842],
            'Cachoeira Paulista': [-22.6658, -45.0058],
            'Cruzeiro': [-22.5761, -44.9633],
            'Santos': [-23.9618, -46.3322],
            'São Vicente': [-23.9632, -46.3919],
            'Roseira': [-22.9044, -45.3008],
            'Ribeirão Preto': [-21.1775, -47.8208],
            'Campinas': [-22.9056, -47.0608],
            'Guarujá': [-24.0139, -46.2564],
            'Peruíbe': [-24.3200, -46.9978],
            'Canas': [-22.7058, -45.0458],
            'Cunha': [-23.0766, -44.9598],
            'Campos do Jordão': [-22.7399, -45.5917],
            'Franca': [-20.5386, -47.4006],
            'Itanhaém': [-24.1828, -46.7889],
            'Itatiba': [-23.0058, -46.8383],
            'Piracaia': [-23.0533, -46.3594],
            'Franco da Rocha': [-23.3289, -46.7272],
            'Hortolândia': [-22.8583, -47.2200],
            'Mongaguá': [-24.0889, -46.6119],
            'Vargem': [-22.8858, -46.4058],
            'Louveira': [-23.0847, -46.9486],
            'Várzea Paulista': [-23.2114, -46.8294],
            'Vinhedo': [-23.0297, -46.9753],
            'Americana': [-22.7394, -47.3311],
            'Cubatão': [-23.8950, -46.4253],
            'Indaiatuba': [-23.0920, -47.2181],
            'São Bento do Sapucaí': [-22.6859, -45.7253],
            'Socorro': [-22.5919, -46.5297],
            'Sumaré': [-22.8219, -47.2669],
            'Lagoinha': [-23.1158, -45.1758],
            'Monteiro Lobato': [-22.9579, -45.8376],
            'Santa Branca': [-23.3977, -45.8863],
            'Silveiras': [-22.7997, -44.8705],
            'Suzano': [-23.5426, -46.3116],
            'Jundiaí': [-23.1864, -46.8842],
            'Ribeirão Preto': [-21.1775, -47.8208],
            'Guarujá': [-24.0139, -46.2564],
            'Peruíbe': [-24.3200, -46.9978],
            'Campos do Jordão': [-22.7399, -45.5917],
            'Hortolândia': [-22.8583, -47.2200],
            'Mongaguá': [-24.0889, -46.6119],
            'Várzea Paulista': [-23.2114, -46.8294],
            'Cubatão': [-23.8950, -46.4253],
            'São Bento do Sapucaí': [-22.6859, -45.7253],
            'Sumaré': [-22.8219, -47.2669]
        }
        
        cidades_no_mapa = 0
        cidades_sem_coordenadas = []
        
        for i, (cidade, count) in enumerate(cidades_ordenadas, 1):
            tem_coordenadas = cidade in coordenadas_cidades
            status_mapa = "✅ NO MAPA" if tem_coordenadas else "❌ SEM COORDENADAS"
            
            if tem_coordenadas:
                cidades_no_mapa += 1
            else:
                cidades_sem_coordenadas.append(cidade)
            
            print(f"  {i:2d}. {cidade}: {count} registros - {status_mapa}")
        
        print(f"\n📍 RESUMO:")
        print(f"   Total de cidades únicas: {len(cidades_unicas)}")
        print(f"   Cidades que aparecem no mapa: {cidades_no_mapa}")
        print(f"   Cidades sem coordenadas: {len(cidades_sem_coordenadas)}")
        
        if cidades_sem_coordenadas:
            print(f"\n🔍 Cidades que NÃO aparecem no mapa:")
            for cidade in cidades_sem_coordenadas:
                print(f"     - {cidade}")
        
except Exception as e:
    print(f"Erro: {e}")
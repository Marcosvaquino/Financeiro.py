import requests

try:
    response = requests.get('http://127.0.0.1:5000/logistica/api/monitoramento/dados', timeout=5)
    data = response.json()
    
    if data.get('data'):
        # Usar todos os dados (sem filtro)
        dados_filtrados = data['data']
        
        print(f"📊 Total de registros: {len(dados_filtrados)}")
        
        # Simular normalização melhorada
        def normalizar_nome_cidade(cidade):
            if not cidade or cidade.strip() == '':
                return ''
            
            # Correções específicas de encoding mais abrangentes
            correcoes = {
                # Padrões comuns de encoding UTF-8 problemático
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
                # Casos específicos identificados
                'São Josã©': 'São José',
                'Braganã§a': 'Bragança',
                'São JosÃ© dos Campos': 'São José dos Campos',
                'São Paulo': 'São Paulo',
                'São Sebastiao': 'São Sebastião',
                'São Joao da Boa Vista': 'São João da Boa Vista',
                'São Joaquim da Barra': 'São Joaquim da Barra'
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
        
        print(f"\n📋 Top 15 cidades normalizadas:")
        contagem_cidades = {}
        for cidade in cidades_normalizadas:
            contagem_cidades[cidade] = contagem_cidades.get(cidade, 0) + 1
        
        top_cidades = sorted(contagem_cidades.items(), key=lambda x: x[1], reverse=True)[:15]
        
        for i, (cidade, count) in enumerate(top_cidades, 1):
            print(f"  {i:2d}. {cidade}: {count} registros")
        
except Exception as e:
    print(f"Erro: {e}")
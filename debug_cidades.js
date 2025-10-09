// Criar script para investigar discrepância de cidades
console.log('🔍 INVESTIGAÇÃO: Discrepância Mapa vs Card Cidades');

// Simular dados filtrados para análise
fetch('http://127.0.0.1:5000/logistica/api/monitoramento/dados')
.then(response => response.json())
.then(data => {
    if (data.data) {
        // Filtrar apenas tipologia 3/4 como no teste
        const dadosFiltrados = data.data.filter(item => item['Tipologia'] === '3/4');
        
        console.log(`📊 Total de registros com tipologia 3/4: ${dadosFiltrados.length}`);
        
        // ANÁLISE DO CARD (como está no código)
        const cidadesCard = [...new Set(dadosFiltrados.map(item => item['Cidade']).filter(c => c && c.trim() !== ''))];
        console.log(`🏙️ CARD - Cidades únicas: ${cidadesCard.length}`);
        console.log('📋 CARD - Lista de cidades:', cidadesCard.sort());
        
        // ANÁLISE DO MAPA (lógica similar)
        const cidadesComCoordenadas = {};
        const coordenadasCidades = {
            'SÃO PAULO': [-23.5505, -46.6333],
            'TAUBATÉ': [-23.0205, -45.5555],
            'RIO DE JANEIRO': [-22.9068, -43.1729],
            'BELO HORIZONTE': [-19.9167, -43.9345],
            'BRASÍLIA': [-15.7942, -47.8822],
            'SALVADOR': [-12.9714, -38.5014],
            'CAMPINAS': [-22.9056, -47.0608],
            'SANTOS': [-23.9618, -46.3322],
            'SÃO JOSÉ DOS CAMPOS': [-23.2237, -45.9009],
            'SOROCABA': [-23.5015, -47.4526],
            'AMERICANA': [-22.7428, -47.3313],
            'AGUAI': [-22.0548, -46.9821],
            'APARECIDA': [-22.8497, -45.2290]
        };
        
        dadosFiltrados.forEach(item => {
            const cidade = item['Cidade'];
            if (cidade && cidade.trim() !== '') {
                const cidadeLimpa = cidade.toUpperCase().trim();
                
                // Verificar se tem coordenadas (como no mapa)
                if (coordenadasCidades[cidadeLimpa]) {
                    if (!cidadesComCoordenadas[cidadeLimpa]) {
                        cidadesComCoordenadas[cidadeLimpa] = [];
                    }
                    cidadesComCoordenadas[cidadeLimpa].push(item);
                }
            }
        });
        
        console.log(`🗺️ MAPA - Cidades com coordenadas: ${Object.keys(cidadesComCoordenadas).length}`);
        console.log('📍 MAPA - Lista de cidades com coordenadas:', Object.keys(cidadesComCoordenadas).sort());
        
        // COMPARAÇÃO
        console.log('\n🔍 ANÁLISE DA DISCREPÂNCIA:');
        console.log(`- Card conta: ${cidadesCard.length} cidades`);
        console.log(`- Mapa mostra: ${Object.keys(cidadesComCoordenadas).length} cidades`);
        
        // Cidades que aparecem no card mas não no mapa
        const cidadesSemCoordenadas = cidadesCard.filter(cidade => 
            !coordenadasCidades[cidade.toUpperCase().trim()]
        );
        
        console.log(`\n❌ Cidades SEM coordenadas (aparecem no card, não no mapa): ${cidadesSemCoordenadas.length}`);
        console.log('Lista:', cidadesSemCoordenadas.sort());
        
        // Contar registros por cidade
        console.log('\n📈 Registros por cidade:');
        const contagemCidades = {};
        cidadesCard.forEach(cidade => {
            const count = dadosFiltrados.filter(item => item['Cidade'] === cidade).length;
            contagemCidades[cidade] = count;
        });
        
        // Mostrar top 10
        const top10 = Object.entries(contagemCidades)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        console.log('Top 10 cidades por número de registros:');
        top10.forEach(([cidade, count]) => {
            const temCoordenada = coordenadasCidades[cidade.toUpperCase().trim()] ? '🗺️' : '❌';
            console.log(`${temCoordenada} ${cidade}: ${count} registros`);
        });
    }
})
.catch(err => console.error('Erro:', err));
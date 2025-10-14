# 🗺️ Funcionalidade de Macro-Regiões - Mapa de Calor

## 📋 Resumo da Implementação

Foi adicionada uma nova funcionalidade ao **Mapa de Calor** que permite visualizar os dados de duas formas:

### 🔍 Tipos de Visualização

#### 1. **Micro Setores** (Padrão - Por Cidade)
- Mostra cada cidade individualmente no mapa
- Marcadores menores e mais precisos
- Ideal para análise detalhada de operações por cidade

#### 2. **Macro Setores** (Novo - Por Região) ⭐
- Agrupa cidades em 9 macro-regiões geográficas
- Marcadores maiores representando regiões inteiras
- Ideal para visão estratégica e análise regional

---

## 🌎 As 9 Macro-Regiões

### 1. **Vale do Paraíba** (24 cidades)
Principais: São José dos Campos, Taubaté, Jacareí, Pindamonhangaba, Guaratinguetá, Aparecida

### 2. **Litoral Norte** (3 cidades)
Caraguatatuba, São Sebastião, Ubatuba

### 3. **Litoral Sul** (8 cidades)
Santos, Guarujá, Cubatão, São Vicente, Peruíbe, Bertioga, Mongaguá, Itanhaém

### 4. **SP Capital e Região Metropolitana** (9 cidades)
Guarulhos, Mogi das Cruzes, Arujá, Itaquaquecetuba, Franco da Rocha, etc.

### 5. **ABC Paulista** (7 cidades)
São Paulo, Santo André, São Bernardo do Campo, Diadema, Mauá, Osasco, São Caetano

### 6. **Campinas e Região** (13 cidades)
Campinas, Americana, Indaiatuba, Hortolândia, Sumaré, Vinhedo, etc.

### 7. **Sorocaba e Região** (1 cidade)
Sorocaba

### 8. **Interior SP** (6 cidades)
Ribeirão Preto, Franca, São João da Boa Vista, Ituverava, etc.

### 9. **Outras Capitais** (9 cidades)
Rio de Janeiro, Belo Horizonte, Curitiba, Brasília, Salvador, Porto Alegre, etc.

---

## 🎯 Como Usar

### Passo 1: Acessar o Mapa de Calor
1. Vá para **Logística > Mapa de Calor**
2. Faça upload do arquivo Excel/CSV com os dados

### Passo 2: Alternar entre Visualizações
No canto superior esquerdo do mapa, você verá dois botões:
- **📍 Micro Setores** - Mostra cidades individuais
- **🌎 Macro Setores** - Mostra regiões agrupadas

### Passo 3: Análise
- **No modo Micro:** Clique nos marcadores para ver detalhes de cada cidade
- **No modo Macro:** Clique nos marcadores para ver:
  - Nome da região
  - Total de ocorrências
  - Quantidade de cidades
  - Lista das principais cidades

---

## 🔧 Lógica Técnica

### Classificação Automática por Coordenadas
O sistema classifica automaticamente cada cidade em uma macro-região baseado em:
- **Latitude** (posição norte-sul)
- **Longitude** (posição leste-oeste)

#### Exemplos de Critérios:

**Vale do Paraíba:**
```
Latitude: entre -23.4 e -22.5
Longitude: entre -46.0 e -44.7
```

**Litoral Sul:**
```
Latitude: menor que -23.8
Longitude: maior que -47.0
```

**Campinas e Região:**
```
Latitude: entre -23.3 e -22.5
Longitude: entre -47.5 e -46.3
```

### Agrupamento de Dados
Quando seleciona "Macro Setores":
1. Sistema percorre todos os dados carregados
2. Classifica cada cidade em sua macro-região
3. Soma as ocorrências de todas as cidades da região
4. Posiciona marcador no centro geográfico da região
5. Renderiza o mapa com dados agregados

---

## 💡 Benefícios

### Para Gestores
- ✅ Visão estratégica da distribuição geográfica
- ✅ Identificação rápida de regiões com alta/baixa demanda
- ✅ Planejamento de recursos por região
- ✅ Análise comparativa entre regiões

### Para Operação
- ✅ Mantém visualização detalhada por cidade (modo Micro)
- ✅ Flexibilidade para alternar entre visões
- ✅ Filtros de intensidade funcionam em ambos os modos

---

## 📊 Estatísticas

As estatísticas no topo da página se adaptam automaticamente:
- **Modo Micro:** Mostra total de cidades, ocorrências totais, média por cidade, máximo
- **Modo Macro:** Mostra total de regiões, ocorrências totais, média por região, máximo

---

## 🎨 Visual

### Micro Setores
- Marcadores pequenos (8px)
- Calor com raio de 25px
- Zoom ajustado para mostrar todas as cidades

### Macro Setores  
- Marcadores grandes (15px)
- Calor com raio de 80px (área maior)
- Zoom ajustado para mostrar todas as regiões

---

## 🔄 Compatibilidade

- ✅ Funciona com uploads de Excel/CSV
- ✅ Funciona com dados salvos anteriormente
- ✅ Mantém filtros de intensidade
- ✅ Responsivo em dispositivos móveis

---

## 📝 Notas Técnicas

1. **Classificação é automática** - Baseada em coordenadas geográficas
2. **Sem alteração no backend** - Tudo processado no frontend
3. **Performance otimizada** - Agrupamento feito apenas quando necessário
4. **Dados originais preservados** - Alternância não perde informações

---

## 🚀 Próximas Melhorias Possíveis

- [ ] Permitir customização de macro-regiões
- [ ] Exportar relatório por região
- [ ] Filtrar regiões específicas
- [ ] Comparar períodos diferentes por região
- [ ] Adicionar mais métricas por região (frete médio, etc.)

---

**Desenvolvido com ❤️ para FRZ Logística**  
*Data: Outubro 2025*

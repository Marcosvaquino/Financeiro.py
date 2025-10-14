# 🔥 Mapa de Calor - Logística

## 📋 Descrição
Novo módulo dentro do menu **Logística** que permite importar arquivos Excel/CSV e visualizar dados geograficamente através de um mapa de calor interativo.

## ✨ Funcionalidades Implementadas

### 1. **Submenu Criado**
- ✅ Adicionado "🔥 Mapa de Calor" no menu Logística
- ✅ Acesso via: Menu > Logística > Mapa de Calor

### 2. **Upload de Arquivos**
- ✅ Suporte para arquivos: `.xlsx`, `.xls`, `.csv`
- ✅ Drag & drop ou seleção manual
- ✅ Processamento automático de dados

### 3. **Mapa Interativo**
- ✅ Visualização com Leaflet.js (mesmo do Monitoramento)
- ✅ Camada de calor (heatmap) com gradiente de cores
- ✅ Marcadores clicáveis com informações
- ✅ Zoom automático para os dados
- ✅ Legenda de intensidade

### 4. **Estatísticas**
- ✅ Total de locais mapeados
- ✅ Total acumulado de valores
- ✅ Média por local
- ✅ Maior concentração

## 📊 Formato do Arquivo Excel/CSV

### ✅ Formato Recomendado (Seu caso - 185 cidades)
```
| Cidade         | Endereço Completo              | Bairro           | Estado |
|----------------|--------------------------------|------------------|--------|
| São Paulo      | RUA PROFA NINA STOCCO, 833     | JARDIM CATANDUVA | SP     |
| Campinas       | AVENIDA ANTONIO CARLOS, 460    | JARDIM PROENÇA   | SP     |
| Santo André    | Avenida Dom Pedro II, 1689     | Campestre        | SP     |
```

**O sistema irá:**
1. 🎯 **Primeiro:** Tentar encontrar a cidade no banco de cidades pré-cadastradas (19 cidades SP)
2. 🌐 **Segundo:** Geocodificar usando Endereço + Bairro + Cidade + Estado
3. 🏘️ **Terceiro:** Geocodificar usando apenas Bairro + Cidade + Estado
4. 🗺️ **Quarto:** Geocodificar usando apenas Cidade + Estado
5. 📊 **Valor:** Se não houver coluna "Valor", conta automaticamente quantas vezes cada cidade aparece

### Opção 1: Com Coordenadas (Mais Rápido)
```
| Cidade              | Latitude  | Longitude  | Valor |
|---------------------|-----------|------------|-------|
| SÃO PAULO          | -23.5505  | -46.6333   | 150   |
| RIO DE JANEIRO     | -22.9068  | -43.1729   | 120   |
| BELO HORIZONTE     | -19.9167  | -43.9345   | 80    |
```

### Opção 2: Apenas Cidade (Geocodificação Automática)
```
| Cidade              | Valor |
|---------------------|-------|
| SÃO PAULO          | 150   |
| RIO DE JANEIRO     | 120   |
| BELO HORIZONTE     | 80    |
```

**Cidades SP pré-cadastradas (geocodificação instantânea):**
- São Paulo, Campinas, Santos, São José dos Campos
- Guarulhos, Santo André, Osasco, São Bernardo do Campo
- Sorocaba, Ribeirão Preto, Mauá, Diadema
- Piracicaba, Barueri, Itaquaquecetuba, Jundiaí
- Taboão da Serra, Indaiatuba, Itapecerica da Serra

## 🎨 Esquema de Cores do Mapa

```
🔵 Azul   → Intensidade Baixa (0-20%)
🟢 Verde  → Intensidade Média-Baixa (20-40%)
🟡 Amarelo→ Intensidade Média (40-60%)
🟠 Laranja→ Intensidade Média-Alta (60-80%)
🔴 Vermelho→ Intensidade Alta (80-100%)
```

## 🚀 Como Usar

### Passo 1: Acessar o Módulo
1. Abra o sistema
2. Clique em **Logística** no menu lateral
3. Selecione **🔥 Mapa de Calor**

### Passo 2: Preparar Arquivo
1. Crie um Excel ou CSV com as colunas corretas
2. Preencha com seus dados
3. Salve o arquivo

### Passo 3: Upload
1. Arraste o arquivo para a área de upload **OU**
2. Clique em "Selecionar Arquivo"
3. Escolha seu arquivo
4. Clique em **Processar**

### Passo 4: Visualizar
1. Aguarde o processamento
2. O mapa será atualizado automaticamente
3. Clique nos marcadores para ver detalhes
4. Use os botões de zoom (+/-) para navegar

## 📁 Arquivos Criados

### Backend (Python)
- `financeiro/logistica.py` - Adicionado:
  - Rota `/mapa_calor` (página)
  - API `/api/mapa_calor/upload` (processamento)

### Frontend (HTML)
- `financeiro/templates/logistica/mapa_calor.html` - Novo arquivo completo

### Menu
- `financeiro/templates/base.html` - Atualizado com novo submenu

### Utilitários
- `gerar_exemplo_mapa_calor.py` - Script para gerar arquivos de teste

## 🛠️ Dependências Instaladas
```bash
pandas      # Processamento de Excel/CSV
openpyxl    # Leitura de arquivos .xlsx
```

## 📦 Bibliotecas JavaScript Usadas
- **Leaflet.js** - Mapa base
- **Leaflet.heat** - Camada de calor
- **Bootstrap 5** - Interface
- **Font Awesome 6** - Ícones

## 🎯 Casos de Uso

### 1. **Logística de Entregas**
- Visualizar concentração de entregas por cidade
- Identificar regiões de maior demanda
- Planejar rotas baseado em densidade

### 2. **Análise de Vendas**
- Mapear volume de vendas por região
- Identificar mercados potenciais
- Visualizar distribuição geográfica

### 3. **Gestão de Frotas**
- Ver distribuição de veículos
- Identificar áreas de cobertura
- Otimizar alocação de recursos

### 4. **Análise de Clientes**
- Visualizar distribuição de clientes
- Identificar clusters geográficos
- Planejar expansão regional

## 🔧 Funcionalidades Técnicas

### Processamento Inteligente
- ✅ Detecção automática de colunas
- ✅ Geocodificação de cidades conhecidas
- ✅ Validação de dados
- ✅ Tratamento de erros

### Interface Responsiva
- ✅ Adaptável a diferentes telas
- ✅ Drag & drop moderno
- ✅ Feedback visual
- ✅ Loading states

### Mapa Avançado
- ✅ Gradiente customizado
- ✅ Intensidade configurável
- ✅ Popups informativos
- ✅ Controles de zoom

## 📝 Notas Importantes

1. **Formato dos Dados:**
   - Coluna "Valor" deve conter números
   - Coordenadas devem usar formato decimal
   - Cidades devem estar em MAIÚSCULAS para geocodificação

2. **Limites:**
   - Tamanho máximo do arquivo: Conforme configuração do servidor
   - Cidades não cadastradas: Precisam ter coordenadas no arquivo

3. **Performance:**
   - Arquivos grandes podem demorar para processar
   - O mapa ajusta automaticamente o zoom

## 🎨 Personalização

### Adicionar Novas Cidades
Edite o arquivo `logistica.py` e adicione no dicionário `cidades_coords`:

```python
cidades_coords = {
    'NOVA CIDADE': [-00.0000, -00.0000],
    # ... outras cidades
}
```

### Ajustar Cores do Mapa
No arquivo `mapa_calor.html`, modifique o gradiente:

```javascript
gradient: {
    0.0: 'blue',
    0.5: 'yellow',
    1.0: 'red'
}
```

## 🐛 Troubleshooting

### Arquivo não processa
- ✅ Verifique o formato (.xlsx, .xls, .csv)
- ✅ Confirme as colunas necessárias
- ✅ Veja o console do navegador (F12)

### Mapa não aparece
- ✅ Verifique conexão com internet (Leaflet CDN)
- ✅ Recarregue a página
- ✅ Limpe o cache do navegador

### Cidades não aparecem
- ✅ Verifique se está em MAIÚSCULAS
- ✅ Adicione coordenadas manualmente
- ✅ Veja logs no console Python

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Consulte os logs do sistema
3. Verifique o console do navegador (F12)

---

**Desenvolvido com ❤️ para FRZ Logística**

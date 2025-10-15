# Dashboard de Armazém - Ajustes Implementados

## 📋 Resumo das Mudanças

Baseado no seu dashboard original (print fornecido), implementei as seguintes melhorias:

## ✅ Alterações Realizadas

### 1. **Filtros Atualizados**
- ✅ **Dia**: Filtra por dia específico (1-31)
- ✅ **Mês**: Filtra por mês (Janeiro - Dezembro)
- ✅ **Ano**: Filtra por ano
- ✅ **Filial**: Filtra por SJC, JAC ou TODAS

### 2. **Gráficos Implementados**

#### 📊 **Embarcadores - JAC e SJC** (Substituiu "Distribuição por Cliente")
- Gráfico de barras horizontal
- Mostra TODOS os embarcadores:
  - **MIEGGS** (Mafrig Foods)
  - **FRIBOI**
  - **MINERVA** (Mafrig Atacado)
  - **GOLD PÃO**
  - **VALENCIO** (compartilhado)
  - **ALIBEM** (compartilhado)
  - **SAUDALI** (compartilhado)
  - **PAMPLONA** (compartilhado)
  - **GT FOODS** (compartilhado)
  - **SANTA LUCIA** (compartilhado)
  - **MAFRIG** (compartilhado total)
  - **ADORO** (preparado para futuro)
  - **FRZ LOG** (preparado para futuro)
- Exibe tanto **Carros** quanto **Peso** para cada embarcador

#### 📈 **Análise Mensal - Peso e Carros** (Ajustado conforme solicitado)
- Gráfico combinado de **barras** (Peso) + **linha** (Carros)
- Mostra a evolução mensal das duas filiais combinadas
- Eixo Y duplo:
  - Esquerda: Peso em toneladas (barras laranjas)
  - Direita: Número de carros (linha azul)

#### 🥧 **Peso x Bases - Anual** (Mantido, similar ao seu)
- Gráfico de pizza (donut)
- Mostra a distribuição de peso entre:
  - **SJC** (São José dos Campos)
  - **JAC** (Jacareí) - preparado para quando tiver dados

#### 📈 **Evolução Diária de Carros** (Melhorado)
- Mostra todos os dias do mês selecionado (1 a 31)
- Se não selecionar mês/ano, mostra os últimos 31 dias
- Gráfico de linha com área preenchida

### 3. **Tabela Detalhada - Últimos 30 dias**
✅ Agora inclui **TODOS os embarcadores** como colunas:
- Data
- Filial
- Total Carros
- Peso
- MIEGGS
- FRIBOI
- MINERVA
- GOLD PÃO
- VALENCIO
- ALIBEM
- SAUDALI
- PAMPLONA
- GT FOODS
- SANTA LUCIA
- MAFRIG (compartilhado)
- ADORO
- FRZ LOG

### 4. **Embarcadores Compartilhados**
✅ **Entendimento implementado**:
- A coluna "COMPARTILHADO" na planilha de SJC tem subcolunas:
  - **VALENCIO**
  - **ALIBEM/AGRA**
  - **SAUDALI**
  - **PAMPLONA**
  - **GT FOODS**
  - **SANTA LUCIA**
- Cada uma dessas subcolunas representa carros individuais
- O peso total do compartilhado está na coluna "Compartilhado_Peso"
- Todos esses embarcadores agora aparecem no gráfico e na tabela

### 5. **Removidos** (conforme solicitado)
- ❌ 🥧 Distribuição por Cliente
- ❌ 📅 Operações por Dia da Semana

## 🎨 Design Visual

- **Cores modernas**: Gradiente roxo/azul no fundo
- **Cards brancos** com sombras suaves
- **Gráficos coloridos** com paleta profissional
- **Tabela estilizada** com hover effects
- **Responsivo** para diferentes tamanhos de tela

## 📂 Arquivos Modificados

1. **`financeiro/armazem.py`**
   - Função `carregar_dados_armazem()`: Corrigida para ler todas as colunas corretamente
   - API `/api/dados`: Reescrita com novos filtros e estrutura de dados
   - Adicionados todos os embarcadores compartilhados

2. **`financeiro/templates/armazem_novo.html`**
   - Novo template HTML completo
   - Filtros: Dia, Mês, Ano, Filial
   - 4 gráficos principais (Chart.js)
   - Tabela com todas as colunas de embarcadores

3. **`test_armazem_server.py`** (novo)
   - Servidor de teste simplificado
   - Evita problemas com banco de dados do módulo logística
   - Use este para testar: `python test_armazem_server.py`

## 🚀 Como Usar

### Iniciar o servidor:
```bash
python test_armazem_server.py
```

### Acessar no navegador:
```
http://localhost:5000/armazem
```

### Testar filtros:
1. Selecione um **mês** (ex: Outubro)
2. Selecione um **ano** (ex: 2025)
3. Clique em **🔍 Filtrar**
4. O gráfico "Evolução Diária" mostrará todos os dias daquele mês (1-31)

## 📊 Estrutura da Planilha ARMAZEM.xlsx

```
Linha 1: "São Jose dos Campos" (header geral)
Linha 2: MAFRIG (FOODS) | MAFRIG (ATACADO) | GOLD PÃO | COMPARTILHADO | FRIBOI | TOTAL SJC
Linha 3: CARROS | PESO | CARROS | PESO | ... | VALENCIO | ALIBEM/AGRA | SAUDALI | ...
Linha 4+: Dados
```

## 🔄 Próximos Passos (Sugestões)

1. **Adicionar dados de JAC**:
   - Criar planilha ou aba para Jacareí
   - Atualizar função `carregar_dados_armazem()` para ler ambas as filiais
   - O gráfico de pizza já está preparado

2. **Exportar relatórios**:
   - Botão para baixar dados em Excel
   - Exportar gráficos como imagem

3. **Comparação entre filiais**:
   - Gráfico lado a lado SJC vs JAC
   - Tabela comparativa

4. **Alertas e metas**:
   - Definir metas mensais
   - Alertas quando abaixo da meta

## 🐛 Observações

- Os embarcadores **ADORO** e **FRZ LOG** estão preparados na estrutura, mas com valores zerados
- Quando tiver dados reais, basta adicionar as colunas correspondentes na planilha
- O peso dos embarcadores compartilhados individuais não está separado na planilha original, apenas o total

## 📞 Dúvidas?

Se precisar de mais ajustes ou adicionar novos recursos, é só avisar!

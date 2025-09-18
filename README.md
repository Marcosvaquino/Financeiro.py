# 💼 Sistema Financeiro - Projeção e Controle

Sistema web completo para controle financeiro empresarial com funcionalidades de importação de dados, projeções e dashboard interativo.

## 🚀 Funcionalidades

- **Dashboard Financeiro**: Visualização de receitas, custos, saldo e rentabilidade
- **Importação de Dados**: Upload e processamento de arquivos CSV
- **Projeções**: Sistema de planejamento financeiro por cliente e período
- **Filtros Avançados**: Análise por mês/ano específico
- **Rentabilidade**: Cálculo automático de margens de lucro
- **Cards Inteligentes**: 
  - Total a Receber (19 clientes pré-cadastrados)
  - Total a Pagar (todos os custos)
  - Saldo Projetado
  - Rentabilidade

## 🛠️ Tecnologias

- **Backend**: Python 3.x + Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Processamento**: Pandas para CSV
- **Formatação**: Padrão brasileiro (R$ 1.234.567,89)

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/PROJETOFINANCEIRO.PY.git
cd PROJETOFINANCEIRO.PY
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r financeiro/requirements.txt
```

## 🚀 Como Executar

1. Ative o ambiente virtual (se não estiver ativo)
2. Execute o servidor:
```bash
python -m financeiro.main
```

3. Acesse no navegador: `http://127.0.0.1:5000`

## 📊 Estrutura do Projeto

```
financeiro/
├── main.py              # Aplicação Flask principal
├── database.py          # Configuração do banco de dados
├── importacao.py        # Lógica de importação de CSV
├── schema.sql           # Estrutura do banco
├── requirements.txt     # Dependências Python
├── static/
│   └── style.css       # Estilos CSS
├── templates/          # Templates HTML
│   ├── base.html
│   ├── planejamento.html
│   ├── projecao.html
│   └── importacao.html
└── uploads/            # Arquivos CSV importados
```

## 💡 Uso

### Importação de Dados
1. Acesse a seção "Importação"
2. Faça upload dos arquivos CSV (contas-a-receber.csv, contas-a-pagar.csv)
3. O sistema processará automaticamente

### Dashboard
1. Acesse "Painel"
2. Use os filtros de mês/ano
3. Visualize os cards com dados financeiros

### Projeções
1. Acesse "Projeção"
2. Configure valores por cliente e período
3. Salve as projeções

## 🎯 Clientes Pré-cadastrados (19)

O sistema trabalha com 19 clientes específicos para cálculos de receita:
- ADORO, AGRA FOODS, ALIBEM, FRIBOI
- GOLDPAO CD SAO JOSE DOS CAMPOS, GTFOODS BARUERI
- JK DISTRIBUIDORA, LATICINIO CARMONA
- MARFRIG (ITUPEVA CD, PROMISSAO, GLOBAL FOODS)
- MINERVA S A, PAMPLONA JANDIRA
- PEIXES MEGGS PESCADOS LTDA, SANTA LUCIA
- SAUDALI, VALENCIO JATAÍ

## 📈 Cálculos

- **Total a Receber**: Soma de todos os valores dos 19 clientes (qualquer status)
- **Receita Realizada**: Apenas valores com status "RECEBIDO" dos 19 clientes
- **Total a Pagar**: Todos os custos do período filtrado
- **Rentabilidade**: ((Receita - Custos) / Custos) × 100

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

Para dúvidas ou suporte, abra uma issue no GitHub.
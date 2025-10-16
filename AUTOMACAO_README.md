# Automação ESL Cloud - Relatório Contas a Receber

## 📋 Descrição

Script de automação para extrair relatórios de **Contas a Receber** do sistema ESL Cloud de forma automática.

## 🚀 Como Usar

### 1️⃣ Instalar Dependências

Primeiro, instale as bibliotecas necessárias:

```powershell
pip install selenium python-dotenv
```

### 2️⃣ Configurar ChromeDriver

O Selenium precisa do ChromeDriver compatível com seu Chrome:

**Opção A - Instalação Automática (Recomendado):**
```powershell
pip install webdriver-manager
```

**Opção B - Download Manual:**
1. Verifique sua versão do Chrome: `chrome://settings/help`
2. Baixe o ChromeDriver em: https://chromedriver.chromium.org/
3. Coloque o `chromedriver.exe` na pasta do projeto ou no PATH

### 3️⃣ Configurar Credenciais

1. Copie o arquivo `.env.example` para `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edite o arquivo `.env` e adicione suas credenciais:
   ```
   ESL_EMAIL=seu_email@empresa.com
   ESL_SENHA=SuaSenhaAqui123
   ```

⚠️ **IMPORTANTE:** O arquivo `.env` não deve ser versionado (já está no .gitignore)

### 4️⃣ Executar o Script

```powershell
python automacao_eslcloud.py
```

## ⚙️ Personalização

### Alterar o Período do Relatório

Edite o arquivo `automacao_eslcloud.py` na função `main()`:

```python
automacao.executar(
    data_inicio="01/01/2025",  # Altere aqui
    data_fim="31/12/2025"      # Altere aqui
)
```

### Alterar Pasta de Download

```python
# No código, modifique:
automacao = ESLCloudAutomation(download_path="C:/MeusRelatorios")
```

## 🔍 Fluxo de Automação

O script realiza as seguintes etapas:

1. ✅ Acessa o sistema ESL Cloud
2. ✅ Faz login com email e senha
3. ✅ Clica no menu ESL Cloud
4. ✅ Acessa o módulo Financeiro
5. ✅ Abre Relatórios > Contas a Receber
6. ✅ Limpa o campo Filial
7. ✅ Define período de emissão (01/01/2025 - 31/12/2025)
8. ✅ Busca os dados (clica na lupa)
9. ✅ Exporta para Excel
10. ✅ Confirma o download do arquivo

## 🛠️ Solução de Problemas

### "Credenciais não configuradas"
- Verifique se o arquivo `.env` existe e está preenchido corretamente

### "ChromeDriver não encontrado"
- Instale o webdriver-manager: `pip install webdriver-manager`
- Ou baixe manualmente o ChromeDriver compatível

### "Elemento não encontrado"
- O site pode ter mudado a estrutura
- Aumente os tempos de espera no código
- Execute em modo visual (comente a linha `--headless`)

### Modal não aparece
- O arquivo já está sendo gerado
- Verifique sua pasta de Downloads
- Tente aumentar o tempo de espera

## 📦 Dependências

- `selenium` - Automação de navegador
- `python-dotenv` - Gerenciamento de variáveis de ambiente
- `webdriver-manager` - (Opcional) Gerenciamento automático do ChromeDriver

## 🔒 Segurança

- ✅ Credenciais em arquivo `.env` (não versionado)
- ✅ Sem senhas em código
- ✅ Arquivo `.env.example` como template

## 📝 Notas

- O script abre o navegador visualmente por padrão
- Para rodar em background, descomente a linha `--headless` no código
- Os arquivos são salvos na pasta Downloads do Windows por padrão
- Tempo médio de execução: 30-60 segundos

## 👨‍💻 Autor

Desenvolvido para FRZ Logística

---

**Última atualização:** Outubro 2025

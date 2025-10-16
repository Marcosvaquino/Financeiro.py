# 🚀 GUIA RÁPIDO - AUTOMAÇÃO ESL CLOUD

## ⚡ Início Rápido (3 passos)

### 1️⃣ Instalar
```powershell
.\instalar_automacao.ps1
```

### 2️⃣ Configurar
Edite o arquivo `.env` e adicione suas credenciais:
```
ESL_EMAIL=seu_email@empresa.com
ESL_SENHA=sua_senha_aqui
```

### 3️⃣ Executar
```powershell
python automacao_eslcloud.py
```

## ✅ Pronto! 

O arquivo Excel será baixado automaticamente na sua pasta **Downloads**.

---

## 📝 Personalizações Comuns

### Mudar o período do relatório

Edite `automacao_eslcloud.py` na linha final:

```python
automacao.executar(
    data_inicio="01/01/2025",  # ← Altere aqui
    data_fim="31/03/2025"      # ← Altere aqui
)
```

### Rodar em segundo plano (sem abrir navegador)

No arquivo `automacao_eslcloud.py`, linha 52, descomente:

```python
chrome_options.add_argument('--headless')  # ← Remova o #
```

### Escolher pasta de download

```python
automacao = ESLCloudAutomation(
    download_path="C:/MeusRelatorios"  # ← Sua pasta
)
```

---

## 🆘 Problemas Comuns

| Erro | Solução |
|------|---------|
| "Credenciais não configuradas" | Verifique o arquivo `.env` |
| "ChromeDriver não encontrado" | Execute: `pip install webdriver-manager` |
| "Modal não aparece" | Aumente tempo de espera ou verifique Downloads |
| Site mudou | Avise para ajustar os seletores |

---

## 📞 Suporte

Qualquer dúvida, entre em contato!

**Desenvolvido para FRZ Logística** 🚛

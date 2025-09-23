# 🚛 INTEGRAÇÃO MANIFESTO + VEÍCULOS - GUIA DE USO

## 📋 **RESUMO DA IMPLEMENTAÇÃO**

Criamos uma integração completa entre o sistema de veículos e manifestos que permite:

✅ **242 veículos** cadastrados no banco `financeiro.db`  
✅ **Busca otimizada** por placa individual ou múltiplas  
✅ **Enriquecimento automático** de dados do manifesto  
✅ **Cálculos de custo** baseados no status dos veículos  
✅ **Relatórios detalhados** com alertas e sugestões  

---

## 🗄️ **ESTRUTURA DO BANCO DE DADOS**

```sql
-- Tabela: veiculos_suporte
- placa: TEXT (PK)           -- Chave primária
- status: TEXT               -- FIXO ou SPOT  
- tipologia: TEXT            -- 3/4, TRUCK, TOCO, VUC
- data_cadastro: DATETIME    -- Data de cadastro
- ativo: BOOLEAN             -- Se está ativo (1/0)

-- Distribuição atual:
- Total: 242 veículos
- FIXO: 29 veículos (próprios)
- SPOT: 213 veículos (terceirizados)
```

---

## 🔧 **COMO USAR NO SEU MANIFESTO**

### **1. Importação Simples**
```python
from financeiro.manifesto_integration import processar_manifesto

# Suas placas do manifesto
placas = ["AXR4A69", "CDL3807", "ABC1234"]

# Enriquecer com dados dos veículos
dados_enriquecidos = processar_manifesto(placas)

# Resultado: cada placa terá status, tipologia, etc.
```

### **2. Com Dados Completos do Manifesto**
```python
# Seus dados originais do manifesto
manifesto = [
    {"id": 1, "placa": "AXR4A69", "destino": "São Paulo", "peso": 1500},
    {"id": 2, "placa": "CDL3807", "destino": "RJ", "peso": 2000}
]

# Enriquecer mantendo dados originais
resultado = processar_manifesto(manifesto)

# Resultado: dados originais + informações dos veículos
# resultado[0] = {
#     "id": 1, 
#     "placa": "AXR4A69", 
#     "destino": "São Paulo", 
#     "peso": 1500,
#     "veiculo_status": "SPOT",      # ← NOVO
#     "veiculo_tipologia": "3/4",    # ← NOVO
#     "veiculo_encontrado": True     # ← NOVO
# }
```

### **3. Validação Rápida de Placas**
```python
from financeiro.manifesto_integration import validar_placas_manifesto

placas = ["AXR4A69", "INEXISTENTE", "CDL3807"]
validacao = validar_placas_manifesto(placas)

print(f"Válidas: {validacao['validas']}")      # ["AXR4A69", "CDL3807"]
print(f"Inválidas: {validacao['invalidas']}")  # ["INEXISTENTE"]
print(f"% Válido: {validacao['percentual_valido']}%")  # 66.67%
```

### **4. Cálculo de Custos Automático**
```python
from financeiro.manifesto_integration import calcular_custos_manifesto

# Dados enriquecidos + distância
custos = calcular_custos_manifesto(dados_enriquecidos, distancia_km=150)

print(f"Veículos FIXO: {custos['veiculos_fixo']} = R$ {custos['custo_fixo_total']}")
print(f"Veículos SPOT: {custos['veiculos_spot']} = R$ {custos['custo_spot_total']}")
print(f"TOTAL: R$ {custos['custo_total']}")
print(f"Economia se todos FIXO: R$ {custos['economia_se_todos_fixo']}")
```

---

## 📊 **FUNÇÕES DISPONÍVEIS**

### **Busca Individual**
```python
from financeiro.veiculo_helper import get_veiculo_status, get_veiculo_tipologia

status = get_veiculo_status("AXR4A69")      # "SPOT"
tipologia = get_veiculo_tipologia("AXR4A69") # "3/4"
```

### **Busca Múltipla Otimizada**
```python
from financeiro.veiculo_helper import VeiculoHelper

placas = ["AXR4A69", "CDL3807", "CFY3C64"]
dados = VeiculoHelper.buscar_multiplas_placas(placas)

# dados["AXR4A69"] = {
#     "placa": "AXR4A69",
#     "status": "SPOT", 
#     "tipologia": "3/4",
#     "encontrado": True
# }
```

### **Relatório Completo**
```python
from financeiro.manifesto_integration import gerar_relatorio_manifesto_veiculos

relatorio = gerar_relatorio_manifesto_veiculos(dados_enriquecidos)

# relatorio = {
#     "resumo": {"total_registros": 5, "veiculos_encontrados": 4, ...},
#     "status": {"fixo": 1, "spot": 3},
#     "tipologias": {"3/4": 2, "TRUCK": 1, "VUC": 1},
#     "alertas": ["⚠️ 1 veículos não encontrados no sistema"]
# }
```

---

## 💡 **CASOS DE USO PRÁTICOS**

### **1. Validação de Manifesto**
```python
# Antes de processar manifesto, validar se veículos existem
validacao = validar_placas_manifesto(placas_do_manifesto)
if validacao['percentual_valido'] < 90:
    print("❌ Muitos veículos não cadastrados!")
```

### **2. Cálculo de Custo por Rota**
```python
# Para cada rota do manifesto
for rota in rotas:
    custos = calcular_custos_manifesto(rota['veiculos'], rota['distancia'])
    rota['custo_estimado'] = custos['custo_total']
    rota['economia_potencial'] = custos['economia_se_todos_fixo']
```

### **3. Alertas Automáticos**
```python
relatorio = gerar_relatorio_manifesto_veiculos(manifesto_enriquecido)
for alerta in relatorio['alertas']:
    enviar_notificacao(alerta)  # Sua função de notificação
```

### **4. Dashboard de Status**
```python
resumo = VeiculoHelper.get_status_resumo()
# resumo = {
#     "FIXO": {"total": 29, "ativos": 29},
#     "SPOT": {"total": 213, "ativos": 213},
#     "TOTAL": {"total": 242, "ativos": 242}
# }
```

---

## 🚀 **PERFORMANCE**

- ✅ **Busca otimizada**: Uma query para múltiplas placas
- ✅ **Cache interno**: Evita consultas desnecessárias  
- ✅ **Normalização**: Placas sempre em maiúscula
- ✅ **Tratamento de erros**: Nunca quebra o fluxo

---

## 📂 **ARQUIVOS CRIADOS**

1. **`financeiro/veiculo_helper.py`** - Funções core de busca
2. **`financeiro/manifesto_integration.py`** - Integração com manifesto
3. **`importar_veiculos.py`** - Script de importação (já usado)
4. **`exemplo_manifesto_veiculos.py`** - Exemplos de uso

---

## ✨ **PRÓXIMOS PASSOS SUGERIDOS**

1. **Testar com seus dados reais** de manifesto
2. **Integrar no fluxo atual** do processamento
3. **Configurar alertas** para veículos não encontrados
4. **Personalizar custos** por km/status conforme sua operação
5. **Adicionar logs** para auditoria das consultas

---

**🎯 PRONTO PARA USO!** 

Agora o manifesto pode buscar automaticamente o status (FIXO/SPOT) e tipologia de qualquer placa cadastrada nos seus 242 veículos! 🚛💨
"""
Módulo para processamento de arquivos MANIFESTO
Lógica CTRL+C + CTRL+V - preserva formatação exata do Excel
"""
import os
import openpyxl
import csv
import re
from datetime import datetime

def tentar_converter_numero_brasileiro(texto):
    """
    Tenta converter texto que pode ser um número em formato brasileiro
    Exemplos: "1.234,56", "1234.56", "1,234.56", "1234"
    """
    if not texto or not isinstance(texto, str):
        return None
    
    texto_limpo = texto.strip().replace(' ', '')
    
    # Se está vazio após limpeza
    if not texto_limpo:
        return None
    
    # Verificar se tem apenas números, vírgulas e pontos
    if not re.match(r'^-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?$', texto_limpo):
        return None
    
    try:
        # Caso 1: Formato brasileiro "1.234,56"
        if ',' in texto_limpo and '.' in texto_limpo:
            # Se vírgula vem depois do ponto, é formato brasileiro
            pos_virgula = texto_limpo.rfind(',')
            pos_ponto = texto_limpo.rfind('.')
            
            if pos_virgula > pos_ponto:
                # Formato brasileiro: 1.234,56
                numero_str = texto_limpo.replace('.', '').replace(',', '.')
                return float(numero_str)
            else:
                # Formato americano: 1,234.56  
                numero_str = texto_limpo.replace(',', '')
                return float(numero_str)
        
        # Caso 2: Apenas vírgula "1234,56" (brasileiro)
        elif ',' in texto_limpo:
            numero_str = texto_limpo.replace(',', '.')
            return float(numero_str)
        
        # Caso 3: Apenas ponto "1234.56" ou "1.234" (pode ser americano ou separador de milhares)
        elif '.' in texto_limpo:
            # Se tem mais de 3 dígitos após o último ponto, é separador decimal
            partes = texto_limpo.split('.')
            if len(partes[-1]) <= 2:  # Última parte tem 1-2 dígitos = decimal
                return float(texto_limpo)
            else:  # Mais de 2 dígitos = separador de milhares brasileiro
                numero_str = texto_limpo.replace('.', '')
                return float(numero_str)
        
        # Caso 4: Apenas números "1234"
        else:
            return float(texto_limpo)
            
    except (ValueError, AttributeError):
        return None

def processar_manifesto(arquivo_upload):
    """
    Processa arquivo de manifesto usando lógica CTRL+C + CTRL+V
    
    Args:
        arquivo_upload: FileStorage object do Flask
        
    Returns:
        dict: {"success": bool, "message": str, "dados": dict}
    """
    try:
        # CTRL+C - Ler Excel preservando formatação
        dados_excel = ler_excel_ctrl_c(arquivo_upload)
        
        # CTRL+V - Salvar como CSV com encoding correto
        resultado_csv = salvar_csv_ctrl_v(dados_excel, arquivo_upload.filename)
        
        return {
            "success": True,
            "message": f"Manifesto processado: {resultado_csv['linhas']} linhas salvas em {resultado_csv['arquivo']}",
            "dados": {
                "linhas_processadas": resultado_csv['linhas'],
                "arquivo_csv": resultado_csv['arquivo'],
                "colunas": dados_excel['colunas']
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao processar manifesto: {str(e)}",
            "dados": {}
        }

def ler_excel_ctrl_c(arquivo_upload):
    """
    CTRL+C - Lê Excel preservando formatação exata
    """
    # Carregar workbook com data_only=True para valores calculados
    wb = openpyxl.load_workbook(arquivo_upload, data_only=True)
    ws = wb.active
    
    dados = []
    colunas = []
    
    # Detectar colunas pela primeira linha
    primeira_linha = True
    for linha in ws.iter_rows(values_only=True):
        if not any(linha):  # Pular linhas vazias
            continue
            
        if primeira_linha:
            colunas = [str(cel) if cel is not None else f"Coluna_{i+1}" for i, cel in enumerate(linha)]
            primeira_linha = False
            continue
            
        # Processar dados preservando formato
        linha_processada = []
        for cel in linha:
            if cel is None:
                linha_processada.append("")
            elif isinstance(cel, datetime):
                # Preservar datas no formato dd/mm/yyyy
                linha_processada.append(cel.strftime("%d/%m/%Y"))
            elif isinstance(cel, (int, float)):
                # NÚMEROS: converter para inteiro (sem casa decimal)
                linha_processada.append(int(cel))
            else:
                # TEXTO: só limpar, não converter
                valor_str = str(cel).replace('\n', ' ').replace('\r', '').strip()
                linha_processada.append(valor_str)
        
        dados.append(linha_processada)
    
    return {
        "colunas": colunas,
        "dados": dados
    }

def salvar_csv_ctrl_v(dados_excel, nome_original):
    """
    CTRL+V - Salva como CSV com encoding UTF-8-BOM
    """
    # Criar diretório se não existir
    pasta_saida = "financeiro/uploads/manifestos"
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_csv = f"MANIFESTO_{timestamp}_{nome_original.replace('.xlsx', '.csv')}"
    caminho_completo = os.path.join(pasta_saida, nome_csv)
    
    # Salvar CSV com UTF-8-BOM e delimitador ponto-e-vírgula
    with open(caminho_completo, 'w', encoding='utf-8-sig', newline='') as arquivo_csv:
        writer = csv.writer(arquivo_csv, delimiter=';')
        
        # Escrever cabeçalho
        writer.writerow(dados_excel['colunas'])
        
        # Escrever dados
        for linha in dados_excel['dados']:
            writer.writerow(linha)
    
    return {
        "arquivo": nome_csv,
        "caminho": caminho_completo,
        "linhas": len(dados_excel['dados'])
    }

def validar_estrutura_manifesto(dados_excel):
    """
    Valida se o arquivo tem a estrutura esperada de manifesto
    """
    colunas_obrigatorias = ['manifesto', 'data', 'veiculo', 'motorista']
    colunas_encontradas = [col.lower() for col in dados_excel['colunas']]
    
    for col_obrig in colunas_obrigatorias:
        if not any(col_obrig in col for col in colunas_encontradas):
            return False, f"Coluna '{col_obrig}' não encontrada"
    
    return True, "Estrutura válida"
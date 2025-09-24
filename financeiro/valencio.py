"""
Módulo para processamento de arquivos VALENCIO
Lógica de cálculos e processamento de dados de frete
"""
import os
import openpyxl
import csv
import re
from datetime import datetime

def tentar_converter_numero_brasileiro(texto):
    """
    Tenta converter texto que pode ser um número em formato brasileiro
    """
    if not texto or not isinstance(texto, str):
        return None
    
    texto_limpo = texto.strip().replace(' ', '')
    
    if not texto_limpo:
        return None
    
    if not re.match(r'^-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?$', texto_limpo):
        return None
    
    try:
        # Formato brasileiro "1.234,56"
        if ',' in texto_limpo and '.' in texto_limpo:
            pos_virgula = texto_limpo.rfind(',')
            pos_ponto = texto_limpo.rfind('.')
            
            if pos_virgula > pos_ponto:
                numero_str = texto_limpo.replace('.', '').replace(',', '.')
                return float(numero_str)
            else:
                numero_str = texto_limpo.replace(',', '')
                return float(numero_str)
        
        elif ',' in texto_limpo:
            numero_str = texto_limpo.replace(',', '.')
            return float(numero_str)
        
        elif '.' in texto_limpo:
            partes = texto_limpo.split('.')
            if len(partes[-1]) <= 2:
                return float(texto_limpo)
            else:
                numero_str = texto_limpo.replace('.', '')
                return float(numero_str)
        
        else:
            return float(texto_limpo)
            
    except (ValueError, AttributeError):
        return None

def processar_valencio(arquivo_upload):
    """
    Processa arquivo de valencio/cálculos
    
    Args:
        arquivo_upload: FileStorage object do Flask
        
    Returns:
        dict: {"success": bool, "message": str, "dados": dict}
    """
    try:
        # Determinar nome original quando arquivo_upload for caminho string
        if isinstance(arquivo_upload, str):
            nome_original = os.path.basename(arquivo_upload)
        else:
            nome_original = getattr(arquivo_upload, 'filename', 'uploaded_valencio.xlsx')

        # Ler dados do Excel
        dados_excel = ler_excel_valencio(arquivo_upload)
        
        # Processar cálculos específicos do Valencio
        calculos = processar_calculos_valencio(dados_excel)
        
        # Salvar resultado
        resultado_csv = salvar_valencio_csv(calculos, nome_original)
        
        return {
            "success": True,
            "message": f"Valencio processado: {resultado_csv['linhas']} linhas calculadas em {resultado_csv['arquivo']}",
            "dados": {
                "linhas_processadas": resultado_csv['linhas'],
                "arquivo_csv": resultado_csv['arquivo'],
                "total_calculado": calculos.get('total_geral', 0)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao processar valencio: {str(e)}",
            "dados": {}
        }

def ler_excel_valencio(arquivo_upload):
    """
    Lê Excel específico para valencio/cálculos
    """
    wb = openpyxl.load_workbook(arquivo_upload, data_only=True)
    ws = wb.active
    
    dados = []
    colunas = []
    
    primeira_linha = True
    for linha in ws.iter_rows(values_only=True):
        if not any(linha):
            continue
            
        if primeira_linha:
            colunas = [str(cel) if cel is not None else f"Coluna_{i+1}" for i, cel in enumerate(linha)]
            primeira_linha = False
            continue
            
        linha_processada = []
        for cel in linha:
            if cel is None:
                linha_processada.append("")
            elif isinstance(cel, (int, float)):
                # Converter para inteiro (sem casa decimal)
                linha_processada.append(int(cel))
            elif isinstance(cel, datetime):
                linha_processada.append(cel.strftime("%d/%m/%Y"))
            else:
                valor_str = str(cel).replace('\n', ' ').replace('\r', '').strip()
                linha_processada.append(valor_str)
        
        dados.append(linha_processada)
    
    return {
        "colunas": colunas,
        "dados": dados
    }

def processar_calculos_valencio(dados_excel):
    """
    Processa cálculos específicos do Valencio
    """
    resultados = {
        "dados_originais": dados_excel['dados'],
        "colunas": dados_excel['colunas'],
        "calculos": [],
        "total_geral": 0
    }
    
    # Procurar colunas de valores para cálculo
    colunas = dados_excel['colunas']
    col_valor = None
    
    for i, col in enumerate(colunas):
        if any(palavra in col.lower() for palavra in ['valor', 'preco', 'total', 'frete']):
            col_valor = i
            break
    
    if col_valor is not None:
        total = 0
        linhas_calculadas = 0
        
        for linha in dados_excel['dados']:
            try:
                if col_valor < len(linha) and linha[col_valor] != "":
                    valor = linha[col_valor]
                    
                    # Se já é número, usar direto como inteiro
                    if isinstance(valor, (int, float)):
                        valor_final = int(float(valor))
                    else:
                        # String: tentar converter para inteiro
                        valor_str = str(valor).replace(',', '.')
                        valor_final = int(float(valor_str))
                    
                    total += valor_final
                    linhas_calculadas += 1
                    
                    resultados['calculos'].append({
                        "linha": linha,
                        "valor": valor_final,
                        "valor_original": valor
                    })
                    
            except (ValueError, TypeError) as e:
                # Log do erro para debug
                resultados['calculos'].append({
                    "linha": linha,
                    "valor": 0,
                    "valor_original": linha[col_valor] if col_valor < len(linha) else "",
                    "erro": f"Erro conversão: {str(e)}"
                })
                continue
        
        resultados['total_geral'] = total
        resultados['linhas_calculadas'] = linhas_calculadas
    
    return resultados

def salvar_valencio_csv(calculos, nome_original):
    """
    Salva resultado dos cálculos Valencio
    """
    pasta_saida = "financeiro/uploads/valencio"
    os.makedirs(pasta_saida, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_csv = f"VALENCIO_{timestamp}_{nome_original.replace('.xlsx', '.csv')}"
    caminho_completo = os.path.join(pasta_saida, nome_csv)
    
    with open(caminho_completo, 'w', encoding='utf-8-sig', newline='') as arquivo_csv:
        writer = csv.writer(arquivo_csv, delimiter=';')
        
        # Cabeçalho com informações adicionais
        colunas_saida = calculos['colunas'] + ['VALOR_CALCULADO', 'VALOR_ORIGINAL', 'STATUS']
        writer.writerow(colunas_saida)
        
        # Adicionar linha de resumo
        writer.writerow(['=== RESUMO ===', f'Total Geral: {calculos["total_geral"]}', 
                        f'Linhas processadas: {calculos.get("linhas_calculadas", 0)}', 
                        f'Total linhas: {len(calculos["calculos"])}'])
        writer.writerow([])  # Linha vazia
        
        # Dados com cálculos e debug
        for item in calculos['calculos']:
            status = "ERRO" if "erro" in item else "OK"
            linha_saida = (item['linha'] + 
                          [item['valor'], 
                           item.get('valor_original', ''), 
                           item.get('erro', status)])
            writer.writerow(linha_saida)
    
    return {
        "arquivo": nome_csv,
        "caminho": caminho_completo,
        "linhas": len(calculos['calculos'])
    }

def validar_estrutura_valencio(dados_excel):
    """
    Valida se o arquivo tem estrutura de valencio
    """
    colunas_esperadas = ['valor', 'frete', 'preco', 'total']
    colunas_encontradas = [col.lower() for col in dados_excel['colunas']]
    
    tem_coluna_valor = any(
        any(esperada in col for esperada in colunas_esperadas) 
        for col in colunas_encontradas
    )
    
    if not tem_coluna_valor:
        return False, "Nenhuma coluna de valor/frete encontrada"
    
    return True, "Estrutura válida para cálculos"
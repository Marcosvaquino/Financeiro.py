"""
Módulo para processamento de arquivos Pamplona
Estrutura similar ao valencio.py
"""

import os
import re
import openpyxl
from datetime import datetime
import pandas as pd
import traceback


def tentar_converter_numero_brasileiro(texto):
    """
    Converte texto em número, lidando com formatos brasileiros e americanos.
    Exemplo: '1.234,56' -> 1234.56 | '1,234.56' -> 1234.56 | '1234.56' -> 1234.56
    """
    if not texto or pd.isna(texto):
        return None
    
    if isinstance(texto, (int, float)):
        return float(texto)
    
    texto_str = str(texto).strip()
    if not texto_str or texto_str.lower() in ['', 'nan', 'none']:
        return None
    
    try:
        # Remove espaços e caracteres não numéricos (exceto . , -)
        texto_limpo = re.sub(r'[^\d.,-]', '', texto_str)
        
        # Se tem vírgula como último separador decimal (formato BR)
        if ',' in texto_limpo and '.' in texto_limpo:
            # Formato: 1.234.567,89 -> remover pontos e trocar vírgula por ponto
            texto_limpo = texto_limpo.replace('.', '').replace(',', '.')
        elif ',' in texto_limpo:
            # Se só tem vírgula, assumir que é decimal brasileiro
            texto_limpo = texto_limpo.replace(',', '.')
        
        return float(texto_limpo)
    except (ValueError, TypeError):
        return None


def processar_pamplona(arquivo_upload):
    """
    Processa um arquivo Pamplona (similar ao valencio.py).
    
    Args:
        arquivo_upload: Caminho para o arquivo Excel/CSV
        
    Returns:
        dict: {"success": bool, "message": str, "detalhes": dict}
    """
    try:
        print(f"🏢 INICIANDO PROCESSAMENTO PAMPLONA: {os.path.basename(arquivo_upload)}")
        
        # Ler o arquivo Excel
        dados_excel = ler_excel_pamplona(arquivo_upload)
        
        # Processar cálculos específicos do Pamplona (implementar depois)
        resultado_calculos = processar_calculos_pamplona(dados_excel)
        
        # Salvar resultado de volta no Excel
        resultado_salvar = salvar_pamplona_csv(arquivo_upload, resultado_calculos['dados'])
        
        if resultado_salvar['success']:
            return {
                "success": True,
                "message": f"✅ PAMPLONA PROCESSADO: {resultado_calculos['message']}",
                "detalhes": {
                    "arquivo": os.path.basename(arquivo_upload),
                    "linhas_processadas": resultado_calculos.get('linhas_processadas', 0),
                    "blocos_processados": resultado_calculos.get('blocos_processados', 0)
                }
            }
        else:
            return {
                "success": False,
                "message": f"❌ ERRO AO SALVAR: {resultado_salvar['message']}",
                "detalhes": {}
            }
            
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"❌ ERRO GERAL: {str(e)}",
            "detalhes": {}
        }


def ler_excel_pamplona(arquivo_upload):
    """
    Lê o arquivo Excel do Pamplona e retorna estrutura de dados.
    """
    try:
        print(f"📖 Lendo arquivo: {os.path.basename(arquivo_upload)}")
        
        # Carregar workbook
        wb = openpyxl.load_workbook(arquivo_upload, data_only=True)
        ws = wb.active
        
        # Extrair cabeçalhos
        colunas = []
        for col in range(1, ws.max_column + 1):
            valor = ws.cell(1, col).value
            colunas.append(str(valor) if valor else f"Col_{col}")
        
        # Extrair dados
        dados = []
        for row in range(2, ws.max_row + 1):
            linha = []
            for col in range(1, ws.max_column + 1):
                valor = ws.cell(row, col).value
                # Converter datetime para string se necessário
                if isinstance(valor, datetime):
                    valor = valor.strftime('%d/%m/%Y')
                # Tentar converter números
                elif valor and isinstance(valor, str):
                    numero = tentar_converter_numero_brasileiro(valor)
                    if numero is not None:
                        valor = numero
                linha.append(valor)
            dados.append(linha)
        
        print(f"✅ Arquivo lido: {len(colunas)} colunas, {len(dados)} linhas de dados")
        
        return {
            "colunas": colunas,
            "dados": dados
        }
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        raise


def processar_calculos_pamplona(dados_excel):
    """
    Processa os cálculos específicos do Pamplona.
    
    TODO: Implementar lógica específica do Pamplona quando você me disser as regras.
    Por enquanto, apenas retorna os dados sem modificação.
    """
    try:
        print("🔄 Processando cálculos Pamplona...")
        
        # Por enquanto, apenas registra que foi chamado
        linhas_processadas = len(dados_excel["dados"])
        
        print(f"✅ Cálculos Pamplona processados: {linhas_processadas} linhas")
        
        return {
            "dados": dados_excel["dados"],
            "message": f"{linhas_processadas} linhas processadas",
            "linhas_processadas": linhas_processadas,
            "blocos_processados": 0  # Para compatibilidade
        }
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        raise


def salvar_pamplona_csv(arquivo_original, dados_processados):
    """
    Salva os dados processados de volta no arquivo Excel original.
    """
    try:
        print(f"💾 Salvando dados processados em: {os.path.basename(arquivo_original)}")
        
        # Carregar workbook original
        wb = openpyxl.load_workbook(arquivo_original, data_only=True)
        ws = wb.active
        
        # Atualizar dados (começando da linha 2, preservando cabeçalho)
        for row_idx, linha in enumerate(dados_processados, start=2):
            for col_idx, valor in enumerate(linha, start=1):
                if col_idx <= ws.max_column:
                    ws.cell(row_idx, col_idx, valor)
        
        # Salvar arquivo
        wb.save(arquivo_original)
        
        print(f"✅ Arquivo salvo com sucesso!")
        
        return {
            "success": True,
            "message": f"Arquivo salvo: {os.path.basename(arquivo_original)}"
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        
        # Tentar salvar backup em caso de erro
        try:
            backup_path = arquivo_original + ".backup"
            wb.save(backup_path)
            return {
                "success": False,
                "message": f"Erro ao salvar original, backup criado: {os.path.basename(backup_path)}"
            }
        except:
            return {
                "success": False,
                "message": f"Erro ao salvar: {str(e)}"
            }


# Função auxiliar para compatibilidade com o padrão do sistema
def processar_bloco_pamplona_real(dados_bloco):
    """
    Processa um bloco específico do Pamplona.
    TODO: Implementar lógica específica quando você definir as regras.
    """
    # Por enquanto, retorna os dados sem modificação
    return dados_bloco
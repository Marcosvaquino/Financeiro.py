"""Módulo simples de delegação de Frete.

Este arquivo fornece uma função utilitária `process_frete_file` usada por
ferramentas de automação e testes. Mantém-se pequeno e sem rota Flask
para evitar dependências desnecessárias.
"""
import os
from pathlib import Path


def process_frete_file(filepath: str) -> str:
    """Processa/delega o arquivo de frete.

    Args:
        filepath: caminho completo para o arquivo.

    Returns:
        str: caminho do arquivo gerado ou mensagem de status.
    """
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    name = p.name.lower()
    try:
        if 'valencio' in name or 'valen' in name or 'calculo' in name:
            from .valencio import processar_valencio
            res = processar_valencio(str(p))
            return res.get('arquivo_csv', res.get('message', str(res)))
        else:
            from .manifesto import processar_manifesto
            res = processar_manifesto(str(p))
            return res.get('arquivo_csv', res.get('message', str(res)))
    except Exception as e:
        return f"ERRO: {str(e)}"

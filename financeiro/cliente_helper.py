"""
Módulo auxiliar para consultas de clientes no sistema de suporte.
Usado para integração com manifestos e outras funcionalidades.
"""

import sqlite3
from typing import Dict, Optional, List
import os
import sys

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from financeiro.database import get_connection
except ImportError:
    # Fallback para conexão direta se não conseguir importar
    def get_connection():
        return sqlite3.connect('financeiro.db')

def remover_acentos(texto):
    """Remove acentos de uma string"""
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def normalizar_nome_fuzzy(nome):
    """
    Normaliza nome para comparação fuzzy: remove espaços, parênteses, acentos e converte para maiúscula
    """
    if not nome:
        return ""
    
    # Converter para string e remover acentos
    nome_str = str(nome)
    nome_sem_acento = remover_acentos(nome_str)
    
    # Remover caracteres especiais e espaços, converter para maiúscula
    nome_normalizado = nome_sem_acento.upper().replace(' ', '').replace('(', '').replace(')', '').replace('-', '').replace('_', '')
    
    return nome_normalizado

class ClienteHelper:
    """Classe para consultas otimizadas de clientes"""
    
    @staticmethod
    def buscar_cliente_por_nome_real(nome_real: str) -> Optional[Dict]:
        """
        Busca informações de um cliente pelo nome real
        
        Args:
            nome_real (str): Nome real do cliente
            
        Returns:
            Dict com dados do cliente ou None se não encontrado
        """
        if not nome_real:
            return None
            
        # Normalizar nome (sem espaços extras)
        nome_normalizado = str(nome_real).strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT nome_real, nome_ajustado, data_cadastro, ativo
                FROM clientes_suporte 
                WHERE nome_real = ? AND ativo = 1
            """, (nome_normalizado,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return {
                    'nome_real': resultado[0],
                    'nome_ajustado': resultado[1],
                    'data_cadastro': resultado[2],
                    'ativo': bool(resultado[3]),
                    'encontrado': True
                }
            else:
                return {
                    'nome_real': nome_normalizado,
                    'nome_ajustado': None,
                    'data_cadastro': None,
                    'ativo': False,
                    'encontrado': False
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar cliente {nome_real}: {e}")
            return None
    
    @staticmethod
    def buscar_cliente_por_nome_ajustado(nome_ajustado: str) -> Optional[Dict]:
        """
        Busca cliente pelo nome ajustado (mais comum em manifestos)
        
        Args:
            nome_ajustado (str): Nome ajustado do cliente
            
        Returns:
            Dict com dados do cliente ou None se não encontrado
        """
        if not nome_ajustado:
            return None
            
        # Normalizar nome ajustado (maiúscula, sem espaços)
        nome_normalizado = str(nome_ajustado).upper().strip()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT nome_real, nome_ajustado, data_cadastro, ativo
                FROM clientes_suporte 
                WHERE nome_ajustado = ? AND ativo = 1
            """, (nome_normalizado,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return {
                    'nome_real': resultado[0],
                    'nome_ajustado': resultado[1],
                    'data_cadastro': resultado[2],
                    'ativo': bool(resultado[3]),
                    'encontrado': True
                }
            else:
                return {
                    'nome_real': None,
                    'nome_ajustado': nome_normalizado,
                    'data_cadastro': None,
                    'ativo': False,
                    'encontrado': False
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar cliente por nome ajustado {nome_ajustado}: {e}")
            return None
    
    @staticmethod
    def buscar_multiplos_nomes_ajustados(nomes_ajustados: List[str]) -> Dict[str, Dict]:
        """
        Busca informações de múltiplos nomes ajustados de uma vez
        
        Args:
            nomes_ajustados (List[str]): Lista de nomes ajustados para buscar
            
        Returns:
            Dict com nome_ajustado como chave e dados como valor
        """
        if not nomes_ajustados:
            return {}
            
        # Normalizar todos os nomes
        nomes_normalizados = [str(n).upper().strip() for n in nomes_ajustados if n]
        
        if not nomes_normalizados:
            return {}
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Criar placeholders para query
            placeholders = ','.join(['?' for _ in nomes_normalizados])
            
            cursor.execute(f"""
                SELECT nome_real, nome_ajustado, data_cadastro, ativo
                FROM clientes_suporte 
                WHERE nome_ajustado IN ({placeholders}) AND ativo = 1
            """, nomes_normalizados)
            
            resultados = cursor.fetchall()
            conn.close()
            
            # Criar dicionário de resposta
            dados_encontrados = {}
            for resultado in resultados:
                dados_encontrados[resultado[1]] = {
                    'nome_real': resultado[0],
                    'nome_ajustado': resultado[1],
                    'data_cadastro': resultado[2],
                    'ativo': bool(resultado[3]),
                    'encontrado': True
                }
            
            # Adicionar nomes não encontrados
            for nome in nomes_normalizados:
                if nome not in dados_encontrados:
                    dados_encontrados[nome] = {
                        'nome_real': None,
                        'nome_ajustado': nome,
                        'data_cadastro': None,
                        'ativo': False,
                        'encontrado': False
                    }
            
            return dados_encontrados
            
        except Exception as e:
            print(f"❌ Erro ao buscar múltiplos nomes: {e}")
            return {}
    
    @staticmethod
    def get_resumo_clientes() -> Dict:
        """
        Retorna resumo dos clientes cadastrados
        
        Returns:
            Dict com estatísticas dos clientes
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Total de clientes
            cursor.execute("SELECT COUNT(*) FROM clientes_suporte")
            total_clientes = cursor.fetchone()[0]
            
            # Clientes ativos
            cursor.execute("SELECT COUNT(*) FROM clientes_suporte WHERE ativo = 1")
            clientes_ativos = cursor.fetchone()[0]
            
            # Agrupamento por nome ajustado
            cursor.execute("""
                SELECT nome_ajustado, COUNT(*) as qtd
                FROM clientes_suporte 
                WHERE ativo = 1
                GROUP BY nome_ajustado
                ORDER BY qtd DESC, nome_ajustado
            """)
            
            agrupamentos = {}
            for resultado in cursor.fetchall():
                nome_ajustado = resultado[0]
                quantidade = resultado[1]
                agrupamentos[nome_ajustado] = quantidade
            
            conn.close()
            
            resumo = {
                'total_clientes': total_clientes,
                'clientes_ativos': clientes_ativos,
                'clientes_inativos': total_clientes - clientes_ativos,
                'agrupamentos': agrupamentos,
                'tipos_unicos': len(agrupamentos)
            }
            
            return resumo
            
        except Exception as e:
            print(f"❌ Erro ao obter resumo: {e}")
            return {}
    
    @staticmethod
    def buscar_multiplos_nomes_reais(nomes_reais: List[str]) -> Dict[str, Dict]:
        """
        Busca informações de múltiplos nomes REAIS de uma vez
        (Diferente da função anterior que buscava por nome_ajustado)
        
        Args:
            nomes_reais (List[str]): Lista de nomes reais para buscar (como aparecem no manifesto)
            
        Returns:
            Dict com nome_real como chave e dados como valor
        """
        if not nomes_reais:
            return {}
            
        # Normalizar todos os nomes (manter maiúscula e sem espaços extras)
        nomes_normalizados = [str(n).upper().strip() for n in nomes_reais if n]
        
        if not nomes_normalizados:
            return {}
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Primeiro tentar busca exata
            placeholders = ','.join(['?' for _ in nomes_normalizados])
            
            cursor.execute(f"""
                SELECT nome_real, nome_ajustado, data_cadastro, ativo
                FROM clientes_suporte 
                WHERE UPPER(TRIM(nome_real)) IN ({placeholders}) AND ativo = 1
            """, nomes_normalizados)
            
            resultados_exatos = cursor.fetchall()
            
            # Criar dicionário de resposta
            dados_encontrados = {}
            nomes_encontrados = set()
            
            for resultado in resultados_exatos:
                nome_real_original = str(resultado[0]).upper().strip()
                dados_encontrados[nome_real_original] = {
                    'nome_real': resultado[0],
                    'nome_ajustado': resultado[1],
                    'data_cadastro': resultado[2],
                    'ativo': bool(resultado[3]),
                    'encontrado': True
                }
                nomes_encontrados.add(nome_real_original)
            
            # Para nomes não encontrados, tentar busca similaridade (sem acentos)
            
            nomes_nao_encontrados = [n for n in nomes_normalizados if n not in nomes_encontrados]
            
            if nomes_nao_encontrados:
                # Buscar todos os nomes da base para comparação sem acentos
                cursor.execute("SELECT nome_real, nome_ajustado FROM clientes_suporte WHERE ativo = 1")
                todos_clientes = cursor.fetchall()
                
                for nome_manifesto in nomes_nao_encontrados:
                    nome_sem_acento = remover_acentos(nome_manifesto).upper().strip()
                    
                    for cliente_real, cliente_ajustado in todos_clientes:
                        cliente_sem_acento = remover_acentos(cliente_real).upper().strip()
                        
                        if nome_sem_acento == cliente_sem_acento:
                            dados_encontrados[nome_manifesto] = {
                                'nome_real': cliente_real,
                                'nome_ajustado': cliente_ajustado,
                                'data_cadastro': None,
                                'ativo': True,
                                'encontrado': True
                            }
                            nomes_encontrados.add(nome_manifesto)
                            break
            
            # Adicionar nomes ainda não encontrados
            for nome in nomes_normalizados:
                if nome not in dados_encontrados:
                    dados_encontrados[nome] = {
                        'nome_real': nome,
                        'nome_ajustado': '0',  # Valor padrão quando não encontrado
                        'data_cadastro': None,
                        'ativo': False,
                        'encontrado': False
                    }
            
            conn.close()
            return dados_encontrados
            
        except Exception as e:
            print(f"❌ Erro ao buscar múltiplos nomes reais: {e}")
            return {}

    @staticmethod
    def mapear_nomes_manifesto(nomes_manifesto: List[str]) -> Dict[str, str]:
        """
        Mapeia nomes do manifesto para nomes ajustados conhecidos
        Útil para detectar variações de nome e normalizar
        
        Args:
            nomes_manifesto: Lista de nomes como aparecem no manifesto
            
        Returns:
            Dict mapeando nome_original -> nome_ajustado_encontrado
        """
        if not nomes_manifesto:
            return {}
        
        # Buscar exato primeiro
        dados_exatos = ClienteHelper.buscar_multiplos_nomes_ajustados(nomes_manifesto)
        
        mapeamento = {}
        nomes_nao_encontrados = []
        
        for nome_original in nomes_manifesto:
            nome_normalizado = str(nome_original).upper().strip()
            if dados_exatos.get(nome_normalizado, {}).get('encontrado', False):
                mapeamento[nome_original] = nome_normalizado
            else:
                nomes_nao_encontrados.append(nome_original)
        
        # Para nomes não encontrados, tentar busca similar
        if nomes_nao_encontrados:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Buscar todos os nomes ajustados para comparação
                cursor.execute("SELECT DISTINCT nome_ajustado FROM clientes_suporte WHERE ativo = 1")
                nomes_cadastrados = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                # Tentar encontrar similaridades
                for nome_nao_encontrado in nomes_nao_encontrados:
                    nome_upper = str(nome_nao_encontrado).upper().strip()
                    
                    # Buscar contenção parcial
                    for nome_cadastrado in nomes_cadastrados:
                        if nome_upper in nome_cadastrado or nome_cadastrado in nome_upper:
                            mapeamento[nome_nao_encontrado] = nome_cadastrado
                            break
                    
                    # Se não encontrou, marcar como não mapeado
                    if nome_nao_encontrado not in mapeamento:
                        mapeamento[nome_nao_encontrado] = None
                        
            except Exception as e:
                print(f"❌ Erro na busca similar: {e}")
                # Marcar restantes como não encontrados
                for nome in nomes_nao_encontrados:
                    if nome not in mapeamento:
                        mapeamento[nome] = None
        
        return mapeamento

    @staticmethod
    def buscar_multiplos_nomes_manifesto(nomes_manifesto: List[str]) -> Dict[str, Dict]:
        """
        Busca inteligente de clientes para dados do manifesto.
        Tenta primeiro por nome_real exato, depois por nome_ajustado, depois por busca fuzzy.
        
        Args:
            nomes_manifesto: Lista de nomes como aparecem no manifesto
            
        Returns:
            Dict com dados dos clientes encontrados (chave: nome_original_manifesto)
        """
        if not nomes_manifesto:
            return {}
        
        resultado = {}
        nomes_nao_encontrados = []
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # ETAPA 1: Buscar por nome_real exato (case-insensitive)
            for nome_manifesto in nomes_manifesto:
                nome_limpo = str(nome_manifesto).strip()
                if not nome_limpo:
                    continue
                    
                cursor.execute("""
                    SELECT nome_real, nome_ajustado, data_cadastro, ativo
                    FROM clientes_suporte 
                    WHERE UPPER(nome_real) = UPPER(?) AND ativo = 1
                """, (nome_limpo,))
                
                resultado_db = cursor.fetchone()
                if resultado_db:
                    resultado[nome_manifesto] = {
                        'nome_real': resultado_db[0],
                        'nome_ajustado': resultado_db[1],
                        'data_cadastro': resultado_db[2],
                        'ativo': bool(resultado_db[3]),
                        'encontrado': True,
                        'metodo': 'nome_real_exato'
                    }
                else:
                    nomes_nao_encontrados.append(nome_manifesto)
            
            # ETAPA 2: Para nomes não encontrados, buscar por nome_ajustado
            if nomes_nao_encontrados:
                nomes_ainda_nao_encontrados = []
                
                for nome_manifesto in nomes_nao_encontrados:
                    nome_normalizado = str(nome_manifesto).upper().strip()
                    
                    cursor.execute("""
                        SELECT nome_real, nome_ajustado, data_cadastro, ativo
                        FROM clientes_suporte 
                        WHERE UPPER(nome_ajustado) = ? AND ativo = 1
                    """, (nome_normalizado,))
                    
                    resultado_db = cursor.fetchone()
                    if resultado_db:
                        resultado[nome_manifesto] = {
                            'nome_real': resultado_db[0],
                            'nome_ajustado': resultado_db[1],
                            'data_cadastro': resultado_db[2],
                            'ativo': bool(resultado_db[3]),
                            'encontrado': True,
                            'metodo': 'nome_ajustado_exato'
                        }
                    else:
                        nomes_ainda_nao_encontrados.append(nome_manifesto)
                
                # ETAPA 3: Para nomes ainda não encontrados, buscar fuzzy (removendo espaços, parênteses, etc.)
                if nomes_ainda_nao_encontrados:
                    # Buscar todos os clientes para comparação fuzzy
                    cursor.execute("SELECT nome_real, nome_ajustado FROM clientes_suporte WHERE ativo = 1")
                    todos_clientes = cursor.fetchall()
                    
                    for nome_manifesto in nomes_ainda_nao_encontrados:
                        nome_fuzzy = normalizar_nome_fuzzy(nome_manifesto)
                        cliente_encontrado = None
                        
                        # Comparar com todos os clientes
                        for cliente_real, cliente_ajustado in todos_clientes:
                            if (normalizar_nome_fuzzy(cliente_real) == nome_fuzzy or 
                                normalizar_nome_fuzzy(cliente_ajustado) == nome_fuzzy):
                                cliente_encontrado = (cliente_real, cliente_ajustado)
                                break
                        
                        if cliente_encontrado:
                            resultado[nome_manifesto] = {
                                'nome_real': cliente_encontrado[0],
                                'nome_ajustado': cliente_encontrado[1],
                                'data_cadastro': None,
                                'ativo': True,
                                'encontrado': True,
                                'metodo': 'fuzzy_match'
                            }
                        else:
                            resultado[nome_manifesto] = {
                                'nome_real': None,
                                'nome_ajustado': nome_manifesto,
                                'data_cadastro': None,
                                'ativo': False,
                                'encontrado': False,
                                'metodo': 'nao_encontrado'
                            }
            
            conn.close()
            return resultado
            
        except Exception as e:
            print(f"❌ Erro ao buscar múltiplos nomes do manifesto: {e}")
            return {nome: {'nome_real': None, 'nome_ajustado': nome, 'encontrado': False, 'metodo': 'erro'} 
                   for nome in nomes_manifesto}

# Funções de conveniência para uso direto
def get_nome_ajustado(nome_real: str) -> Optional[str]:
    """
    Função simples para obter o nome ajustado de um cliente
    
    Args:
        nome_real (str): Nome real do cliente
        
    Returns:
        Nome ajustado ou None se não encontrado
    """
    cliente = ClienteHelper.buscar_cliente_por_nome_real(nome_real)
    return cliente['nome_ajustado'] if cliente and cliente['encontrado'] else None

def get_nome_real_por_ajustado(nome_ajustado: str) -> Optional[str]:
    """
    Função simples para obter o nome real através do nome ajustado
    
    Args:
        nome_ajustado (str): Nome ajustado do cliente
        
    Returns:
        Nome real ou None se não encontrado
    """
    cliente = ClienteHelper.buscar_cliente_por_nome_ajustado(nome_ajustado)
    return cliente['nome_real'] if cliente and cliente['encontrado'] else None

def verificar_cliente_ativo(nome_ajustado: str) -> bool:
    """
    Verifica se um cliente está ativo no sistema
    
    Args:
        nome_ajustado (str): Nome ajustado do cliente
        
    Returns:
        True se cliente está ativo, False caso contrário
    """
    cliente = ClienteHelper.buscar_cliente_por_nome_ajustado(nome_ajustado)
    return cliente['ativo'] if cliente and cliente['encontrado'] else False

# Exemplo de uso para manifesto
def enriquecer_manifesto_com_clientes(nomes_manifesto: List[str]) -> Dict:
    """
    Enriquece dados do manifesto com informações dos clientes
    
    Args:
        nomes_manifesto (List[str]): Lista de nomes de clientes do manifesto
        
    Returns:
        Dict com dados enriquecidos para cada cliente
    """
    mapeamento = ClienteHelper.mapear_nomes_manifesto(nomes_manifesto)
    dados_clientes = ClienteHelper.buscar_multiplos_nomes_ajustados(
        [nome for nome in mapeamento.values() if nome is not None]
    )
    
    resultado = {
        'clientes_encontrados': 0,
        'clientes_nao_encontrados': 0,
        'clientes_mapeados': 0,
        'dados': {},
        'mapeamento': mapeamento
    }
    
    for nome_original, nome_mapeado in mapeamento.items():
        if nome_mapeado and dados_clientes.get(nome_mapeado, {}).get('encontrado', False):
            resultado['clientes_encontrados'] += 1
            resultado['clientes_mapeados'] += 1
            resultado['dados'][nome_original] = dados_clientes[nome_mapeado]
        else:
            resultado['clientes_nao_encontrados'] += 1
            resultado['dados'][nome_original] = {
                'nome_real': None,
                'nome_ajustado': nome_original,
                'encontrado': False
            }
    
    return resultado

if __name__ == "__main__":
    # Teste rápido
    print("=== TESTE DO CLIENTE HELPER ===")
    
    # Testar busca por nome ajustado
    print("\n1. Teste busca por nome ajustado:")
    cliente_teste = ClienteHelper.buscar_cliente_por_nome_ajustado("ADORO")
    print(f"Cliente ADORO: {cliente_teste}")
    
    # Testar busca múltipla
    print("\n2. Teste busca múltipla:")
    nomes_teste = ["ADORO", "MINERVA", "CLIENTE_INEXISTENTE"]
    resultado_multiplo = ClienteHelper.buscar_multiplos_nomes_ajustados(nomes_teste)
    for nome, dados in resultado_multiplo.items():
        status = "✅ ENCONTRADO" if dados['encontrado'] else "❌ NÃO ENCONTRADO"
        print(f"  {nome}: {status} - Nome Real: {dados['nome_real']}")
    
    # Testar resumo
    print("\n3. Resumo dos clientes:")
    resumo = ClienteHelper.get_resumo_clientes()
    print(f"  Total: {resumo['total_clientes']} clientes")
    print(f"  Ativos: {resumo['clientes_ativos']}")
    print(f"  Tipos únicos: {resumo['tipos_unicos']}")
    print(f"  Agrupamentos:", list(resumo['agrupamentos'].keys())[:5], "...")
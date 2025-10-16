from flask import Blueprint, render_template, jsonify, request
import requests
import threading
import time
from datetime import datetime
import json
import sqlite3
import os

# Lock global para sincronizar acesso ao banco de dados
db_lock = threading.Lock()

bp = Blueprint('logistica', __name__, url_prefix='/logistica')

# Configurações do monitoramento
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16XYzthDIaF5oNaPSq-UO4cs09Kw_rIUR8r47rbKCV0A/export?format=csv&gid=0"
MONITORING_INTERVAL = 120  # 2 minutos em segundos
monitoring_data = {}
monitoring_active = False

def get_db_path():
    """Retorna o caminho para o banco de dados"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'financeiro.db')

def get_db_connection(timeout=30.0):
    """
    Cria uma conexão com o banco de dados com configurações otimizadas
    """
    conn = sqlite3.connect(
        get_db_path(),
        timeout=timeout,
        isolation_level=None,  # Autocommit mode
        check_same_thread=False
    )
    # Configurações para melhor concorrência
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging
    conn.execute('PRAGMA busy_timeout=30000')  # 30 segundos
    return conn

def criar_tabela_mapa_calor():
    """Cria tabela para armazenar dados do mapa de calor"""
    conn = None
    try:
        with db_lock:  # Usar lock para evitar conflitos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Tabela para armazenar uploads
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mapa_calor_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_arquivo TEXT NOT NULL,
                    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_locais INTEGER,
                    total_linhas INTEGER,
                    total_erros INTEGER,
                    ativo INTEGER DEFAULT 1
                )
            ''')
            
            # Tabela para armazenar dados processados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mapa_calor_dados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    upload_id INTEGER NOT NULL,
                    cidade TEXT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    valor REAL DEFAULT 0,
                    peso REAL DEFAULT 0,
                    FOREIGN KEY (upload_id) REFERENCES mapa_calor_uploads(id)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_upload_id ON mapa_calor_dados(upload_id)')
            
            conn.commit()
            print("✅ Tabela mapa_calor criada com sucesso")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela mapa_calor: {e}")
        return False
    finally:
        if conn:
            conn.close()

def salvar_dados_mapa_calor(nome_arquivo, dados, total_linhas, total_erros):
    """Salva dados processados no banco de dados"""
    conn = None
    try:
        with db_lock:  # Usar lock para evitar conflitos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Criar upload
            cursor.execute('''
                INSERT INTO mapa_calor_uploads (nome_arquivo, total_locais, total_linhas, total_erros)
                VALUES (?, ?, ?, ?)
            ''', (nome_arquivo, len(dados), total_linhas, total_erros))
            
            upload_id = cursor.lastrowid
            
            # Inserir dados
            for dado in dados:
                peso = dado.get('peso', 0)  # Pega peso se existir, senão usa 0
                cursor.execute('''
                    INSERT INTO mapa_calor_dados (upload_id, cidade, latitude, longitude, valor, peso)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (upload_id, dado['cidade'], dado['lat'], dado['lng'], dado['valor'], peso))
            
            conn.commit()
            
            print(f"✅ Dados salvos no banco: Upload ID {upload_id}")
            return upload_id
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados do mapa de calor: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if conn:
            conn.close()

def carregar_ultimo_mapa_calor():
    """Carrega o último upload do mapa de calor"""
    conn = None
    try:
        with db_lock:  # Usar lock para evitar conflitos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar último upload ativo
            cursor.execute('''
                SELECT id, nome_arquivo, data_upload, total_locais
                FROM mapa_calor_uploads
                WHERE ativo = 1
                ORDER BY data_upload DESC
                LIMIT 1
            ''')
            
            upload = cursor.fetchone()
            
            if not upload:
                return None
            
            upload_id = upload[0]
            
            # Buscar dados do upload
            cursor.execute('''
                SELECT cidade, latitude, longitude, valor, peso
                FROM mapa_calor_dados
                WHERE upload_id = ?
            ''', (upload_id,))
            
            dados = []
            for row in cursor.fetchall():
                dados.append({
                    'cidade': row[0],
                    'lat': row[1],
                    'lng': row[2],
                    'valor': row[3],
                    'peso': row[4] if len(row) > 4 else 0  # Compatibilidade com dados antigos
                })
            
            return {
                'upload_id': upload_id,
                'nome_arquivo': upload[1],
                'data_upload': upload[2],
                'total_locais': upload[3],
                'dados': dados
            }
        
    except Exception as e:
        print(f"❌ Erro ao carregar último mapa de calor: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_veiculo_info(placa):
    """Busca informações completas do veículo no banco de dados local"""
    conn = None
    try:
        with db_lock:  # Usar lock para evitar conflitos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar tipologia e perfil (status) da placa na tabela veiculos_suporte
            cursor.execute('''
                SELECT tipologia, status FROM veiculos_suporte 
                WHERE placa = ? AND ativo = 1
            ''', (placa,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'tipologia': resultado[0],
                    'perfil': resultado[1]
                }
            else:
                return {
                    'tipologia': None,
                    'perfil': None
                }
            
    except Exception as e:
        print(f"❌ Erro ao buscar informações da placa {placa}: {e}")
        return {
            'tipologia': None,
            'perfil': None
        }
    finally:
        if conn:
            conn.close()

def enrich_data_with_tipologia(data):
    """Enriquece os dados da planilha com tipologia e perfil do banco local"""
    encontrados = 0
    total_processados = 0
    
    for item in data:
        placa = item.get('Placa', '').strip()
        total_processados += 1
        
        if placa and placa != 'N/A' and placa != '' and placa != 'None':
            # Buscar informações completas do veículo
            veiculo_info = get_veiculo_info(placa)
            
            # Debug para primeira placa
            if total_processados == 1:
                print(f"🔍 DEBUG: Primeira placa '{placa}' -> Info: {veiculo_info}")
            
            # Adicionar tipologia
            if veiculo_info['tipologia']:
                item['Tipologia'] = veiculo_info['tipologia']
                encontrados += 1
            else:
                item['Tipologia'] = 'Não cadastrado'
            
            # Adicionar perfil
            if veiculo_info['perfil']:
                item['Perfil'] = veiculo_info['perfil']
            else:
                item['Perfil'] = 'Não cadastrado'
        else:
            item['Tipologia'] = 'Sem placa'
            item['Perfil'] = 'Sem placa'
    
    print(f"✅ Enriquecimento concluído: {encontrados}/{total_processados} placas encontradas no banco")
    return data

def init_monitoring_db():
    """Inicializa a tabela de monitoramento se não existir"""
    conn = None
    try:
        with db_lock:  # Usar lock para evitar conflitos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logistica_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data TEXT,
                    status TEXT
                )
            ''')
            
            conn.commit()
    except Exception as e:
        print(f"⚠️ Erro ao criar tabela de monitoramento: {e}")
    finally:
        if conn:
            conn.close()

def fetch_google_sheets_data():
    """Busca dados do Google Sheets"""
    try:
        import csv
        from io import StringIO
        
        response = requests.get(GOOGLE_SHEET_URL, timeout=30)
        response.raise_for_status()
        
        # Usar csv.DictReader para parsing correto
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        data = []
        for row in reader:
            data.append(row)
        
        return data
        
    except Exception as e:
        print(f"Erro ao buscar dados do Google Sheets: {e}")
        return None

def save_monitoring_data(data, status="success"):
    """Salva dados de monitoramento no banco"""
    conn = None
    try:
        with db_lock:  # Usar lock para evitar conflitos
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logistica_monitoring (data, status)
                VALUES (?, ?)
            ''', (json.dumps(data) if data else None, status))
            
            conn.commit()
        
    except Exception as e:
        print(f"Erro ao salvar dados de monitoramento: {e}")
    finally:
        if conn:
            conn.close()

def monitoring_worker():
    """Worker que executa o monitoramento a cada 2 minutos"""
    global monitoring_data, monitoring_active
    
    while monitoring_active:
        try:
            print(f"[{datetime.now()}] Buscando dados do Google Sheets...")
            data = fetch_google_sheets_data()
            
            if data:
                # Enriquecer dados com tipologia do banco local
                print("🔄 Enriquecendo dados com tipologia do banco de veículos...")
                data = enrich_data_with_tipologia(data)
                
                monitoring_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': data,
                    'status': 'success',
                    'count': len(data)
                }
                save_monitoring_data(data, "success")
                print(f"✅ Dados atualizados: {len(data)} registros")
            else:
                monitoring_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': [],
                    'status': 'error',
                    'count': 0
                }
                save_monitoring_data(None, "error")
                print("❌ Erro ao buscar dados")
                
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
            monitoring_data = {
                'timestamp': datetime.now().isoformat(),
                'data': [],
                'status': 'error',
                'count': 0,
                'error': str(e)
            }
            save_monitoring_data(None, f"error: {str(e)}")
        
        time.sleep(MONITORING_INTERVAL)

def start_monitoring():
    """Inicia o monitoramento em background"""
    global monitoring_active, monitoring_data
    
    if not monitoring_active:
        monitoring_active = True
        init_monitoring_db()
        
        # Faz uma busca inicial imediatamente
        print("🔄 Fazendo busca inicial...")
        initial_data = fetch_google_sheets_data()
        if initial_data:
            monitoring_data = {
                'timestamp': datetime.now().isoformat(),
                'data': initial_data,
                'status': 'success',
                'count': len(initial_data)
            }
            save_monitoring_data(initial_data, "success")
            print(f"✅ Busca inicial concluída: {len(initial_data)} registros")
        else:
            monitoring_data = {
                'timestamp': datetime.now().isoformat(),
                'data': [],
                'status': 'error',
                'count': 0,
                'message': 'Erro na busca inicial'
            }
            save_monitoring_data(None, "error")
            print("❌ Erro na busca inicial")
        
        # Inicia thread de monitoramento
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
        
        print("🚀 Monitoramento logístico iniciado (intervalo: 2 minutos)")

@bp.route('/')
def index():
    return render_template('logistica.html')

@bp.route('/monitoramento')
def monitoramento():
    """Página de monitoramento em tempo real"""
    # Inicia monitoramento se ainda não foi iniciado
    start_monitoring()
    
    return render_template('logistica/monitoramento.html')

@bp.route('/mapa_calor')
def mapa_calor():
    """Página de mapa de calor com importação de Excel"""
    # Criar tabela se não existir
    criar_tabela_mapa_calor()
    return render_template('logistica/mapa_calor.html')

@bp.route('/api/mapa_calor/progresso', methods=['GET'])
def api_mapa_calor_progresso():
    """API para consultar o progresso do processamento"""
    global progresso_processamento
    return jsonify(progresso_processamento)

@bp.route('/api/mapa_calor/carregar_ultimo', methods=['GET'])
def api_carregar_ultimo_mapa_calor():
    """API para carregar o último upload salvo"""
    try:
        dados = carregar_ultimo_mapa_calor()
        
        if dados:
            return jsonify({
                'status': 'success',
                'message': f'Dados carregados: {dados["nome_arquivo"]}',
                'dados': dados['dados'],
                'info': {
                    'nome_arquivo': dados['nome_arquivo'],
                    'data_upload': dados['data_upload'],
                    'total_locais': dados['total_locais']
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Nenhum dado salvo encontrado'
            }), 404
            
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/mapa_calor/poligonos', methods=['POST'])
def api_buscar_poligonos_cidades():
    """API para buscar polígonos (limites geográficos) das cidades"""
    try:
        data = request.json
        cidades = data.get('cidades', [])
        
        if not cidades:
            return jsonify({
                'status': 'error',
                'message': 'Nenhuma cidade fornecida'
            }), 400
        
        print(f"🗺️ Buscando polígonos para {len(cidades)} cidades...")
        
        poligonos = {}
        cache_file = os.path.join(os.path.dirname(__file__), 'cache_poligonos.json')
        
        # Tentar carregar cache
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except:
                cache = {}
        
        for cidade_info in cidades:
            cidade = cidade_info.get('cidade', '')
            lat = cidade_info.get('lat')
            lng = cidade_info.get('lng')
            
            if not cidade:
                continue
            
            # Verificar cache primeiro
            if cidade in cache:
                poligonos[cidade] = cache[cidade]
                continue
            
            # Buscar da API Nominatim
            try:
                # Adicionar "Brasil" para melhor precisão
                query = f"{cidade}, Brasil"
                
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'polygon_geojson': 1,
                    'limit': 1
                }
                headers = {
                    'User-Agent': 'FRZ-Logistica-MapaCalor/1.0'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=5)
                
                if response.ok:
                    results = response.json()
                    if results and len(results) > 0:
                        result = results[0]
                        if 'geojson' in result:
                            poligonos[cidade] = result['geojson']
                            cache[cidade] = result['geojson']
                            print(f"  ✅ {cidade}: polígono encontrado")
                        else:
                            print(f"  ⚠️ {cidade}: sem polígono, usando círculo")
                            poligonos[cidade] = criar_circulo_geojson(lat, lng, 5000)
                    else:
                        print(f"  ❌ {cidade}: não encontrada")
                        poligonos[cidade] = criar_circulo_geojson(lat, lng, 5000)
                
                # Respeitar rate limit da API
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Erro ao buscar {cidade}: {e}")
                if lat and lng:
                    poligonos[cidade] = criar_circulo_geojson(lat, lng, 5000)
        
        # Salvar cache atualizado
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
        
        return jsonify({
            'status': 'success',
            'poligonos': poligonos,
            'total': len(poligonos)
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar polígonos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao buscar polígonos: {str(e)}'
        }), 500

def criar_circulo_geojson(lat, lng, raio_metros=5000):
    """Cria um círculo GeoJSON aproximado como fallback"""
    import math
    
    pontos = 64
    coords = []
    
    raio_lat = raio_metros / 111000
    
    for i in range(pontos + 1):
        angulo = (i / pontos) * 2 * math.pi
        dx = raio_lat * math.cos(angulo)
        dy = (raio_metros / (111000 * math.cos(math.radians(lat)))) * math.sin(angulo)
        coords.append([lng + dy, lat + dx])
    
    return {
        'type': 'Polygon',
        'coordinates': [coords]
    }

@bp.route('/teste')
def teste_monitoramento():
    """Página de teste simples para debug"""
    from flask import send_file
    import os
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_monitoramento.html')
    return send_file(test_file)

@bp.route('/teste-direto')
def teste_direto():
    """Teste mais direto"""
    from flask import send_file
    import os
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'teste_direto.html')
    return send_file(test_file)

@bp.route('/teste-api')
def teste_api():
    """Teste específico da API"""
    from flask import send_file
    import os
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'teste_api_direto.html')
    return send_file(test_file)

@bp.route('/api/monitoramento/dados', methods=['GET', 'OPTIONS'])
def api_monitoramento_dados():
    """API para obter dados atuais do monitoramento"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    print(f"[DEBUG] monitoring_data: {monitoring_data}")
    
    # Se não há dados ainda, retorna estrutura padrão
    if not monitoring_data:
        response = jsonify({
            'timestamp': datetime.now().isoformat(),
            'data': [],
            'status': 'initializing',
            'count': 0,
            'message': 'Sistema inicializando...'
        })
    else:
        response = jsonify(monitoring_data)
    
    # Adicionar cabeçalhos CORS
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response

@bp.route('/api/monitoramento/historico', methods=['GET', 'OPTIONS'])
def api_monitoramento_historico():
    """API para obter histórico do monitoramento"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, data, status 
            FROM logistica_monitoring 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        historico = []
        for row in rows:
            data_parsed = None
            if row[1]:
                try:
                    data_parsed = json.loads(row[1])
                except:
                    pass
                    
            historico.append({
                'timestamp': row[0],
                'data': data_parsed,
                'status': row[2],
                'count': len(data_parsed) if data_parsed else 0
            })
        
        response = jsonify(historico)
        
        # Adicionar cabeçalhos CORS
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response
        
    except Exception as e:
        error_response = jsonify({'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@bp.route('/api/monitoramento/start')
def api_start_monitoring():
    """API para iniciar monitoramento"""
    start_monitoring()
    return jsonify({'status': 'started'})

# ========================================
# MAPA DE CALOR - ROTAS E APIS
# ========================================

# Variável global para armazenar progresso
progresso_processamento = {
    'total': 0,
    'atual': 0,
    'percentual': 0,
    'mensagem': '',
    'concluido': False
}

def atualizar_progresso(atual, total, mensagem=''):
    """Atualiza o progresso do processamento"""
    global progresso_processamento
    progresso_processamento['atual'] = atual
    progresso_processamento['total'] = total
    progresso_processamento['percentual'] = int((atual / total * 100)) if total > 0 else 0
    progresso_processamento['mensagem'] = mensagem
    print(f"📊 Progresso: {atual}/{total} ({progresso_processamento['percentual']}%) - {mensagem}")

def geocodificar_endereco(cidade=None, endereco=None, bairro=None, estado='SP'):
    """
    Geocodifica um endereço usando a API Nominatim (OpenStreetMap)
    Retorna (latitude, longitude) ou (None, None) se não encontrar
    """
    import time
    import urllib.parse
    import urllib.request
    
    # Construir query de busca
    queries = []
    
    # Prioridade 1: Endereço completo
    if endereco and cidade:
        query = f"{endereco}, {bairro}, {cidade}, {estado}, Brasil" if bairro else f"{endereco}, {cidade}, {estado}, Brasil"
        queries.append(query)
    
    # Prioridade 2: Bairro + Cidade
    if bairro and cidade:
        queries.append(f"{bairro}, {cidade}, {estado}, Brasil")
    
    # Prioridade 3: Apenas cidade
    if cidade:
        queries.append(f"{cidade}, {estado}, Brasil")
    
    for query in queries:
        try:
            # Codificar URL
            encoded_query = urllib.parse.quote(query)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1"
            
            # Fazer requisição (com User-Agent obrigatório)
            req = urllib.request.Request(url, headers={'User-Agent': 'FRZ-Logistica-MapaCalor/1.0'})
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    print(f"✅ Geocodificado: {query} -> ({lat}, {lon})")
                    time.sleep(1)  # Respeitar rate limit (1 req/seg)
                    return (lat, lon)
            
            time.sleep(1)  # Rate limit entre tentativas
            
        except Exception as e:
            print(f"⚠️ Erro ao geocodificar '{query}': {e}")
            continue
    
    return (None, None)

@bp.route('/api/mapa_calor/upload', methods=['POST'])
def api_upload_mapa_calor():
    """API para upload e processamento de arquivo Excel do mapa de calor"""
    try:
        print("🔵 [DEBUG] Iniciando upload...")
        
        if 'file' not in request.files:
            print("❌ [ERROR] Nenhum arquivo no request")
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        print(f"📁 [DEBUG] Arquivo recebido: {file.filename}")
        
        if file.filename == '':
            print("❌ [ERROR] Arquivo sem nome")
            return jsonify({'error': 'Arquivo sem nome'}), 400
        
        # Verificar extensão do arquivo
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            print(f"❌ [ERROR] Formato inválido: {file.filename}")
            return jsonify({'error': 'Formato inválido. Use .xlsx, .xls ou .csv'}), 400
        
        print("📦 [DEBUG] Importando bibliotecas...")
        # Processar o arquivo
        try:
            import pandas as pd
            import io
            print("✅ [DEBUG] Bibliotecas importadas")
        except ImportError as e:
            print(f"❌ [ERROR] Erro ao importar bibliotecas: {e}")
            return jsonify({'error': f'Erro ao importar bibliotecas: {str(e)}'}), 500
        
        print("📖 [DEBUG] Lendo arquivo...")
        # Ler o arquivo
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file.read()), encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(io.BytesIO(file.read()), engine='openpyxl')
            
            print(f"📊 Arquivo lido: {len(df)} linhas")
            print(f"📋 Colunas: {df.columns.tolist()}")
        except Exception as e:
            print(f"❌ [ERROR] Erro ao ler arquivo: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 500
        
        # Identificar colunas automaticamente
        colunas = df.columns.tolist()
        col_cidade = None
        col_endereco = None
        col_bairro = None
        col_estado = None
        col_lat = None
        col_lng = None
        col_valor = None
        col_peso = None
        
        for col in colunas:
            col_lower = col.lower()
            if 'cidade' in col_lower or 'city' in col_lower or 'município' in col_lower or 'municipio' in col_lower:
                col_cidade = col
            elif 'endereço' in col_lower or 'endereco' in col_lower or 'address' in col_lower or 'rua' in col_lower:
                col_endereco = col
            elif 'bairro' in col_lower or 'neighborhood' in col_lower:
                col_bairro = col
            elif 'estado' in col_lower or 'uf' in col_lower or 'state' in col_lower:
                col_estado = col
            elif 'lat' in col_lower and 'latitude' not in col_lower:
                col_lat = col
            elif 'latitude' in col_lower:
                col_lat = col
            elif 'lng' in col_lower or 'long' in col_lower:
                col_lng = col
            elif 'longitude' in col_lower:
                col_lng = col
            elif 'valor' in col_lower or 'qtd' in col_lower or 'quantidade' in col_lower or 'total' in col_lower or 'count' in col_lower:
                col_valor = col
            elif 'peso' in col_lower or 'weight' in col_lower:
                col_peso = col
        
        print(f"🔍 Colunas identificadas:")
        print(f"   Cidade: {col_cidade}")
        print(f"   Endereço: {col_endereco}")
        print(f"   Bairro: {col_bairro}")
        print(f"   Estado: {col_estado}")
        print(f"   Latitude: {col_lat}")
        print(f"   Longitude: {col_lng}")
        print(f"   Valor: {col_valor}")
        print(f"   Peso: {col_peso}")
        
        dados_processados = []
        erros = []
        
        # Cache de cidades já geocodificadas
        cache_geocoding = {}
        
        # Dicionário expandido de cidades SP
        cidades_sp_coords = {
            'SÃO PAULO': [-23.5505, -46.6333],
            'CAMPINAS': [-22.9056, -47.0608],
            'SANTOS': [-23.9618, -46.3322],
            'SÃO JOSÉ DOS CAMPOS': [-23.2237, -45.9009],
            'SOROCABA': [-23.5015, -47.4526],
            'RIBEIRÃO PRETO': [-21.1775, -47.8208],
            'GUARULHOS': [-23.4538, -46.5333],
            'SANTO ANDRÉ': [-23.6633, -46.5333],
            'OSASCO': [-23.5329, -46.7918],
            'SÃO BERNARDO DO CAMPO': [-23.6914, -46.5646],
            'MAUÁ': [-23.6700, -46.4611],
            'DIADEMA': [-23.6861, -46.6208],
            'PIRACICABA': [-22.7253, -47.6492],
            'BARUERI': [-23.5106, -46.8767],
            'ITAQUAQUECETUBA': [-23.4869, -46.3483],
            'JUNDIAÍ': [-23.1864, -46.8842],
            'TABOÃO DA SERRA': [-23.6088, -46.7575],
            'INDAIATUBA': [-23.0903, -47.2180],
            'ITAPECERICA DA SERRA': [-23.7175, -46.8492],
        }
        
        # NOVA LÓGICA: Agrupar por cidade PRIMEIRO e contar ocorrências
        print("📊 Agrupando dados por cidade...")
        
        # Criar dicionário para agrupar por cidade
        cidades_agrupadas = {}
        
        # Resetar progresso
        global progresso_processamento
        progresso_processamento = {
            'total': len(df),
            'atual': 0,
            'percentual': 0,
            'mensagem': 'Agrupando cidades...',
            'concluido': False
        }
        
        # PASSO 1: Agrupar todas as linhas por cidade
        total_linhas = len(df)
        atualizar_progresso(0, total_linhas, 'Analisando cidades...')
        
        for idx, row in df.iterrows():
            cidade = str(row[col_cidade]).strip() if col_cidade and pd.notna(row[col_cidade]) else None
            
            if cidade:
                cidade_upper = cidade.upper()
                if cidade_upper not in cidades_agrupadas:
                    cidades_agrupadas[cidade_upper] = {
                        'cidade': cidade,
                        'count': 0,
                        'peso_total': 0.0,
                        'endereco': str(row[col_endereco]).strip() if col_endereco and pd.notna(row[col_endereco]) else None,
                        'bairro': str(row[col_bairro]).strip() if col_bairro and pd.notna(row[col_bairro]) else None,
                        'estado': str(row[col_estado]).strip() if col_estado and pd.notna(row[col_estado]) else 'SP'
                    }
                cidades_agrupadas[cidade_upper]['count'] += 1
                
                # Somar peso se a coluna existir
                if col_peso and pd.notna(row[col_peso]):
                    try:
                        peso_valor = float(row[col_peso])
                        cidades_agrupadas[cidade_upper]['peso_total'] += peso_valor
                    except (ValueError, TypeError):
                        pass  # Ignora valores inválidos
        
        print(f"✅ Total de cidades únicas: {len(cidades_agrupadas)}")
        
        # Mostrar top 10 cidades
        top_cidades = sorted(cidades_agrupadas.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        print("\n🏆 Top 10 cidades com mais ocorrências:")
        for cidade, info in top_cidades:
            print(f"   {info['cidade']}: {info['count']} ocorrências")
        
        # PASSO 2: Geocodificar apenas cidades únicas
        total_cidades = len(cidades_agrupadas)
        progresso_processamento['total'] = total_cidades
        atualizar_progresso(0, total_cidades, 'Iniciando geocodificação...')
        
        idx = 0
        for cidade_upper, info in cidades_agrupadas.items():
            idx += 1
            atualizar_progresso(idx, total_cidades, f'Geocodificando: {info["cidade"][:30]}...')
            
            lat = None
            lng = None
            
            # Estratégia 1: Buscar no cache de cidades pré-cadastradas
            if cidade_upper in cidades_sp_coords:
                lat, lng = cidades_sp_coords[cidade_upper]
                print(f"✅ {info['cidade']}: Cache ({info['count']} ocorrências)")
            
            # Estratégia 2: Buscar no cache de geocoding
            elif cidade_upper in cache_geocoding:
                lat, lng = cache_geocoding[cidade_upper]
            
            # Estratégia 3: Geocodificar usando API
            else:
                lat, lng = geocodificar_endereco(
                    info['cidade'], 
                    info['endereco'], 
                    info['bairro'], 
                    info['estado']
                )
                if lat and lng:
                    cache_geocoding[cidade_upper] = (lat, lng)
                    print(f"🌍 {info['cidade']}: Geocodificado ({info['count']} ocorrências)")
            
            # Adicionar aos resultados se conseguiu coordenadas
            if lat and lng:
                dados_processados.append({
                    'cidade': info['cidade'],
                    'lat': lat,
                    'lng': lng,
                    'valor': info['count'],  # ← USAR CONTAGEM COMO VALOR
                    'peso': info.get('peso_total', 0.0)  # ← ADICIONAR PESO TOTAL
                })
            else:
                erros.append(f"{info['cidade']} ({info['count']} ocorrências)")
                print(f"❌ {info['cidade']}: Não geocodificado ({info['count']} ocorrências)")
        
        # Marcar como concluído
        progresso_processamento['concluido'] = True
        progresso_processamento['mensagem'] = 'Processamento concluído!'
        
        print(f"\n✅ Processamento concluído!")
        print(f"   Total processado: {len(dados_processados)} locais")
        print(f"   Erros: {len(erros)}")
        
        # Salvar no banco de dados
        upload_id = salvar_dados_mapa_calor(
            nome_arquivo=file.filename,
            dados=dados_processados,
            total_linhas=total_linhas,
            total_erros=len(erros)
        )
        
        return jsonify({
            'status': 'success',
            'message': f'{len(dados_processados)} locais processados com sucesso',
            'dados': dados_processados,
            'upload_id': upload_id,
            'salvo_bd': upload_id is not None,
            'erros': erros[:10],  # Primeiros 10 erros apenas
            'total_erros': len(erros),
            'colunas_encontradas': {
                'cidade': col_cidade,
                'endereco': col_endereco,
                'bairro': col_bairro,
                'latitude': col_lat,
                'longitude': col_lng,
                'valor': col_valor,
                'peso': col_peso
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Inicia automaticamente quando o módulo é carregado
start_monitoring()

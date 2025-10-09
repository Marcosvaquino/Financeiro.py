from flask import Blueprint, render_template, jsonify, request
import requests
import threading
import time
from datetime import datetime
import json
import sqlite3
import os

bp = Blueprint('logistica', __name__, url_prefix='/logistica')

# Configurações do monitoramento
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16XYzthDIaF5oNaPSq-UO4cs09Kw_rIUR8r47rbKCV0A/export?format=csv&gid=0"
MONITORING_INTERVAL = 120  # 2 minutos em segundos
monitoring_data = {}
monitoring_active = False

def get_db_path():
    """Retorna o caminho para o banco de dados"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'financeiro.db')

def init_monitoring_db():
    """Inicializa a tabela de monitoramento se não existir"""
    conn = sqlite3.connect(get_db_path())
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
    conn.close()

def fetch_google_sheets_data():
    """Busca dados do Google Sheets"""
    try:
        response = requests.get(GOOGLE_SHEET_URL, timeout=30)
        response.raise_for_status()
        
        # Processa os dados CSV
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return None
            
        headers = lines[0].split(',')
        data = []
        
        for line in lines[1:]:
            row = line.split(',')
            if len(row) >= len(headers):
                data.append(dict(zip(headers, row)))
        
        return data
        
    except Exception as e:
        print(f"Erro ao buscar dados do Google Sheets: {e}")
        return None

def save_monitoring_data(data, status="success"):
    """Salva dados de monitoramento no banco"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logistica_monitoring (data, status)
            VALUES (?, ?)
        ''', (json.dumps(data) if data else None, status))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao salvar dados de monitoramento: {e}")

def monitoring_worker():
    """Worker que executa o monitoramento a cada 2 minutos"""
    global monitoring_data, monitoring_active
    
    while monitoring_active:
        try:
            print(f"[{datetime.now()}] Buscando dados do Google Sheets...")
            data = fetch_google_sheets_data()
            
            if data:
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

# Inicia automaticamente quando o módulo é carregado
start_monitoring()

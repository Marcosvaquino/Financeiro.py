from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime
from .database import get_connection

bp = Blueprint('custo_frota', __name__, url_prefix='/frete/custo-frota')

def get_db_connection():
    """Retorna conexão com o banco de dados usando o wrapper central."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/')
def index():
    """Página principal - lista todos os custos da frota"""
    conn = get_db_connection()
    custos = conn.execute('''
        SELECT id, tipo_veiculo, custo_fixo, custo_variavel, km, dias, custo_mensal, 
               data_cadastro, ativo 
        FROM custo_frota 
        ORDER BY tipo_veiculo
    ''').fetchall()
    conn.close()
    return render_template('custo_frota.html', custos=custos)

def converter_moeda_br_para_float(valor_str):
    """Converte string em formato brasileiro (1.234,56) para float"""
    if not valor_str:
        return 0.0
    # Remove pontos de milhares e troca vírgula por ponto
    valor_limpo = valor_str.replace('.', '').replace(',', '.')
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0

def converter_numero_br_para_int(valor_str):
    """Converte string em formato brasileiro (1.234) para int"""
    if not valor_str:
        return 0
    # Remove pontos de milhares
    valor_limpo = valor_str.replace('.', '')
    try:
        return int(valor_limpo)
    except ValueError:
        return 0

@bp.route('/add', methods=['POST'])
def add_custo():
    """Adiciona um novo custo de frota"""
    tipo_veiculo = request.form.get('tipo_veiculo', '').strip().upper()
    custo_fixo_str = request.form.get('custo_fixo', '').strip()
    custo_variavel_str = request.form.get('custo_variavel', '').strip()
    km_str = request.form.get('km', '').strip()
    dias_str = request.form.get('dias', '').strip()
    custo_mensal_str = request.form.get('custo_mensal', '').strip()
    
    # Validações básicas
    if not tipo_veiculo:
        flash('Tipo de veículo é obrigatório', 'error')
        return redirect(url_for('custo_frota.index'))
    
    try:
        custo_fixo = converter_moeda_br_para_float(custo_fixo_str)
        custo_variavel = converter_moeda_br_para_float(custo_variavel_str)
        km = converter_numero_br_para_int(km_str)
        dias = int(dias_str) if dias_str else 0
        custo_mensal = converter_moeda_br_para_float(custo_mensal_str)
    except ValueError:
        flash('Valores numéricos inválidos', 'error')
        return redirect(url_for('custo_frota.index'))
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO custo_frota (tipo_veiculo, custo_fixo, custo_variavel, km, dias, custo_mensal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tipo_veiculo, custo_fixo, custo_variavel, km, dias, custo_mensal))
        conn.commit()
        flash(f'Custo para {tipo_veiculo} adicionado com sucesso', 'success')
    except sqlite3.IntegrityError:
        flash(f'Erro ao adicionar custo', 'error')
    except Exception as e:
        flash(f'Erro ao adicionar custo: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('custo_frota.index'))

@bp.route('/edit/<int:custo_id>', methods=['POST'])
def edit_custo(custo_id):
    """Edita um custo existente"""
    tipo_veiculo = request.form.get('tipo_veiculo', '').strip().upper()
    custo_fixo_str = request.form.get('custo_fixo', '').strip()
    custo_variavel_str = request.form.get('custo_variavel', '').strip()
    km_str = request.form.get('km', '').strip()
    dias_str = request.form.get('dias', '').strip()
    custo_mensal_str = request.form.get('custo_mensal', '').strip()
    ativo = request.form.get('ativo') == 'on'
    
    if not tipo_veiculo:
        flash('Tipo de veículo é obrigatório', 'error')
        return redirect(url_for('custo_frota.index'))
    
    try:
        custo_fixo = converter_moeda_br_para_float(custo_fixo_str)
        custo_variavel = converter_moeda_br_para_float(custo_variavel_str)
        km = converter_numero_br_para_int(km_str)
        dias = int(dias_str) if dias_str else 0
        custo_mensal = converter_moeda_br_para_float(custo_mensal_str)
    except ValueError:
        flash('Valores numéricos inválidos', 'error')
        return redirect(url_for('custo_frota.index'))
    
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE custo_frota 
            SET tipo_veiculo = ?, custo_fixo = ?, custo_variavel = ?, km = ?, dias = ?, 
                custo_mensal = ?, ativo = ?
            WHERE id = ?
        ''', (tipo_veiculo, custo_fixo, custo_variavel, km, dias, custo_mensal, ativo, custo_id))
        conn.commit()
        flash(f'Custo para {tipo_veiculo} atualizado com sucesso', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar custo: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('custo_frota.index'))

@bp.route('/delete/<int:custo_id>', methods=['POST'])
def delete_custo(custo_id):
    """Remove um custo"""
    conn = get_db_connection()
    try:
        # Buscar tipo do veículo para mostrar na mensagem
        custo = conn.execute('SELECT tipo_veiculo FROM custo_frota WHERE id = ?', (custo_id,)).fetchone()
        if custo:
            conn.execute('DELETE FROM custo_frota WHERE id = ?', (custo_id,))
            conn.commit()
            flash(f'Custo para {custo["tipo_veiculo"]} removido com sucesso', 'success')
        else:
            flash('Custo não encontrado', 'error')
    except Exception as e:
        flash(f'Erro ao remover custo: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('custo_frota.index'))

@bp.route('/get/<int:custo_id>')
def get_custo(custo_id):
    """API para buscar dados de um custo específico (para modal de edição)"""
    conn = get_db_connection()
    try:
        custo = conn.execute('''
            SELECT id, tipo_veiculo, custo_fixo, custo_variavel, km, dias, custo_mensal, ativo
            FROM custo_frota WHERE id = ?
        ''', (custo_id,)).fetchone()
        
        if custo:
            return jsonify({
                'id': custo['id'],
                'tipo_veiculo': custo['tipo_veiculo'],
                'custo_fixo': custo['custo_fixo'],
                'custo_variavel': custo['custo_variavel'],
                'km': custo['km'],
                'dias': custo['dias'],
                'custo_mensal': custo['custo_mensal'],
                'ativo': bool(custo['ativo'])
            })
        else:
            return jsonify({'error': 'Custo não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# === HELPER FUNCTIONS PARA INTEGRAÇÃO ===

class CustoFrotaHelper:
    """Helper para buscar custos de frota por tipologia"""
    
    @staticmethod
    def buscar_custo_por_tipologia(tipologia):
        """
        Busca custo fixo e variável por tipologia
        Retorna: {'custo_fixo': float, 'custo_variavel': float, 'encontrado': bool}
        """
        if not tipologia or tipologia.strip() == '':
            return {'custo_fixo': 0.0, 'custo_variavel': 0.0, 'encontrado': False}
        
        tipologia_norm = str(tipologia).upper().strip()
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT custo_fixo, custo_variavel 
                FROM custo_frota 
                WHERE UPPER(tipo_veiculo) = ? AND ativo = 1
                LIMIT 1
            ''', (tipologia_norm,))
            
            resultado = cursor.fetchone()
            if resultado:
                return {
                    'custo_fixo': float(resultado['custo_fixo']),
                    'custo_variavel': float(resultado['custo_variavel']),
                    'encontrado': True
                }
            else:
                return {'custo_fixo': 0.0, 'custo_variavel': 0.0, 'encontrado': False}
        except Exception as e:
            print(f"Erro ao buscar custo por tipologia {tipologia}: {e}")
            return {'custo_fixo': 0.0, 'custo_variavel': 0.0, 'encontrado': False}
        finally:
            conn.close()
    
    @staticmethod
    def calcular_custo_frota_fixa(tipologia, km):
        """
        Calcula custo frota fixa: custo_fixo + (km * custo_variavel)
        Retorna: float
        """
        if not tipologia or not km:
            return 0.0
        
        try:
            km_float = float(km)
        except (ValueError, TypeError):
            return 0.0
        
        custos = CustoFrotaHelper.buscar_custo_por_tipologia(tipologia)
        if not custos['encontrado']:
            return 0.0
        
        custo_total = custos['custo_fixo'] + (km_float * custos['custo_variavel'])
        return round(custo_total, 2)
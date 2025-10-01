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

@bp.route('/add', methods=['POST'])
def add_custo():
    """Adiciona um novo custo de frota"""
    tipo_veiculo = request.form.get('tipo_veiculo', '').strip().upper()
    custo_fixo = request.form.get('custo_fixo', '').replace(',', '.')
    custo_variavel = request.form.get('custo_variavel', '').replace(',', '.')
    km = request.form.get('km', '')
    dias = request.form.get('dias', '')
    custo_mensal = request.form.get('custo_mensal', '').replace(',', '.')
    
    # Validações básicas
    if not tipo_veiculo:
        flash('Tipo de veículo é obrigatório', 'error')
        return redirect(url_for('custo_frota.index'))
    
    try:
        custo_fixo = float(custo_fixo) if custo_fixo else 0.0
        custo_variavel = float(custo_variavel) if custo_variavel else 0.0
        km = int(km) if km else 0
        dias = int(dias) if dias else 0
        custo_mensal = float(custo_mensal) if custo_mensal else 0.0
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
    custo_fixo = request.form.get('custo_fixo', '').replace(',', '.')
    custo_variavel = request.form.get('custo_variavel', '').replace(',', '.')
    km = request.form.get('km', '')
    dias = request.form.get('dias', '')
    custo_mensal = request.form.get('custo_mensal', '').replace(',', '.')
    ativo = request.form.get('ativo') == 'on'
    
    if not tipo_veiculo:
        flash('Tipo de veículo é obrigatório', 'error')
        return redirect(url_for('custo_frota.index'))
    
    try:
        custo_fixo = float(custo_fixo) if custo_fixo else 0.0
        custo_variavel = float(custo_variavel) if custo_variavel else 0.0
        km = int(km) if km else 0
        dias = int(dias) if dias else 0
        custo_mensal = float(custo_mensal) if custo_mensal else 0.0
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
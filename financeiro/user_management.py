"""
Módulo de gestão de usuários e permissões
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .database import get_connection
import bcrypt

bp = Blueprint('user_management', __name__, url_prefix='/admin')

def require_admin():
    """Decorator para garantir que apenas admins acessem"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Verificar se é admin
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT perfil FROM usuarios WHERE id = ?", (session.get('user_id'),))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user['perfil'] != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
        return redirect(url_for('dashboard'))
    
    return None

@bp.route('/usuarios')
def usuarios():
    """Página principal de gestão de usuários"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar todos os usuários
    cursor.execute("""
        SELECT id, nome, email, perfil, criado_em 
        FROM usuarios 
        ORDER BY nome
    """)
    usuarios = cursor.fetchall()
    
    # Buscar todos os menus disponíveis
    cursor.execute("""
        SELECT id, nome, descricao, categoria, icone, ordem
        FROM menus_sistema 
        WHERE ativo = 1
        ORDER BY categoria, ordem, nome
    """)
    menus = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/usuarios.html', usuarios=usuarios, menus=menus)

@bp.route('/usuarios/criar', methods=['POST'])
def criar_usuario():
    """Criar novo usuário"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    perfil = request.form.get('perfil', 'user')
    
    if not all([nome, email, senha]):
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se email já existe
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email já está em uso'})
    
    # Criar hash da senha
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Inserir usuário
    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha_hash, perfil)
        VALUES (?, ?, ?, ?)
    """, (nome, email, senha_hash, perfil))
    
    usuario_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'message': f'Usuário {nome} criado com sucesso!',
        'usuario_id': usuario_id
    })

@bp.route('/usuarios/<int:usuario_id>/permissoes')
def get_permissoes_usuario(usuario_id):
    """Obter permissões de um usuário"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar permissões do usuário
    cursor.execute("""
        SELECT 
            m.id as menu_id,
            m.nome,
            m.descricao,
            m.categoria,
            COALESCE(up.pode_acessar, 0) as tem_acesso
        FROM menus_sistema m
        LEFT JOIN usuario_permissoes up ON m.id = up.menu_id AND up.usuario_id = ?
        WHERE m.ativo = 1
        ORDER BY m.categoria, m.ordem, m.nome
    """, (usuario_id,))
    
    permissoes = cursor.fetchall()
    conn.close()
    
    # Agrupar por categoria
    permissoes_por_categoria = {}
    for perm in permissoes:
        categoria = perm['categoria']
        if categoria not in permissoes_por_categoria:
            permissoes_por_categoria[categoria] = []
        permissoes_por_categoria[categoria].append({
            'menu_id': perm['menu_id'],
            'nome': perm['nome'],
            'descricao': perm['descricao'],
            'tem_acesso': bool(perm['tem_acesso'])
        })
    
    return jsonify({'permissoes': permissoes_por_categoria})

@bp.route('/usuarios/<int:usuario_id>/permissoes', methods=['POST'])
def salvar_permissoes_usuario(usuario_id):
    """Salvar permissões de um usuário"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    permissoes = request.json.get('permissoes', [])
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Limpar permissões existentes
        cursor.execute("DELETE FROM usuario_permissoes WHERE usuario_id = ?", (usuario_id,))
        
        # Inserir novas permissões
        for menu_id in permissoes:
            cursor.execute("""
                INSERT INTO usuario_permissoes (usuario_id, menu_id, pode_acessar)
                VALUES (?, ?, 1)
            """, (usuario_id, menu_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Permissões salvas com sucesso!'})
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Erro ao salvar permissões: {str(e)}'})

@bp.route('/usuarios/<int:usuario_id>/deletar', methods=['POST'])
def deletar_usuario(usuario_id):
    """Deletar usuário"""
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    # Não permitir deletar próprio usuário
    if usuario_id == session.get('user_id'):
        return jsonify({'success': False, 'message': 'Não é possível deletar seu próprio usuário'})
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar nome do usuário
    cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    
    if not usuario:
        conn.close()
        return jsonify({'success': False, 'message': 'Usuário não encontrado'})
    
    # Deletar usuário (CASCADE irá deletar permissões automaticamente)
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Usuário {usuario["nome"]} deletado com sucesso!'})

def get_user_permissions(user_id):
    """Função utilitária para obter permissões de um usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.rota, m.nome
        FROM menus_sistema m
        JOIN usuario_permissoes up ON m.id = up.menu_id
        WHERE up.usuario_id = ? AND up.pode_acessar = 1 AND m.ativo = 1
    """, (user_id,))
    
    permissoes = cursor.fetchall()
    conn.close()
    
    return [{'rota': p['rota'], 'nome': p['nome']} for p in permissoes]

def has_permission(user_id, rota):
    """Verificar se usuário tem permissão para acessar uma rota"""
    # Admin sempre tem todas as permissões
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT perfil FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user and user['perfil'] == 'admin':
        conn.close()
        return True
    
    # Verificar permissão específica
    cursor.execute("""
        SELECT 1
        FROM menus_sistema m
        JOIN usuario_permissoes up ON m.id = up.menu_id
        WHERE up.usuario_id = ? AND m.rota = ? AND up.pode_acessar = 1 AND m.ativo = 1
    """, (user_id, rota))
    
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado is not None
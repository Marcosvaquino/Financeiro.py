from flask import Blueprint, render_template, request, flash, redirect, url_for
import os
from .manifesto import processar_manifesto
from .valencio import processar_valencio

bp = Blueprint('upload_sistema', __name__, url_prefix='/upload')

@bp.route('/')
def index():
    return render_template('upload.html')

@bp.route('/processar', methods=['POST'])
def processar():
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo foi selecionado!')
        return redirect(url_for('upload_sistema.index'))
    
    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        flash('Nenhum arquivo foi selecionado!')
        return redirect(url_for('upload_sistema.index'))
    
    # Capturar o tipo selecionado pelo usuário
    tipo_usuario = request.form.get('tipo_arquivo', 'manifesto')
    
    # DETECÇÃO AUTOMÁTICA pelo nome do arquivo
    nome_arquivo = arquivo.filename.lower()
    tipo_detectado = None
    
    if 'manifesto' in nome_arquivo or 'manifest' in nome_arquivo:
        tipo_detectado = 'manifesto'
    elif 'valencio' in nome_arquivo or 'valen' in nome_arquivo or 'calculo' in nome_arquivo:
        tipo_detectado = 'valencio'
    
    # Verificar se há conflito entre seleção e detecção
    if tipo_detectado and tipo_detectado != tipo_usuario:
        flash(f'⚠️ ATENÇÃO: Você selecionou "{tipo_usuario.upper()}" mas o arquivo parece ser "{tipo_detectado.upper()}" (pelo nome). Processando como "{tipo_detectado.upper()}"!')
        tipo_final = tipo_detectado
    else:
        tipo_final = tipo_usuario
    
    # Por enquanto só mostra que recebeu o arquivo com o tipo
    if tipo_final == 'manifesto':
        resultado = processar_manifesto(arquivo)
        if resultado['success']:
            flash(f'✅ MANIFESTO: {resultado["message"]}')
        else:
            flash(f'❌ ERRO MANIFESTO: {resultado["message"]}')
    elif tipo_final == 'valencio':
        resultado = processar_valencio(arquivo)
        if resultado['success']:
            flash(f'✅ VALENCIO: {resultado["message"]}')
        else:
            flash(f'❌ ERRO VALENCIO: {resultado["message"]}')
    else:
        flash(f'❓ Arquivo "{arquivo.filename}" de tipo indefinido foi recebido!')
    
    return redirect(url_for('upload_sistema.index'))
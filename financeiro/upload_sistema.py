from flask import Blueprint, render_template, request, flash, redirect, url_for
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from .manifesto import processar_manifesto, extrair_mes_ano_de_arquivo

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

    # Se for manifesto, tentar extrair mês/ano e renomear antes de processar
    saved_path = None
    if tipo_final == 'manifesto':
        # Extrair mês/ano do arquivo (usa file-like)
        try:
            mes_ano = extrair_mes_ano_de_arquivo(arquivo)
        except Exception:
            mes_ano = None

        # Vamos usar o nome curto solicitado: Manifesto_Frete_{MM-YY}.xlsx
        ext = os.path.splitext(secure_filename(arquivo.filename))[1] or '.xlsx'
        novo_nome = f"Manifesto_Frete_{mes_ano}{ext}" if mes_ano else f"Manifesto_Frete_unknown{ext}"

        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'manifestos'))
        os.makedirs(uploads_dir, exist_ok=True)
        destino = os.path.join(uploads_dir, novo_nome)

        # Se existir, sobrescrevemos (usuário quer apenas um arquivo por mês)
        arquivo.stream.seek(0)
        arquivo.save(destino)
        saved_path = destino
    
    # Por enquanto só mostra que recebeu o arquivo com o tipo
    if tipo_final == 'manifesto':
        # Se salvamos o arquivo, processe pelo caminho salvo; caso contrário processe o file-like
        if saved_path:
            resultado = processar_manifesto(saved_path)
        else:
            resultado = processar_manifesto(arquivo)
        if resultado['success']:
            flash(f'✅ MANIFESTO: {resultado["message"]}')
        else:
            flash(f'❌ ERRO MANIFESTO: {resultado["message"]}')
    elif tipo_final == 'valencio':
        # Para Valencio: extrair mês/ano e renomear para Valencio_Frete_{MM-YY}
        try:
            mes_ano = extrair_mes_ano_de_arquivo(arquivo)
        except Exception:
            mes_ano = None

        ext = os.path.splitext(secure_filename(arquivo.filename))[1] or '.xlsx'
        novo_nome = f"Valencio_Frete_{mes_ano}{ext}" if mes_ano else f"Valencio_Frete_unknown{ext}"

        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'valencio'))
        os.makedirs(uploads_dir, exist_ok=True)
        destino = os.path.join(uploads_dir, novo_nome)

        # salvar (sobrescrever se necessário)
        arquivo.stream.seek(0)
        arquivo.save(destino)

        from .valencio import processar_valencio
        resultado = processar_valencio(destino)
        if resultado['success']:
            flash(f'✅ VALENCIO: {resultado["message"]}')
        else:
            flash(f'❌ ERRO VALENCIO: {resultado["message"]}')
    else:
        flash(f'❓ Arquivo "{arquivo.filename}" de tipo indefinido foi recebido!')
    
    return redirect(url_for('upload_sistema.index'))
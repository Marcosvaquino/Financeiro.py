from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
import os
from datetime import datetime

bp = Blueprint('frete', __name__, url_prefix='/frete')


@bp.route('/')
def index():
    return render_template('frete.html')


@bp.route('/importacao', methods=['GET', 'POST'])
def importacao():
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('Nenhum arquivo enviado!', 'error')
            return redirect(url_for('frete.importacao'))

        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(url_for('frete.importacao'))

        # Criar diretório de uploads do frete se não existir
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'frete'))
        os.makedirs(uploads_dir, exist_ok=True)

        for file in files:
            if file.filename:
                # Salvar arquivo temporariamente
                filepath = os.path.join(uploads_dir, file.filename)
                file.save(filepath)
                # TODO: Implementar processamento do arquivo de frete
                flash(f'{file.filename}: Arquivo salvo com sucesso! (Processamento será implementado)', 'success')

        return redirect(url_for('frete.importacao'))

    # Lista de arquivos enviados (pasta uploads/frete)
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'frete'))
    uploads = []
    if os.path.isdir(uploads_dir):
        for fname in sorted(os.listdir(uploads_dir), reverse=True):
            fpath = os.path.join(uploads_dir, fname)
            try:
                mtime = os.path.getmtime(fpath)
                size = os.path.getsize(fpath)
                uploads.append({
                    'name': fname,
                    'mtime': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': size
                })
            except Exception:
                continue

    return render_template('frete_importacao.html', uploads=uploads)


@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'frete'))
    return send_from_directory(uploads_dir, filename)

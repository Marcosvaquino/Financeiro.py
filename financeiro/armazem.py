from flask import Blueprint, render_template

bp = Blueprint('armazem', __name__, url_prefix='/armazem')


@bp.route('/')
def index():
    return render_template('armazem.html')

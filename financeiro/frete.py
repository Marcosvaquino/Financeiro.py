from flask import Blueprint, render_template

bp = Blueprint('frete', __name__, url_prefix='/frete')


@bp.route('/')
def index():
    return render_template('frete.html')

from flask import Blueprint, render_template

bp = Blueprint('logistica', __name__, url_prefix='/logistica')


@bp.route('/')
def index():
    return render_template('logistica.html')

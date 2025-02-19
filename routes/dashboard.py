from flask import Blueprint, render_template
from flask_login import login_required
from routes.auth import role_required

bp = Blueprint('dashboard', __name__)  # Corrigido __name_

@bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

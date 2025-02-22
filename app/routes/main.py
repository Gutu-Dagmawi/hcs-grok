from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Landing page route."""
    if current_user.is_authenticated:
        if current_user.user_type.value == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.user_type.value == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))
    return render_template('main/index.html') 
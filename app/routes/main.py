from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from . import main_bp

@main_bp.route('/')
@login_required
def index():
    """Landing page route."""
    if current_user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.user_type == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    elif current_user.user_type == 'patient':
        return redirect(url_for('patient.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'admin':
        return render_template('admin/dashboard.html')
    elif current_user.user_type == 'doctor':
        return render_template('doctor/dashboard.html')
    elif current_user.user_type == 'patient':
        return render_template('patient/dashboard.html')
    return render_template('dashboard.html') 
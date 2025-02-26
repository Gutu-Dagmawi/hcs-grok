from flask import render_template, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import patient_required
from . import main_bp

@main_bp.route('/')
def index():
    # If user is not logged in, show the main landing page
    if not current_user.is_authenticated:
        return render_template('main/index.html')
    
    # If user is logged in, redirect to dashboard
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Add debug logging
    current_app.logger.debug(f"User type: {current_user.user_type}")
    current_app.logger.debug(f"User: {current_user.first_name} {current_user.last_name}")
    
    # Render appropriate dashboard template based on user type
    if current_user.user_type == 'admin':
        current_app.logger.debug("Rendering admin dashboard")
        return render_template('admin/dashboard.html')
    elif current_user.user_type == 'patient':
        current_app.logger.debug("Rendering patient dashboard")
        return render_template('patient/dashboard.html')
    elif current_user.user_type == 'doctor':
        current_app.logger.debug("Rendering doctor dashboard")
        return render_template('doctor/dashboard.html')
    
    # Fallback dashboard if user type is not recognized
    current_app.logger.warning(f"Unrecognized user type: {current_user.user_type}")
    return render_template('dashboard.html')


@main_bp.route('/debug')
@login_required
@patient_required
def debug():
    debug_info = {
        'user_id': current_user.id,
        'patient_id': current_user.patient.id,
        'email': current_user.email,
        'name': f"{current_user.first_name} {current_user.last_name}",
        'qr_code_path': current_user.patient.qr_code,
        'user_type': current_user.user_type,
    }
    return jsonify(debug_info) 
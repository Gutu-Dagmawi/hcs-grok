from flask import render_template, abort
from flask_login import login_required, current_user
from . import admin_bp
from app.models import User, Patient, Doctor

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Only allow admin access
    if current_user.user_type != 'admin':
        abort(403)  # Forbidden
    return render_template('admin/dashboard.html')

@admin_bp.route('/patients')
@login_required
def patients():
    # Only allow admin access
    if current_user.user_type != 'admin':
        abort(403)  # Forbidden
    patients = Patient.query.all()
    return render_template('admin/patients.html', patients=patients)

@admin_bp.route('/doctors')
@login_required
def doctors():
    # Only allow admin access
    if current_user.user_type != 'admin':
        abort(403)  # Forbidden
    doctors = Doctor.query.all()
    return render_template('admin/doctors.html', doctors=doctors) 
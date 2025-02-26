from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.models import User
from app.extensions import db
from app.models.user import Patient, Admin, Doctor, UserType
from app.utils.qr_code import generate_qr_code
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.user_type == UserType.ADMIN:
                next_page = url_for('admin.admin_dashboard')
            elif user.user_type == UserType.DOCTOR:
                next_page = url_for('doctor.dashboard')
            else:
                next_page = url_for('main.dashboard')
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
            
        patient = Patient(
            email=email,
            name=name,
            phone=phone,
            user_type=UserType.PATIENT
        )
        patient.set_password(password)
        
        try:
            # Save patient to get ID for QR code
            db.session.add(patient)
            db.session.commit()
            
            # Generate QR code
            qr_code_path = generate_qr_code(patient.id)
            patient.qr_code = qr_code_path
            db.session.commit()
            
            # Log the user in
            login_user(patient)
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('auth.register'))
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('main.index')) 
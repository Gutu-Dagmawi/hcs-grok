from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TelField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from . import auth_bp
from app.models import User, Patient, Doctor
from app.extensions import db
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            if user.user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form_data = {}
    if request.method == 'POST':
        form_data = {
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name']
        }
        
        if request.form['password'] != request.form['confirm_password']:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html', form_data=form_data)
            
        try:
            # Check if email exists
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email address already registered', 'error')
                return render_template('auth/register.html', form_data=form_data, email_error=True)
            
            # Create user
            user = User(
                email=request.form['email'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                user_type='patient'
            )
            user.set_password(request.form['password'])
            
            # Create patient
            patient = Patient()
            user.patient = patient
            
            # Add and commit in one go
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            current_app.logger.error(f"Registration error: {str(e)}")
            return render_template('auth/register.html', form_data=form_data)
    
    return render_template('auth/register.html', form_data=form_data)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth_bp.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form_data = {
        'csrf_token': generate_csrf()  # Generate CSRF token
    }
    
    if request.method == 'POST':
        form_data = {
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'specialization': request.form['specialization'],
            'license_number': request.form['license_number'],
            'education': request.form['education'],
            'experience_years': request.form['experience_years'],
            'office_number': request.form['office_number'],
            'consultation_fee': request.form['consultation_fee']
        }
        
        if request.form['password'] != request.form['confirm_password']:
            flash('Passwords do not match', 'error')
            return render_template('auth/register_doctor.html', form_data=form_data)
            
        try:
            # Check if email exists
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email address already registered', 'error')
                return render_template('auth/register_doctor.html', form_data=form_data, email_error=True)
            
            # Create user
            user = User(
                email=request.form['email'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                user_type='doctor'
            )
            user.set_password(request.form['password'])
            
            # Create doctor profile
            doctor = Doctor(
                specialization=request.form['specialization'],
                license_number=request.form['license_number'],
                education=request.form['education'],
                experience_years=int(request.form['experience_years']),
                office_number=request.form['office_number'],
                consultation_fee=float(request.form['consultation_fee'])
            )
            user.doctor = doctor
            
            # Add and commit
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            current_app.logger.error(f"Doctor registration error: {str(e)}")
            return render_template('auth/register_doctor.html', form_data=form_data)
    
    specializations = [
        'Cardiology',
        'Dermatology',
        'Endocrinology',
        'Family Medicine',
        'Gastroenterology',
        'Neurology',
        'Obstetrics and Gynecology',
        'Oncology',
        'Ophthalmology',
        'Orthopedics',
        'Pediatrics',
        'Psychiatry',
        'Pulmonology',
        'Radiology',
        'Surgery',
        'Urology'
    ]
    
    return render_template('auth/register_doctor.html', 
                         form_data=form_data,
                         specializations=specializations)
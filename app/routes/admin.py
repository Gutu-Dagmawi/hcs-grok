from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Patient, Doctor, Admin, UserType
from app.models.medical import Appointment, MedicalRecord, Payment, AppointmentStatus, PaymentStatus
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != UserType.ADMIN:
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard route."""
    # Get counts for dashboard
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()
    total_payments = Payment.query.filter_by(status=PaymentStatus.PAID).count()
    
    # Get recent appointments
    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(5).all()
    
    # Get payment statistics
    payment_stats = {
        'total_amount': db.session.query(db.func.sum(Payment.amount))
            .filter_by(status=PaymentStatus.PAID)
            .scalar() or 0,
        'pending_amount': db.session.query(db.func.sum(Payment.amount))
            .filter_by(status=PaymentStatus.PENDING)
            .scalar() or 0
    }
    
    return render_template('admin/dashboard.html',
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_appointments=total_appointments,
                         total_payments=total_payments,
                         recent_appointments=recent_appointments,
                         payment_stats=payment_stats)

@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    """Patient management route."""
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('admin/patients.html', patients=patients)

@admin_bp.route('/patient/<int:id>')
@login_required
@admin_required
def patient_details(id):
    """Patient details route."""
    patient = Patient.query.get_or_404(id)
    return render_template('admin/patient_details.html', patient=patient)

@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    """Doctor management route."""
    doctors = Doctor.query.order_by(Doctor.created_at.desc()).all()
    return render_template('admin/doctors.html', doctors=doctors)

@admin_bp.route('/doctor/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def doctor_details(id):
    """Doctor details route."""
    doctor = Doctor.query.get_or_404(id)
    
    if request.method == 'POST':
        doctor.specialty = request.form.get('specialty')
        doctor.room_number = request.form.get('room_number')
        doctor.availability = request.form.get('availability')  # JSON string
        
        try:
            db.session.commit()
            flash('Doctor details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Update failed. Please try again.', 'error')
    
    return render_template('admin/doctor_details.html', doctor=doctor)

@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    """Appointment management route."""
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)

@admin_bp.route('/appointment/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_appointment(id):
    """Update appointment status."""
    appointment = Appointment.query.get_or_404(id)
    status = request.form.get('status')
    
    if status in [s.value for s in AppointmentStatus]:
        appointment.status = AppointmentStatus(status)
        try:
            db.session.commit()
            flash('Appointment status updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Update failed. Please try again.', 'error')
    
    return redirect(url_for('admin.appointments'))

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    """Payment management route."""
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments)

@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """Statistics and analytics route."""
    # Doctor visit statistics
    doctor_visits = db.session.query(
        Doctor.name,
        db.func.count(Appointment.id).label('visit_count')
    ).join(Appointment).group_by(Doctor.id).all()
    
    # Create a bar chart using plotly
    if doctor_visits:
        df = pd.DataFrame(doctor_visits, columns=['Doctor', 'Visits'])
        fig_visits = px.bar(df, x='Doctor', y='Visits',
                          title='Appointments by Doctor')
        doctor_chart = fig_visits.to_html(full_html=False)
    else:
        doctor_chart = None
    
    # Payment method statistics
    payment_methods = db.session.query(
        Payment.payment_method,
        db.func.count(Payment.id).label('count')
    ).group_by(Payment.payment_method).all()
    
    if payment_methods:
        df = pd.DataFrame(payment_methods, columns=['Method', 'Count'])
        fig_payments = px.pie(df, values='Count', names='Method',
                            title='Payment Methods Distribution')
        payment_chart = fig_payments.to_html(full_html=False)
    else:
        payment_chart = None
    
    return render_template('admin/statistics.html',
                         doctor_chart=doctor_chart,
                         payment_chart=payment_chart)

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    doctors = Doctor.query.join(User).all()
    return render_template('admin/dashboard.html', doctors=doctors)

@admin_bp.route('/admin/doctors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    if request.method == 'POST':
        try:
            # Create user for doctor
            new_user = User(
                email=request.form['email'],
                password=request.form['password'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                user_type='doctor'
            )
            db.session.add(new_user)
            db.session.flush()

            # Create doctor profile
            new_doctor = Doctor(
                user_id=new_user.id,
                specialization=request.form['specialization']
            )
            db.session.add(new_doctor)
            db.session.commit()
            
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding doctor: {str(e)}', 'error')
            
    return render_template('admin/add_doctor.html') 
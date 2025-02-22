from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import Doctor, UserType
from app.models.medical import Appointment, AppointmentStatus, Payment
from app.utils.payment import create_payment_record
from datetime import datetime, time

bp = Blueprint('patient', __name__, url_prefix='/patient')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Patient dashboard route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=current_user.id,
        status=AppointmentStatus.SCHEDULED
    ).order_by(Appointment.date).limit(5).all()
    
    # Get recent payments
    recent_payments = Payment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Payment.created_at.desc()).limit(5).all()
    
    return render_template('patient/dashboard.html',
                         upcoming_appointments=upcoming_appointments,
                         recent_payments=recent_payments)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Patient profile route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        current_user.emergency_contact = request.form.get('emergency_contact')
        current_user.emergency_phone = request.form.get('emergency_phone')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Profile update failed. Please try again.', 'error')
            
    return render_template('patient/profile.html')

@bp.route('/appointments')
@login_required
def appointments():
    """Patient appointments route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).all()
    
    return render_template('patient/appointments.html',
                         appointments=appointments)

@bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Book appointment route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        reason = request.form.get('reason')
        
        try:
            # Parse date and time
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            
            # Create appointment
            appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=doctor_id,
                date=date,
                time=time_obj,
                reason=reason,
                status=AppointmentStatus.SCHEDULED
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('patient.appointments'))
            
        except Exception as e:
            db.session.rollback()
            flash('Booking failed. Please try again.', 'error')
    
    # Get available doctors
    doctors = Doctor.query.all()
    return render_template('patient/book_appointment.html',
                         doctors=doctors)

@bp.route('/payments')
@login_required
def payments():
    """Patient payments route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    payments = Payment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return render_template('patient/payments.html',
                         payments=payments)

@bp.route('/pay/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def pay(appointment_id):
    """Process payment for an appointment."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('patient.payments'))
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        
        try:
            # Create payment record
            payment = create_payment_record(
                patient=current_user,
                appointment=appointment,
                amount=amount,
                payment_method=payment_method
            )
            
            flash('Payment processed successfully!', 'success')
            return redirect(url_for('patient.payments'))
            
        except Exception as e:
            flash('Payment failed. Please try again.', 'error')
    
    return render_template('patient/pay.html',
                         appointment=appointment) 
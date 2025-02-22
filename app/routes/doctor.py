from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import Doctor, UserType
from app.models.medical import Appointment, MedicalRecord, AppointmentStatus
from datetime import datetime, timedelta
import json

bp = Blueprint('doctor', __name__, url_prefix='/doctor')

def doctor_required(f):
    """Decorator to require doctor access."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != UserType.DOCTOR:
            flash('Doctor access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    """Doctor dashboard route."""
    # Get today's appointments
    today = datetime.now().date()
    todays_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        date=today
    ).order_by(Appointment.time).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date > today
    ).order_by(Appointment.date, Appointment.time).limit(5).all()
    
    return render_template('doctor/dashboard.html',
                         todays_appointments=todays_appointments,
                         upcoming_appointments=upcoming_appointments)

@bp.route('/appointments')
@login_required
@doctor_required
def appointments():
    """Doctor appointments route."""
    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).order_by(Appointment.date.desc(), Appointment.time).all()
    
    return render_template('doctor/appointments.html',
                         appointments=appointments)

@bp.route('/appointment/<int:id>', methods=['GET', 'POST'])
@login_required
@doctor_required
def appointment_details(id):
    """Appointment details and medical record route."""
    appointment = Appointment.query.get_or_404(id)
    
    if appointment.doctor_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('doctor.appointments'))
    
    if request.method == 'POST':
        # Update appointment status
        status = request.form.get('status')
        if status in [s.value for s in AppointmentStatus]:
            appointment.status = AppointmentStatus(status)
        
        # Create or update medical record
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        if not appointment.medical_record:
            medical_record = MedicalRecord(
                patient_id=appointment.patient_id,
                appointment_id=appointment.id,
                diagnosis=diagnosis,
                treatment=treatment,
                prescription=prescription,
                notes=notes
            )
            db.session.add(medical_record)
        else:
            appointment.medical_record.diagnosis = diagnosis
            appointment.medical_record.treatment = treatment
            appointment.medical_record.prescription = prescription
            appointment.medical_record.notes = notes
        
        try:
            db.session.commit()
            flash('Appointment and medical record updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Update failed. Please try again.', 'error')
    
    return render_template('doctor/appointment_details.html',
                         appointment=appointment)

@bp.route('/availability', methods=['GET', 'POST'])
@login_required
@doctor_required
def availability():
    """Doctor availability management route."""
    if request.method == 'POST':
        try:
            # Update availability schedule
            availability = json.loads(request.form.get('availability'))
            current_user.availability = availability
            db.session.commit()
            flash('Availability schedule updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Update failed. Please try again.', 'error')
    
    return render_template('doctor/availability.html') 
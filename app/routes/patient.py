from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import Doctor, UserType, User
from app.models.medical import Appointment, AppointmentStatus, Payment
from app.utils.payment import create_payment_record
from datetime import datetime, time
import qrcode
import os
import logging

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

# Add this at the top of your file with other imports
logging.basicConfig(level=logging.INFO)

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    """Patient dashboard route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    try:
        current_app.logger.info("Starting dashboard route")
        current_app.logger.info(f"User ID: {current_user.id}")
        current_app.logger.info(f"Patient info: {current_user}")
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter_by(
            patient_id=current_user.id,
            status=AppointmentStatus.SCHEDULED
        ).order_by(Appointment.date).limit(5).all()
        
        # Get recent payments
        recent_payments = Payment.query.filter_by(
            patient_id=current_user.id
        ).order_by(Payment.created_at.desc()).limit(5).all()
        
        current_app.logger.info("Rendering template")
        return render_template('patient/dashboard.html',
                             upcoming_appointments=upcoming_appointments,
                             recent_payments=recent_payments)
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        # For development only - remove in production
        raise e

@patient_bp.route('/profile', methods=['GET', 'POST'])
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

@patient_bp.route('/appointments')
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

@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Book appointment route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
        
    try:
        # Get all doctors (only users with DOCTOR type)
        doctors = User.query.filter_by(user_type=UserType.DOCTOR).all()
        
        if request.method == 'POST':
            doctor_id = request.form.get('doctor')
            date = request.form.get('date')
            time = request.form.get('time')
            reason = request.form.get('reason')
            
            if not all([doctor_id, date, time]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('patient.book_appointment'))
                
            # Create new appointment
            appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=doctor_id,
                date=datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M"),
                reason=reason,
                status=AppointmentStatus.SCHEDULED
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('patient.dashboard'))
            
        return render_template('patient/book_appointment.html', doctors=doctors)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error booking appointment: {str(e)}")
        flash('Error booking appointment. Please try again.', 'error')
        return redirect(url_for('patient.dashboard'))

@patient_bp.route('/payments')
@login_required
def payments():
    """Patient payments route."""
    if current_user.user_type != UserType.PATIENT:
        return redirect(url_for('main.index'))
    
    try:
        # Get all payments for the current patient
        payments = Payment.query.filter_by(
            patient_id=current_user.id
        ).order_by(Payment.created_at.desc()).all()
        
        return render_template('patient/payments.html', payments=payments)
    except Exception as e:
        current_app.logger.error(f"Error fetching payments: {str(e)}")
        flash('Error loading payment history', 'error')
        return redirect(url_for('patient.dashboard'))

@patient_bp.route('/pay/<int:appointment_id>', methods=['GET', 'POST'])
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

def generate_qr_code(patient):
    """Generate QR code for patient"""
    try:
        current_app.logger.info(f"Generating QR code for patient {patient.id}")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data
        data = {
            'patient_id': patient.id,
            'name': patient.name,
            'email': patient.email
        }
        qr.add_data(str(data))
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Define the file path - use forward slashes for web URLs
        filename = f'qr_codes/patient_{patient.id}.png'  # This is the path that will be stored in DB
        
        # Use os.path.join for the actual file system path
        static_path = os.path.join(current_app.static_folder, 'qr_codes', f'patient_{patient.id}.png')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(static_path), exist_ok=True)
        
        current_app.logger.info(f"Saving QR code to: {static_path}")
        
        # Save the image
        img.save(static_path)
        current_app.logger.info("QR code saved successfully")
        
        return filename  # Return the web-friendly path
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_qr_code: {str(e)}", exc_info=True)
        raise

@patient_bp.route('/fix-qr-path', methods=['GET'])
@login_required
def fix_qr_path():
    """One-time fix for QR code paths"""
    try:
        # Clear the incorrect path
        current_user.qr_code = None
        db.session.commit()
        return jsonify({'success': True, 'message': 'QR path cleared'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@patient_bp.route('/generate-qr', methods=['POST'])
@login_required
def generate_patient_qr():
    if current_user.user_type != UserType.PATIENT:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data
        data = {
            'patient_id': current_user.id,
            'name': current_user.name
        }
        qr.add_data(str(data))
        qr.make(fit=True)

        # Create and save QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        filename = f'qr_codes/patient_{current_user.id}.png'
        file_path = os.path.join(current_app.static_folder, 'qr_codes', f'patient_{current_user.id}.png')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        img.save(file_path)
        
        # Update database
        current_user.qr_code = filename
        db.session.commit()
        
        return jsonify({
            'success': True,
            'qr_code': filename
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500 
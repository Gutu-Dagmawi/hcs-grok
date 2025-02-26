from flask import jsonify, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
import os
from datetime import datetime, date, time
import qrcode
from sqlalchemy import desc, text
from sqlalchemy.orm import joinedload

from app.models.medical import Appointment
from . import patient_bp
from app.utils.decorators import patient_required
from qrcode import QRCode
from app.models import User, Patient, Doctor


@patient_bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    try:
        print("\n=== DASHBOARD DEBUG ===")
        
        # First get all appointments (like in view_appointments)
        all_appointments = (
            Appointment.query
            .filter_by(patient_id=current_user.patient.id)
            .order_by(Appointment.date.desc(), Appointment.time.desc())
            .all()
        )
        
        print(f"All appointments count: {len(all_appointments)}")
        if all_appointments:
            print("First appointment details:")
            apt = all_appointments[0]
            print(f"ID: {apt.id}")
            print(f"Date: {apt.date}")
            print(f"Time: {apt.time}")
            print(f"Status: {apt.status}")
        
        # Now get the recent appointment
        recent_appointment = (
            Appointment.query
            .filter_by(patient_id=current_user.patient.id)
            .order_by(Appointment.date.desc(), Appointment.time.desc())
            .first()
        )
        
        print("\nRecent appointment query result:")
        if recent_appointment:
            print(f"ID: {recent_appointment.id}")
            print(f"Date: {recent_appointment.date}")
            print(f"Time: {recent_appointment.time}")
            print(f"Status: {recent_appointment.status}")
        else:
            print("No recent appointment found")
            
        print("=== END DEBUG ===\n")
        
        # Pass both to template for comparison
        return render_template('patient/dashboard.html',
                             recent_appointment=recent_appointment,
                             all_appointments=all_appointments)
                             
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('patient/dashboard.html',
                             recent_appointment=None,
                             all_appointments=[])


@patient_bp.route('/generate-qr', methods=['POST'])
@login_required
@patient_required
def generate_qr():
    try:
        current_app.logger.info(f"Generating QR for user {current_user.id}")
        current_app.logger.info(f"Patient info: {current_user.patient}")
        current_app.logger.info(f"Patient ID: {current_user.patient.id if current_user.patient else 'None'}")
        
        # Ensure patient exists
        if not current_user.patient:
            current_app.logger.error(f"No patient profile for user {current_user.id}")
            return jsonify({'success': False, 'error': 'No patient profile found'})
            
        # Create QR code data with patient-specific information
        qr_data = {
            'patient_id': current_user.patient.id,
            'email': current_user.email,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Generate QR code
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure the path is relative to the static folder
        static_folder = current_app.static_folder
        qr_dir = os.path.join(static_folder, 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Delete old QR code if it exists
        if current_user.patient.qr_code:
            old_file_path = os.path.join(static_folder, current_user.patient.qr_code)
            try:
                os.remove(old_file_path)
                current_app.logger.debug(f"Deleted old QR code: {old_file_path}")
            except OSError as e:
                current_app.logger.warning(f"Could not delete old QR code: {e}")
        
        # Save QR code image with patient-specific filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'patient_qr_{current_user.patient.id}_{timestamp}.png'
        file_path = os.path.join(qr_dir, filename)
        qr_image.save(file_path)
        
        # Store the relative path in the database
        relative_path = os.path.join('qr_codes', filename).replace('\\', '/')
        
        # Force database update
        db.session.execute(
            db.update(Patient)
            .where(Patient.id == current_user.patient.id)
            .values(qr_code=relative_path)
        )
        db.session.commit()
        
        # Refresh the patient object
        db.session.refresh(current_user.patient)
        
        current_app.logger.debug(f"New QR code path: {current_user.patient.qr_code}")
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"QR generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@patient_bp.route('/appointments')
@login_required
@patient_required
def view_appointments():
    try:
        # Get all appointments for the current patient
        appointments = (
            Appointment.query
            .filter_by(patient_id=current_user.patient.id)  # Filter by current patient
            .order_by(
                Appointment.date.desc(),  # Most recent first
                Appointment.time.desc()
            )
            .all()
        )
        
        current_app.logger.info(
            f"Found {len(appointments)} appointments for patient {current_user.patient.id} "
            f"(user: {current_user.email})"
        )
        
        return render_template('patient/appointments.html', 
                             appointments=appointments)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching appointments: {str(e)}")
        flash('Error loading appointments', 'error')
        return redirect(url_for('patient.dashboard'))

@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment():
    if request.method == 'POST':
        try:
            # Get form data
            doctor_id = int(request.form.get('doctor'))
            date_str = request.form.get('date')
            time_str = request.form.get('time')
            reason = request.form.get('reason')
            
            # Validate data
            if not all([doctor_id, date_str, time_str, reason]):
                flash('Please fill all fields', 'error')
                return redirect(url_for('patient.book_appointment'))
            
            # Convert date string to date object
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Convert time string to time object
            hour, minute = map(int, time_str.split(':'))
            appointment_time = time(hour=hour, minute=minute)
            
            # Create appointment
            appointment = Appointment(
                patient_id=current_user.patient.id,
                doctor_id=doctor_id,
                date=appointment_date,
                time=appointment_time,
                reason=reason,
                status='scheduled'  # Using the correct status from model constraints
            )
            
            current_app.logger.info(f"Creating appointment: {appointment.__dict__}")
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('patient.view_appointments'))
            
        except ValueError as e:
            db.session.rollback()
            flash('Invalid date or time format', 'error')
            current_app.logger.error(f"Appointment booking error (ValueError): {str(e)}")
            return redirect(url_for('patient.book_appointment'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to book appointment. Please try again.', 'error')
            current_app.logger.error(f"Appointment booking error: {str(e)}")
            return redirect(url_for('patient.book_appointment'))
    
    return render_template('patient/book_appointment.html')

@patient_bp.route('/payments')
@login_required
@patient_required
def payments():
    return render_template('patient/payments.html')

@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def profile():
    if request.method == 'POST':
        try:
            # Update User model fields
            current_user.first_name = request.form.get('first_name')
            current_user.last_name = request.form.get('last_name')
            
            # Update Patient model fields
            current_user.patient.phone = request.form.get('phone')
            current_user.patient.address = request.form.get('address')
            current_user.patient.blood_type = request.form.get('blood_type')
            current_user.patient.gender = request.form.get('gender')
            current_user.patient.emergency_contact = request.form.get('emergency_contact')
            current_user.patient.emergency_phone = request.form.get('emergency_phone')
            
            # Handle date of birth
            dob = request.form.get('date_of_birth')
            if dob:
                current_user.patient.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile', 'error')
            current_app.logger.error(f"Profile update error: {str(e)}")
        
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/profile.html')

@patient_bp.route('/debug')
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

@patient_bp.route('/get-doctors')
@login_required
@patient_required
def get_doctors():
    try:
        doctors = Doctor.query.join(Doctor.user).all()
        doctors_list = [{
            'id': doc.id,
            'name': f"{doc.user.first_name} {doc.user.last_name}",
            'specialization': doc.specialization,
            'consultation_fee': float(doc.consultation_fee) if doc.consultation_fee else 0
        } for doc in doctors]
        return jsonify({'success': True, 'doctors': doctors_list})
    except Exception as e:
        current_app.logger.error(f"Error fetching doctors: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
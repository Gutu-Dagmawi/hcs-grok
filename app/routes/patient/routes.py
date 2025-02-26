from flask import jsonify, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
import os
from datetime import datetime
import qrcode
from . import patient_bp
from app.utils.decorators import patient_required
from qrcode import QRCode
from app.models import User

@patient_bp.route('/generate-qr', methods=['POST'])
@login_required
@patient_required
def generate_qr():
    try:
        # Create QR code data
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
            except OSError:
                pass  # File might not exist
        
        # Save QR code image with timestamp to prevent caching
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'patient_qr_{current_user.patient.id}_{timestamp}.png'
        file_path = os.path.join(qr_dir, filename)
        qr_image.save(file_path)
        
        # Store the relative path in the database
        relative_path = os.path.join('qr_codes', filename).replace('\\', '/')
        current_user.patient.qr_code = relative_path
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"QR generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@patient_bp.route('/appointments')
@login_required
@patient_required
def appointments():
    return render_template('patient/appointments.html')

@patient_bp.route('/book-appointment')
@login_required
@patient_required
def book_appointment():
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
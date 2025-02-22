import qrcode
import os
from flask import current_app
from datetime import datetime

def generate_qr_code(patient_id, save=True):
    """Generate a QR code for a patient.
    
    Args:
        patient_id: The ID of the patient.
        save: Whether to save the QR code to disk.
        
    Returns:
        str: The path to the saved QR code image or the QR code data.
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data
    data = {
        'patient_id': patient_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    qr.add_data(str(data))
    qr.make(fit=True)

    # Create an image from the QR Code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    if save:
        # Ensure the QR code directory exists
        os.makedirs(current_app.config['QR_CODE_FOLDER'], exist_ok=True)
        
        # Generate filename
        filename = f"patient_{patient_id}_qr.png"
        filepath = os.path.join(current_app.config['QR_CODE_FOLDER'], filename)
        
        # Save the image
        qr_image.save(filepath)
        
        # Return the relative path for storage in the database
        return os.path.join('static', 'qrcodes', filename)
    
    return qr_image

def verify_qr_code(qr_data):
    """Verify a QR code's data.
    
    Args:
        qr_data: The data from the scanned QR code.
        
    Returns:
        dict: The verified data or None if invalid.
    """
    try:
        # Convert string representation back to dict
        data = eval(qr_data)
        
        if isinstance(data, dict) and 'patient_id' in data:
            return data
            
    except (SyntaxError, ValueError, TypeError):
        pass
        
    return None 
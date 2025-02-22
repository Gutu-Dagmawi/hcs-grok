import uuid
from datetime import datetime
from app.models.medical import Payment, PaymentStatus

class MockPaymentGateway:
    """Mock payment gateway for simulating Telebirr and Chapa payments."""
    
    @staticmethod
    def process_telebirr_payment(amount, description=None):
        """Simulate a Telebirr payment.
        
        Args:
            amount: The payment amount.
            description: Optional payment description.
            
        Returns:
            dict: The payment response.
        """
        # Simulate payment processing
        success = amount > 0  # Simple validation
        
        return {
            'success': success,
            'transaction_id': str(uuid.uuid4()) if success else None,
            'amount': amount,
            'method': 'telebirr',
            'timestamp': datetime.utcnow().isoformat(),
            'status': PaymentStatus.PAID if success else PaymentStatus.FAILED,
            'message': 'Payment successful' if success else 'Payment failed'
        }
    
    @staticmethod
    def process_chapa_payment(amount, description=None):
        """Simulate a Chapa payment.
        
        Args:
            amount: The payment amount.
            description: Optional payment description.
            
        Returns:
            dict: The payment response.
        """
        # Simulate payment processing
        success = amount > 0  # Simple validation
        
        return {
            'success': success,
            'transaction_id': str(uuid.uuid4()) if success else None,
            'amount': amount,
            'method': 'chapa',
            'timestamp': datetime.utcnow().isoformat(),
            'status': PaymentStatus.PAID if success else PaymentStatus.FAILED,
            'message': 'Payment successful' if success else 'Payment failed'
        }

def process_payment(payment_method, amount, description=None):
    """Process a payment using the specified method.
    
    Args:
        payment_method: The payment method ('telebirr' or 'chapa').
        amount: The payment amount.
        description: Optional payment description.
        
    Returns:
        dict: The payment response.
    """
    gateway = MockPaymentGateway()
    
    if payment_method == 'telebirr':
        return gateway.process_telebirr_payment(amount, description)
    elif payment_method == 'chapa':
        return gateway.process_chapa_payment(amount, description)
    else:
        return {
            'success': False,
            'message': 'Invalid payment method'
        }

def create_payment_record(patient, appointment, amount, payment_method):
    """Create a payment record in the database.
    
    Args:
        patient: The patient model instance.
        appointment: The appointment model instance.
        amount: The payment amount.
        payment_method: The payment method used.
        
    Returns:
        Payment: The created payment record.
    """
    # Process the payment
    payment_response = process_payment(payment_method, amount)
    
    # Create payment record
    payment = Payment(
        patient_id=patient.id,
        appointment_id=appointment.id,
        amount=amount,
        status=payment_response['status'],
        payment_method=payment_method,
        transaction_id=payment_response.get('transaction_id'),
        payment_date=datetime.utcnow() if payment_response['success'] else None,
        notes=payment_response.get('message')
    )
    
    payment.save()
    return payment 
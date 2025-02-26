from app.extensions import db
from datetime import datetime
from enum import Enum
from app.models.base import Model, TimestampMixin

class AppointmentStatus(Enum):
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'

class PaymentStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Appointment(Model, TimestampMixin):
    """Appointment model."""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(
        db.String(20),
        default='scheduled',
        info={'check_constraint': "status IN ('scheduled', 'completed', 'cancelled', 'no_show')"}
    )
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    payment = db.relationship('Payment', back_populates='appointment', uselist=False)

class MedicalRecord(Model, TimestampMixin):
    """Medical Record model."""
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    attachments = db.Column(db.JSON)

class Payment(Model, TimestampMixin):
    """Payment model."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.String(20),
        default='pending',
        info={'check_constraint': "status IN ('pending', 'completed', 'failed', 'refunded')"}
    )
    payment_method = db.Column(db.String(50))
    
    appointment = db.relationship('Appointment', back_populates='payment')
    patient = db.relationship('Patient', back_populates='payments', overlaps="patient_rel") 
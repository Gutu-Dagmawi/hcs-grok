from app import db
from app.models.base import Model, TimestampMixin
import enum

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class Appointment(Model, TimestampMixin):
    """Appointment model."""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    payment = db.relationship('Payment', back_populates='appointment', uselist=False)
    medical_record = db.relationship('MedicalRecord', back_populates='appointment', uselist=False)

class MedicalRecord(Model, TimestampMixin):
    """Medical record model."""
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    attachments = db.Column(db.JSON)  # Store file paths as JSON

    # Relationships
    patient = db.relationship('Patient', back_populates='medical_records')
    appointment = db.relationship('Appointment', back_populates='medical_record')

class Payment(Model, TimestampMixin):
    """Payment model."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = db.Column(db.String(50))  # 'telebirr' or 'chapa'
    transaction_id = db.Column(db.String(100), unique=True)
    payment_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    # Relationships
    patient = db.relationship('Patient', back_populates='payments')
    appointment = db.relationship('Appointment', back_populates='payment') 
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from app.models.base import Model, TimestampMixin
from datetime import datetime
from sqlalchemy import event

class UserType(Enum):
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    ADMIN = 'admin'

class User(UserMixin, Model, TimestampMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    user_type = db.Column(db.String(20))
    
    # Relationships
    patient = db.relationship('Patient', backref='user', uselist=False, lazy=True)
    doctor = db.relationship('Doctor', backref='user', uselist=False, lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# SQLAlchemy event listener to create patient/doctor profile after user creation
@event.listens_for(User, 'after_insert')
def create_user_profile(mapper, connection, target):
    if target.user_type == 'patient':
        if not target.patient:
            patient = Patient(user_id=target.id)
            db.session.add(patient)
            db.session.commit()
    elif target.user_type == 'doctor':
        if not target.doctor:
            doctor = Doctor(user_id=target.id)
            db.session.add(doctor)
            db.session.commit()

class Doctor(Model, TimestampMixin):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialization = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    education = db.Column(db.String(255))
    experience_years = db.Column(db.Integer)
    office_number = db.Column(db.String(20))
    available_days = db.Column(db.String(100))
    consultation_fee = db.Column(db.Float)
    
    __table_args__ = (
        db.UniqueConstraint('license_number', name='uq_doctor_license_number'),
    )
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor_rel', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='doctor_rel', lazy=True)

class Patient(Model, TimestampMixin):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    qr_code = db.Column(db.String(255))
    
    # Add new fields
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    blood_type = db.Column(db.String(5))
    gender = db.Column(db.String(10))
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    
    # Existing relationships
    appointments = db.relationship('Appointment', backref='patient_rel', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='patient_rel', lazy=True)
    payments = db.relationship('Payment', back_populates='patient', overlaps="patient_rel")

class Admin(Model, TimestampMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from app.models.base import Model, TimestampMixin

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
    user_type = db.Column(
        db.String(20),
        nullable=False,
        info={'check_constraint': "user_type IN ('patient', 'doctor', 'admin')"}
    )

    # Relationships
    patient = db.relationship('Patient', backref='user', uselist=False)
    doctor = db.relationship('Doctor', backref='user', uselist=False)
    admin = db.relationship('Admin', backref='user', uselist=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Doctor(Model, TimestampMixin):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialization = db.Column(db.String(100))
    appointments = db.relationship('Appointment', backref='doctor_rel', lazy=True)

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
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from app.models.base import Model, TimestampMixin, PaginatedMixin
import enum

class UserType(enum.Enum):
    PATIENT = "patient"
    ADMIN = "admin"
    DOCTOR = "doctor"

class User(UserMixin, Model, TimestampMixin):
    """Base user model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.Enum(UserType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

class Patient(User):
    """Patient model with additional fields."""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    qr_code = db.Column(db.String(200), unique=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(200))
    blood_type = db.Column(db.String(5))
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))

    # Relationships
    appointments = db.relationship('Appointment', back_populates='patient')
    medical_records = db.relationship('MedicalRecord', back_populates='patient')
    payments = db.relationship('Payment', back_populates='patient')

    __mapper_args__ = {
        'polymorphic_identity': UserType.PATIENT,
    }

class Admin(User):
    """Admin model with additional fields."""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))

    __mapper_args__ = {
        'polymorphic_identity': UserType.ADMIN,
    }

class Doctor(User):
    """Doctor model with additional fields."""
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    availability = db.Column(db.JSON)  # Store weekly schedule as JSON
    room_number = db.Column(db.String(20))

    # Relationships
    appointments = db.relationship('Appointment', back_populates='doctor')

    __mapper_args__ = {
        'polymorphic_identity': UserType.DOCTOR,
    }

@login_manager.user_loader
def load_user(id):
    """Load a user given the ID."""
    return User.query.get(int(id)) 
from app import create_app, db
from app.models.medical import Appointment
from app.models.user import User, Patient, Doctor
from sqlalchemy import text

def inspect_database():
    app = create_app()
    with app.app_context():
        print("\n=== DATABASE INSPECTION ===")
        
        # Check Users
        users = User.query.all()
        print(f"\nUsers ({len(users)}):")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Type: {user.user_type}")
        
        # Check Patients
        patients = Patient.query.all()
        print(f"\nPatients ({len(patients)}):")
        for patient in patients:
            print(f"ID: {patient.id}, User ID: {patient.user_id}")
        
        # Check Doctors
        doctors = Doctor.query.all()
        print(f"\nDoctors ({len(doctors)}):")
        for doctor in doctors:
            print(f"ID: {doctor.id}, User ID: {doctor.user_id}")
        
        # Check Appointments
        appointments = Appointment.query.all()
        print(f"\nAppointments ({len(appointments)}):")
        for apt in appointments:
            print(f"""
Appointment:
    ID: {apt.id}
    Patient ID: {apt.patient_id}
    Doctor ID: {apt.doctor_id}
    Date: {apt.date}
    Time: {apt.time}
    Status: {apt.status}
            """)
            
        # Direct SQL query
        result = db.session.execute(text('SELECT * FROM appointments'))
        rows = result.fetchall()
        print(f"\nRaw SQL Appointments ({len(rows)}):")
        for row in rows:
            print(row)

if __name__ == "__main__":
    inspect_database() 
from app import create_app
from app.models.medical import Appointment
from app.extensions import db
from datetime import datetime

def debug_appointments():
    app = create_app()
    with app.app_context():
        try:
            # Get all appointments
            appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
            
            print("\n=== All Appointments Debug ===")
            print(f"Total appointments: {len(appointments)}\n")
            
            for apt in appointments:
                print(f"ID: {apt.id}")
                print(f"Date: {apt.date}")
                print(f"Time: {apt.time}")
                print(f"Status: {apt.status}")
                try:
                    print(f"Patient: {apt.patient.user.first_name} {apt.patient.user.last_name}")
                    print(f"Doctor: Dr. {apt.doctor.user.first_name} {apt.doctor.user.last_name}")
                except Exception as e:
                    print(f"Error getting user details: {str(e)}")
                print(f"Reason: {apt.reason or 'No reason provided'}")
                print("-" * 50)
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_appointments() 
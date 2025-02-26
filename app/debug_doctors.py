from app import create_app, db
from app.models.user import Doctor

app = create_app()
with app.app_context():
    doctors = Doctor.query.all()
    print(f"Total doctors: {len(doctors)}")
    # Print all attributes of the first doctor
    if doctors:
        doctor = doctors[0]
        print("Doctor attributes:", vars(doctor)) 
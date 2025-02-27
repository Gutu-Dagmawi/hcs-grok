from app import create_app, db
from app.models.user import User, Patient
from werkzeug.security import generate_password_hash

def seed_users():
    app = create_app()
    with app.app_context():
        # Create sample patients
        patients_data = [
            {
                'email': 'patient1@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson'
            },
            {
                'email': 'patient2@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson'
            },
            {
                'email': 'patient3@example.com',
                'first_name': 'Carol',
                'last_name': 'Brown'
            }
        ]

        for data in patients_data:
            try:
                # Check if user already exists
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user:
                    print(f"User {data['email']} already exists, skipping...")
                    continue

                # Create user
                user = User(
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    user_type='patient'
                )
                user.set_password('password123')
                db.session.add(user)
                db.session.flush()  # Get the user ID

                # Create patient with just user_id
                patient = Patient(user_id=user.id)
                db.session.add(patient)
                
                # Commit both records
                db.session.commit()
                print(f"Created patient: {data['first_name']} {data['last_name']}")

            except Exception as e:
                print(f"Error creating patient {data['email']}: {str(e)}")
                db.session.rollback()
                continue

        print("Patient seeding completed!")

        # Verify the seeding
        patients = Patient.query.all()
        print(f"\nTotal patients created: {len(patients)}")
        for patient in patients:
            user = User.query.get(patient.user_id)
            if user:
                print(f"Patient ID: {patient.id}, User: {user.email}")

if __name__ == "__main__":
    seed_users() 
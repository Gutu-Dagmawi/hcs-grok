from app import create_app, db
from app.models.user import User, Doctor
from werkzeug.security import generate_password_hash

def seed_doctors():
    app = create_app()
    with app.app_context():
        # First, clean up any incomplete doctor records
        try:
            # Find users marked as doctors but without doctor records
            doctor_users = User.query.filter_by(user_type='doctor').all()
            for user in doctor_users:
                if not Doctor.query.filter_by(user_id=user.id).first():
                    print(f"Cleaning up incomplete doctor user: {user.email}")
                    db.session.delete(user)
            db.session.commit()
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")
            db.session.rollback()

        # Create sample doctors
        doctors_data = [
            {
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'specialization': 'Cardiology',
                'license_number': 'MD12345'
            },
            {
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'specialization': 'Pediatrics',
                'license_number': 'MD67890'
            }
        ]

        for data in doctors_data:
            try:
                # Check if user or doctor already exists
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user:
                    print(f"User {data['email']} already exists, skipping...")
                    continue

                # Create both user and doctor in a single transaction
                user = User(
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    user_type='doctor'
                )
                user.set_password('password123')
                db.session.add(user)
                db.session.flush()  # Get the user ID

                doctor = Doctor(
                    user_id=user.id,
                    specialization=data['specialization'],
                    license_number=data['license_number']
                )
                db.session.add(doctor)
                
                # Commit both records
                db.session.commit()
                print(f"Created doctor: {data['first_name']} {data['last_name']}")

            except Exception as e:
                print(f"Error creating doctor {data['email']}: {str(e)}")
                db.session.rollback()
                continue

        print("Seeding completed!")

if __name__ == "__main__":
    seed_doctors() 
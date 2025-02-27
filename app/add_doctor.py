from app import create_app, db
from app.models.user import User, Doctor
import argparse

def add_doctor(email, first_name, last_name, password, specialization, license_number):
    app = create_app()
    with app.app_context():
        # Start a new session
        session = db.session()
        
        try:
            # Check if user already exists
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                print(f"Error: User with email {email} already exists")
                return False

            # Create user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type='doctor'
            )
            user.set_password(password)
            session.add(user)
            session.flush()

            # Create doctor
            doctor = Doctor(
                user_id=user.id,
                specialization=specialization,
                license_number=license_number
            )
            session.add(doctor)
            session.commit()

            print(f"""
Successfully added doctor:
    Name: Dr. {first_name} {last_name}
    Email: {email}
    Specialization: {specialization}
    License: {license_number}
            """)
            return True

        except Exception as e:
            session.rollback()
            print(f"Error adding doctor: {str(e)}")
            return False
        finally:
            session.close()

def main():
    parser = argparse.ArgumentParser(description='Add a new doctor to the system')
    parser.add_argument('--email', required=True, help='Doctor\'s email address')
    parser.add_argument('--first-name', required=True, help='Doctor\'s first name')
    parser.add_argument('--last-name', required=True, help='Doctor\'s last name')
    parser.add_argument('--password', required=True, help='Doctor\'s password')
    parser.add_argument('--specialization', required=True, help='Doctor\'s specialization')
    parser.add_argument('--license', required=True, help='Doctor\'s license number')

    args = parser.parse_args()

    add_doctor(
        email=args.email,
        first_name=args.first_name,
        last_name=args.last_name,
        password=args.password,
        specialization=args.specialization,
        license_number=args.license
    )

if __name__ == "__main__":
    main() 
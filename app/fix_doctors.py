from app import create_app, db
from app.models.user import User, Doctor

def fix_doctors():
    app = create_app()
    with app.app_context():
        print("\n=== FIXING DOCTOR RECORDS ===")
        
        # Find the user with missing doctor record
        user = User.query.filter_by(email='john.doe@example.com').first()
        
        if user:
            # Check if doctor record already exists
            existing_doctor = Doctor.query.filter_by(user_id=user.id).first()
            
            if not existing_doctor:
                try:
                    # Create the missing doctor record
                    doctor = Doctor(
                        user_id=user.id,
                        specialization='Cardiology',
                        license_number='MD12345'
                    )
                    db.session.add(doctor)
                    db.session.commit()
                    print(f"Created doctor record for {user.email}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creating doctor record: {str(e)}")
            else:
                print("Doctor record already exists")
        else:
            print("User not found")
            
        print("=== DONE ===\n")

if __name__ == "__main__":
    fix_doctors() 
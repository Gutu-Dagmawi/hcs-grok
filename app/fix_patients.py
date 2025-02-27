from app import create_app, db
from app.models.user import User, Patient
from datetime import datetime

def fix_patients():
    app = create_app()
    with app.app_context():
        print("\n=== FIXING PATIENT RECORDS ===")
        
        # First, let's print the Patient model fields
        print("Patient model fields:", Patient.__table__.columns.keys())
        
        # Get all users with type 'patient'
        patient_users = User.query.filter_by(user_type='patient').all()
        print(f"Found {len(patient_users)} users with type 'patient'")
        
        for user in patient_users:
            # Check if patient record exists
            existing_patient = Patient.query.filter_by(user_id=user.id).first()
            
            if not existing_patient:
                try:
                    # Create missing patient record with only the required fields
                    patient = Patient(
                        user_id=user.id
                    )
                    db.session.add(patient)
                    print(f"Creating patient record for {user.email}")
                except Exception as e:
                    print(f"Error creating patient record for {user.email}: {str(e)}")
                    continue
        
        try:
            db.session.commit()
            print("Successfully synced patient records!")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing changes: {str(e)}")
        
        # Verify the fix
        patients = Patient.query.all()
        print(f"\nTotal patients after fix: {len(patients)}")
        for patient in patients:
            user = User.query.get(patient.user_id)
            if user:
                print(f"Patient ID: {patient.id}, User: {user.email}")
            else:
                print(f"Patient ID: {patient.id}, No associated user found")
            
        print("=== DONE ===\n")

if __name__ == "__main__":
    fix_patients() 
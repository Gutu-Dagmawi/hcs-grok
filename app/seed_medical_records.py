from app import create_app, db
from app.models.medical import MedicalRecord
from app.models.user import Patient, Doctor
from datetime import datetime, timedelta

def seed_medical_records():
    app = create_app()
    with app.app_context():
        print("\n=== SEEDING MEDICAL RECORDS ===")
        
        # Get all patients and doctors
        patients = Patient.query.all()
        doctors = Doctor.query.all()
        
        if not patients or not doctors:
            print("No patients or doctors found. Please seed patients and doctors first.")
            return
        
        # Sample medical records data
        records_data = [
            {
                'diagnosis': 'Common Cold',
                'prescription': 'Rest and plenty of fluids. Take acetaminophen for fever.',
                'notes': 'Patient presented with runny nose and sore throat.'
            },
            {
                'diagnosis': 'Hypertension',
                'prescription': 'Prescribed lisinopril 10mg daily.',
                'notes': 'Blood pressure: 150/90. Follow up in 2 weeks.'
            },
            {
                'diagnosis': 'Seasonal Allergies',
                'prescription': 'Cetirizine 10mg daily as needed.',
                'notes': 'Patient reports seasonal allergy symptoms.'
            }
        ]

        # Create records for each patient with random doctors
        for patient in patients:
            for i, record_data in enumerate(records_data):
                try:
                    # Assign a doctor (cycling through available doctors)
                    doctor = doctors[i % len(doctors)]
                    
                    # Create record with date offset for variety
                    record = MedicalRecord(
                        patient_id=patient.id,
                        doctor_id=doctor.id,
                        diagnosis=record_data['diagnosis'],
                        prescription=record_data['prescription'],
                        notes=record_data['notes'],
                        date=datetime.utcnow() - timedelta(days=i*7)  # Spread out the dates
                    )
                    
                    db.session.add(record)
                    print(f"Created medical record for patient {patient.id} with doctor {doctor.id}")
                    
                except Exception as e:
                    print(f"Error creating medical record: {str(e)}")
                    continue
        
        try:
            db.session.commit()
            print("Successfully seeded medical records!")
            
            # Verify the seeding
            records = MedicalRecord.query.all()
            print(f"\nTotal medical records created: {len(records)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error committing records: {str(e)}")
        
        print("=== DONE ===\n")

if __name__ == "__main__":
    seed_medical_records() 
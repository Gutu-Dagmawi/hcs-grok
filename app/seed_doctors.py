from app import create_app, db
from app.models.user import Doctor

def seed_doctors():
    app = create_app()
    with app.app_context():
        # Check if doctors already exist
        if Doctor.query.count() == 0:
            doctors = [
                Doctor(
                    first_name="John",
                    last_name="Doe",
                    email="john.doe@example.com",
                    specialization="General Medicine",
                    is_active=True
                ),
                Doctor(
                    first_name="Jane",
                    last_name="Smith",
                    email="jane.smith@example.com",
                    specialization="Pediatrics",
                    is_active=True
                )
            ]
            
            db.session.add_all(doctors)
            db.session.commit()
            print("Doctors seeded successfully!")
        else:
            print("Doctors already exist in the database")

if __name__ == "__main__":
    seed_doctors() 
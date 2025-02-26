from app import create_app, db
from app.models.user import Doctor, User

app = create_app()
with app.app_context():
    # Check User table
    users = User.query.all()
    print("\n=== Users ===")
    for user in users:
        print(f"User ID: {user.id}, Data: {vars(user)}")  # This will show all fields
    
    # Check Doctor table
    doctors = Doctor.query.all()
    print("\n=== Doctors ===")
    for doctor in doctors:
        print(f"Doctor ID: {doctor.id}, Data: {vars(doctor)}")  # This will show all fields
        
        # Try to get associated user
        user = User.query.get(doctor.user_id)
        if user:
            print(f"-> Associated User ID: {user.id}")
        else:
            print("-> No associated user found!") 
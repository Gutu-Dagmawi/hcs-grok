from app import create_app, db
from app.models.user import Doctor, User

app = create_app()
with app.app_context():
    print("\n=== DATABASE DEBUG ===")
    
    # Check User table
    users = User.query.all()
    print("\n=== Users ===")
    for user in users:
        print(f"""
User:
    ID: {user.id}
    Email: {user.email}
    First Name: {user.first_name}
    Last Name: {user.last_name}
    User Type: {user.user_type}
        """)
    
    # Check Doctor table
    doctors = Doctor.query.all()
    print("\n=== Doctors ===")
    for doctor in doctors:
        print(f"""
Doctor:
    ID: {doctor.id}
    User ID: {doctor.user_id}
    Specialization: {doctor.specialization}
    License Number: {doctor.license_number}
        """)
        
        # Try to get associated user
        user = User.query.get(doctor.user_id)
        if user:
            print(f"""    Associated User:
        ID: {user.id}
        Name: {user.first_name} {user.last_name}
        Email: {user.email}
            """)
        else:
            print("    -> No associated user found!")
    
    # Check for users marked as doctors but without doctor records
    doctor_users = User.query.filter_by(user_type='doctor').all()
    print("\n=== Users marked as doctors ===")
    for user in doctor_users:
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if not doctor:
            print(f"""
Missing Doctor Record:
    User ID: {user.id}
    Email: {user.email}
    Name: {user.first_name} {user.last_name}
            """)

    print("\n=== END DEBUG ===") 
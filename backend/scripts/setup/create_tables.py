from app import app, db
from models import User, PasswordResetToken, ReadHistory

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    
    # Check if any users exist
    user_count = User.query.count()
    print(f"Number of users in database: {user_count}")
    
    if user_count == 0:
        print("No users found. You may need to register a new user.")
    else:
        print("Users found in database.") 
#!/usr/bin/env python3
"""
Reset all user passwords to 'password123'
Run this from the playwright_service directory
"""

from app import app, db
from models import User
from auth import bcrypt

def reset_passwords():
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- {user.username}")
        
        # Reset all passwords to 'password123'
        new_password = 'password123'
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        for user in users:
            user.password_hash = password_hash
            print(f"Reset password for: {user.username}")
        
        db.session.commit()
        print(f"\n✅ All {len(users)} users can now login with password: 'password123'")

if __name__ == "__main__":
    reset_passwords() 
#!/usr/bin/env python3
"""
Simple script to fix corrupted password hashes
Run this from the playwright_service directory
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import Flask app and models
from app import app, db
from models import User
from auth import bcrypt

def fix_passwords():
    """Fix corrupted password hashes by resetting all passwords to 'password123'"""
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        
        # Get all users
        users = User.query.all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"Found {len(users)} users in database.")
        
        # Reset all passwords to 'password123'
        default_password = 'password123'
        password_hash = bcrypt.generate_password_hash(default_password).decode('utf-8')
        
        for user in users:
            user.password_hash = password_hash
            print(f"Reset password for user: {user.username}")
        
        # Commit changes
        db.session.commit()
        print(f"\n✅ Successfully reset passwords for {len(users)} users.")
        print("All users can now login with username and password: 'password123'")

if __name__ == "__main__":
    fix_passwords() 
#!/usr/bin/env python3
"""
Create a new user with a known password
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User

def create_user():
    """Create a new user"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///manga_cache.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        # User details
        username = "manga_user"
        email = "manga@example.com"
        password = "manga123"  # Simple password for testing
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists!")
            return
        
        # Hash the password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            hasadmin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ User created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User ID: {new_user.id}")
        print("\n🔑 You can now log in with these credentials!")

if __name__ == '__main__':
    create_user() 
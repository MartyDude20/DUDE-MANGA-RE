#!/usr/bin/env python3
"""
Check existing reading lists
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, ReadingList

def check_reading_lists():
    """Check existing reading lists"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///manga_cache.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        print("👥 Users:")
        users = User.query.all()
        for user in users:
            print(f"  - User ID: {user.id}, Username: {user.username}")
        
        print("\n📚 Reading Lists:")
        reading_lists = ReadingList.query.all()
        for rl in reading_lists:
            print(f"  - ID: {rl.id}, User ID: {rl.user_id}, Name: {rl.name}, Description: {rl.description}")
        
        print(f"\n📊 Total reading lists: {len(reading_lists)}")

if __name__ == '__main__':
    check_reading_lists() 
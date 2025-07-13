#!/usr/bin/env python3
"""
Check database structure
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db

def check_database():
    """Check database structure"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///manga_cache.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        print("📋 Database Tables:")
        tables = inspector.get_table_names()
        for table in tables:
            print(f"  - {table}")
        
        print("\n📊 reading_lists table structure:")
        if 'reading_lists' in tables:
            columns = inspector.get_columns('reading_lists')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("  - Table does not exist")
        
        print("\n📊 users table structure:")
        if 'users' in tables:
            columns = inspector.get_columns('users')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("  - Table does not exist")

        print("\n📊 reading_progress table structure:")
        if 'reading_progress' in tables:
            columns = inspector.get_columns('reading_progress')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("  - Table does not exist")

        print("\n📊 notes table structure:")
        if 'notes' in tables:
            columns = inspector.get_columns('notes')
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")
        else:
            print("  - Table does not exist")

if __name__ == '__main__':
    check_database() 
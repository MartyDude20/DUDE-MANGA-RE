#!/usr/bin/env python3
"""
Database migration script for Dude Manga Reader
Adds new tables and columns for enhanced features
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, PasswordResetToken, ReadHistory, ReadingProgress, ReadingList, ReadingListEntry, Notification, Bookmark, Note, MangaUpdate, PreloadedManga

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///manga_cache.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def migrate_database():
    """Run database migration"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        inspector = db.inspect(db.engine)

        # Ensure all columns in Note model exist in the notes table (do this first)
        notes_columns = [col['name'] for col in inspector.get_columns('notes')]
        required_notes_columns = {
            'highlight_text': 'TEXT',
            'color': 'VARCHAR(7)',
        }
        for col, coltype in required_notes_columns.items():
            if col not in notes_columns:
                print(f"  - Adding {col} to notes table")
                with db.engine.connect() as conn:
                    conn.execute(db.text(f'ALTER TABLE notes ADD COLUMN {col} {coltype}'))
                    conn.commit()
        
        # Create all tables
        print("📋 Creating new tables...")
        db.create_all()
        
        # Add new columns to existing tables if they don't exist
        print("🔧 Adding new columns to existing tables...")
        
        # Check if new columns exist in User table
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'avatar_url' not in user_columns:
            print("  - Adding avatar_url to users table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN avatar_url VARCHAR(512)'))
                conn.commit()
        
        if 'bio' not in user_columns:
            print("  - Adding bio to users table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN bio TEXT'))
                conn.commit()
        
        if 'preferences' not in user_columns:
            print("  - Adding preferences to users table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN preferences JSON'))
                conn.commit()
        
        if 'reading_goals' not in user_columns:
            print("  - Adding reading_goals to users table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN reading_goals JSON'))
                conn.commit()
        
        if 'last_active' not in user_columns:
            print("  - Adding last_active to users table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN last_active TIMESTAMP'))
                conn.commit()
        
        # Check if new columns exist in ReadHistory table
        read_history_columns = [col['name'] for col in inspector.get_columns('read_history')]
        
        if 'reading_time' not in read_history_columns:
            print("  - Adding reading_time to read_history table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE read_history ADD COLUMN reading_time INTEGER'))
                conn.commit()
        
        if 'pages_read' not in read_history_columns:
            print("  - Adding pages_read to read_history table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE read_history ADD COLUMN pages_read INTEGER'))
                conn.commit()
        
        if 'total_pages' not in read_history_columns:
            print("  - Adding total_pages to read_history table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE read_history ADD COLUMN total_pages INTEGER'))
                conn.commit()
        
        if 'completion_percentage' not in read_history_columns:
            print("  - Adding completion_percentage to read_history table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE read_history ADD COLUMN completion_percentage FLOAT'))
                conn.commit()
        
        # Check if new columns exist in ReadingList table
        try:
            reading_list_columns = [col['name'] for col in inspector.get_columns('reading_lists')]
        except:
            reading_list_columns = []
        
        if 'description' not in reading_list_columns:
            print("  - Adding description to reading_lists table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE reading_lists ADD COLUMN description TEXT'))
                conn.commit()
        
        if 'color' not in reading_list_columns:
            print("  - Adding color to reading_lists table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE reading_lists ADD COLUMN color VARCHAR(7)'))
                conn.commit()
        
        if 'is_default' not in reading_list_columns:
            print("  - Adding is_default to reading_lists table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE reading_lists ADD COLUMN is_default BOOLEAN DEFAULT FALSE'))
                conn.commit()
        
        if 'updated_at' not in reading_list_columns:
            print("  - Adding updated_at to reading_lists table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE reading_lists ADD COLUMN updated_at TIMESTAMP'))
                conn.commit()
        
        if 'created_at' not in reading_list_columns:
            print("  - Adding created_at to reading_lists table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE reading_lists ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                conn.commit()
        
        # Check if new columns exist in ReadingProgress table
        reading_progress_columns = [col['name'] for col in inspector.get_columns('reading_progress')]
        if 'total_pages_in_chapter' not in reading_progress_columns:
            print("  - Adding total_pages_in_chapter to reading_progress table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE reading_progress ADD COLUMN total_pages_in_chapter INTEGER'))
                conn.commit()

        # Ensure all columns in ReadingProgress model exist in the reading_progress table
        required_progress_columns = {
            'chapters_read': 'INTEGER',
            'total_chapters': 'INTEGER',
            'completion_percentage': 'FLOAT',
            'started_at': 'TIMESTAMP',
            'completed_at': 'TIMESTAMP',
            'total_reading_time': 'INTEGER',
            'average_reading_speed': 'FLOAT',
        }
        for col, coltype in required_progress_columns.items():
            if col not in reading_progress_columns:
                print(f"  - Adding {col} to reading_progress table")
                with db.engine.connect() as conn:
                    conn.execute(db.text(f'ALTER TABLE reading_progress ADD COLUMN {col} {coltype}'))
                    conn.commit()

        # Fix reading_lists table: allow NULLs for manga-specific columns if they exist
        reading_lists_nullable_columns = [
            'manga_id', 'manga_title', 'source', 'added_at', 'last_updated', 'notes'
        ]
        for col in reading_lists_nullable_columns:
            if col in [c['name'] for c in inspector.get_columns('reading_lists')]:
                print(f"  - Altering {col} in reading_lists to allow NULLs")
                with db.engine.connect() as conn:
                    try:
                        conn.execute(db.text(f'ALTER TABLE reading_lists ALTER COLUMN {col} DROP NOT NULL'))
                        conn.commit()
                    except Exception as e:
                        print(f"    - Could not alter {col}: {e}")

        # Add data column to notifications table if missing
        notifications_columns = [col['name'] for col in inspector.get_columns('notifications')]
        if 'data' not in notifications_columns:
            print("  - Adding data (JSON) to notifications table")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE notifications ADD COLUMN data JSON'))
                conn.commit()

        # Create default reading lists for existing users
        print("📚 Creating default reading lists for existing users...")
        users = User.query.all()
        
        default_lists = [
            {
                'name': 'Currently Reading',
                'description': 'Manga you are currently reading',
                'color': '#3B82F6',
                'is_default': True
            },
            {
                'name': 'Plan to Read',
                'description': 'Manga you plan to read in the future',
                'color': '#10B981',
                'is_default': True
            },
            {
                'name': 'Completed',
                'description': 'Manga you have finished reading',
                'color': '#8B5CF6',
                'is_default': True
            },
            {
                'name': 'On Hold',
                'description': 'Manga you have put on hold',
                'color': '#F59E0B',
                'is_default': True
            },
            {
                'name': 'Dropped',
                'description': 'Manga you have stopped reading',
                'color': '#EF4444',
                'is_default': True
            }
        ]
        
        try:
            for user in users:
                print(f"  - Processing user: {user.username} (ID: {user.id})")
                existing_lists = ReadingList.query.filter_by(user_id=user.id).all()
                existing_list_names = [lst.name for lst in existing_lists]
                
                for list_config in default_lists:
                    if list_config['name'] not in existing_list_names:
                        reading_list = ReadingList()
                        reading_list.user_id = user.id
                        reading_list.name = list_config['name']
                        reading_list.description = list_config['description']
                        reading_list.color = list_config['color']
                        reading_list.is_default = list_config['is_default']
                        db.session.add(reading_list)
                        print(f"    - Created '{list_config['name']}' list for user {user.username}")
            db.session.commit()
        except Exception as e:
            print(f"❌ Exception while creating reading lists: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
        
        print("✅ Database migration completed successfully!")
        
        # Print summary (commented out to avoid ORM metadata issues)
        # print("\n📊 Migration Summary:")
        # print(f"  - Users: {User.query.count()}")
        # print(f"  - Reading Lists: {ReadingList.query.count()}")
        # print(f"  - Reading Progress: {ReadingProgress.query.count()}")
        # print(f"  - Notifications: {Notification.query.count()}")
        # print(f"  - Bookmarks: {Bookmark.query.count()}")
        # print(f"  - Notes: {Note.query.count()}")
        # print(f"  - Manga Updates: {MangaUpdate.query.count()}")

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1) 
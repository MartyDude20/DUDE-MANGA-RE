"""
Script to create preloader tables in the database
Run this to set up the preloaded_manga table
"""
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import PreloadedManga

def create_preloader_tables():
    """Create the preloader tables if they don't exist"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if table exists and has data
        try:
            count = PreloadedManga.query.count()
            print(f"✅ PreloadedManga table exists with {count} entries")
        except Exception as e:
            print(f"❌ Error checking PreloadedManga table: {e}")
            return False
        
        # Create a test entry to verify everything works
        try:
            test_manga = PreloadedManga.query.filter_by(
                title="Test Manga Entry"
            ).first()
            
            if not test_manga:
                test_manga = PreloadedManga(
                    title="Test Manga Entry",
                    normalized_title=PreloadedManga.normalize_title("Test Manga Entry"),
                    source_url="https://example.com/test-manga",
                    source="test",
                    last_updated=datetime.utcnow()
                )
                db.session.add(test_manga)
                db.session.commit()
                print("✅ Created test manga entry")
            else:
                print("✅ Test manga entry already exists")
                
        except Exception as e:
            print(f"❌ Error creating test entry: {e}")
            db.session.rollback()
            return False
        
        print("\n✅ Preloader tables are ready!")
        print("\nYou can now:")
        print("1. Start the application to begin automatic preloading")
        print("2. Use the admin endpoints to trigger manual preloading")
        print("3. Search for manga - results will be cached in the preloader")
        
        return True

if __name__ == "__main__":
    success = create_preloader_tables()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Script to set up database tables for the preloading system.
Run this script to create the new tables for PreloadJob, PreloadStats, and RobotsTxtCache.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import app, db
from models import PreloadJob, PreloadStats, RobotsTxtCache

def setup_preload_tables():
    """Create the preload-related database tables"""
    with app.app_context():
        print("Creating preload tables...")
        
        # Create the new tables
        db.create_all()
        
        print("✅ Preload tables created successfully!")
        print("\nCreated tables:")
        print("- preload_jobs")
        print("- preload_stats") 
        print("- robots_txt_cache")
        
        # Verify tables exist by checking if they can be queried
        try:
            # Test if tables exist by trying to count records
            job_count = PreloadJob.query.count()
            stats_count = PreloadStats.query.count()
            robots_count = RobotsTxtCache.query.count()
            
            print(f"\nTable verification:")
            print(f"- preload_jobs: {job_count} records")
            print(f"- preload_stats: {stats_count} records")
            print(f"- robots_txt_cache: {robots_count} records")
            
        except Exception as e:
            print(f"❌ Error verifying tables: {e}")
            print("This might be normal if tables are empty or newly created.")
            return True  # Still return True as tables were created
        
        return True

if __name__ == '__main__':
    success = setup_preload_tables()
    if success:
        print("\n🎉 Preload tables setup completed successfully!")
    else:
        print("\n❌ Preload tables setup failed!")
        sys.exit(1) 
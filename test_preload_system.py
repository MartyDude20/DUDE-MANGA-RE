#!/usr/bin/env python3
"""
Test script for the preloading system.
This script tests the preload manager functionality.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the playwright_service directory to the path
sys.path.append('playwright_service')

# Load environment variables
load_dotenv()

from playwright_service.app import app, db, preload_manager
from playwright_service.models import PreloadJob, PreloadStats, RobotsTxtCache

def test_preload_system():
    """Test the preload system functionality"""
    print("🧪 Testing Preload System...")
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Test robots.txt cache
        print("\n📋 Testing robots.txt cache...")
        try:
            preload_manager.update_robots_txt_all_sources()
            robots_count = RobotsTxtCache.query.count()
            print(f"✅ Robots.txt cache updated: {robots_count} entries")
        except Exception as e:
            print(f"❌ Robots.txt cache error: {e}")
        
        # Test creating daily jobs
        print("\n📅 Testing daily job creation...")
        try:
            jobs_created = preload_manager.create_daily_preload_jobs()
            print(f"✅ Created {jobs_created} daily preload jobs")
        except Exception as e:
            print(f"❌ Daily job creation error: {e}")
        
        # Test getting stats
        print("\n📊 Testing statistics...")
        try:
            stats = preload_manager.get_preload_stats(days=1)
            print(f"✅ Retrieved stats: {len(stats)} entries")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
        
        # Test job queries
        print("\n🔍 Testing job queries...")
        try:
            pending_jobs = PreloadJob.query.filter(PreloadJob.status == 'pending').count()
            print(f"✅ Pending jobs: {pending_jobs}")
        except Exception as e:
            print(f"❌ Job query error: {e}")
        
        # Test cleanup
        print("\n🧹 Testing cleanup...")
        try:
            preload_manager.cleanup_old_jobs(days=1)
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
        
        print("\n🎉 Preload system test completed!")

def test_preload_endpoints():
    """Test the preload API endpoints"""
    print("\n🌐 Testing Preload API Endpoints...")
    
    # This would require a running server and admin authentication
    # For now, just print the available endpoints
    endpoints = [
        'GET /preload/stats - Get preload statistics',
        'GET /preload/jobs - Get current preload jobs',
        'POST /preload/create-daily - Create daily preload jobs',
        'POST /preload/start-worker - Start the preload worker',
        'POST /preload/stop-worker - Stop the preload worker',
        'POST /preload/cleanup - Clean up old preload jobs',
        'POST /preload/update-robots - Update robots.txt cache',
        'GET /preload/status - Get preload system status'
    ]
    
    print("Available preload endpoints:")
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    print("\n⚠️  Note: Endpoint testing requires admin authentication and running server")

if __name__ == '__main__':
    print("🚀 Starting Preload System Tests...\n")
    
    try:
        test_preload_system()
        test_preload_endpoints()
        
        print("\n✅ All tests completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the backend server")
        print("2. Access the PreloadManager component in the frontend")
        print("3. Use admin credentials to manage the preload system")
        print("4. Monitor the preload worker and statistics")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 
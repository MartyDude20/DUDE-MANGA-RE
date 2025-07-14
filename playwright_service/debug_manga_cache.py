#!/usr/bin/env python3
"""
Debug script to track manga details cache operations
"""

import sqlite3
import json
import time
import requests
from datetime import datetime
from typing import Dict, Optional

def check_database_cache():
    """Check the current state of the manga cache database"""
    print("=== DATABASE CACHE ANALYSIS ===")
    
    try:
        with sqlite3.connect("manga_cache.db") as conn:
            cursor = conn.cursor()
            
            # Check manga_cache table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manga_cache'")
            if cursor.fetchone():
                print("✓ manga_cache table exists")
                
                # Get all manga cache entries
                cursor.execute("""
                    SELECT user_id, manga_id, source, title, last_updated, last_refreshed 
                    FROM manga_cache 
                    ORDER BY last_updated DESC 
                    LIMIT 10
                """)
                
                entries = cursor.fetchall()
                print(f"\nFound {len(entries)} manga cache entries:")
                for entry in entries:
                    user_id, manga_id, source, title, last_updated, last_refreshed = entry
                    print(f"  - User: {user_id}, ID: {manga_id}, Source: {source}, Title: {title}")
                    print(f"    Updated: {last_updated}, Refreshed: {last_refreshed}")
            else:
                print("✗ manga_cache table does not exist")
            
            # Check search_cache table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_cache'")
            if cursor.fetchone():
                print("\n✓ search_cache table exists")
                
                cursor.execute("SELECT COUNT(*) FROM search_cache")
                search_count = cursor.fetchone()[0]
                print(f"  - {search_count} search cache entries")
            else:
                print("\n✗ search_cache table does not exist")
                
    except Exception as e:
        print(f"Error checking database: {e}")

def test_manga_details_request(manga_id: str, source: str = "weebcentral"):
    """Test manga details request and track cache behavior"""
    print(f"\n=== TESTING MANGA DETAILS REQUEST ===")
    print(f"Manga ID: {manga_id}")
    print(f"Source: {source}")
    
    # First request - should be fresh
    print("\n1. First request (should be fresh):")
    start_time = time.time()
    
    try:
        response = requests.get(f"http://localhost:5000/manga/{source}/{manga_id}")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success ({duration:.2f}s)")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Cached: {data.get('cached', 'N/A')}")
            print(f"  Chapters: {len(data.get('chapters', []))}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return
    
    # Check cache after first request
    print("\n2. Checking cache after first request:")
    check_specific_cache(manga_id, source)
    
    # Second request - should be cached
    print("\n3. Second request (should be cached):")
    start_time = time.time()
    
    try:
        response = requests.get(f"http://localhost:5000/manga/{source}/{manga_id}")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success ({duration:.2f}s)")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Cached: {data.get('cached', 'N/A')}")
            print(f"  Chapters: {len(data.get('chapters', []))}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
    
    # Check cache after second request
    print("\n4. Checking cache after second request:")
    check_specific_cache(manga_id, source)

def check_specific_cache(manga_id: str, source: str):
    """Check cache for specific manga"""
    try:
        with sqlite3.connect("manga_cache.db") as conn:
            cursor = conn.cursor()
            
            # Check for global cache (user_id = NULL)
            cursor.execute("""
                SELECT user_id, manga_id, source, title, last_updated, last_refreshed 
                FROM manga_cache 
                WHERE manga_id = ? AND source = ?
                ORDER BY last_updated DESC
            """, (manga_id, source))
            
            entries = cursor.fetchall()
            if entries:
                print(f"  Found {len(entries)} cache entries:")
                for entry in entries:
                    user_id, manga_id, source, title, last_updated, last_refreshed = entry
                    user_type = "Global" if user_id is None else f"User {user_id}"
                    print(f"    - {user_type}: {title} (Updated: {last_updated})")
            else:
                print("  No cache entries found")
                
    except Exception as e:
        print(f"  Error checking cache: {e}")

def test_cache_operations():
    """Test direct cache operations"""
    print(f"\n=== TESTING DIRECT CACHE OPERATIONS ===")
    
    try:
        # Import cache manager
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from cache_manager import CacheManager
        cache_manager = CacheManager()
        
        # Test data
        test_manga_data = {
            'title': 'Test Manga',
            'image': 'test.jpg',
            'status': 'Ongoing',
            'author': 'Test Author',
            'description': 'Test description',
            'chapters': [{'title': 'Chapter 1', 'url': 'test1'}, {'title': 'Chapter 2', 'url': 'test2'}]
        }
        
        print("1. Testing cache write (global):")
        cache_manager.cache_manga_details("test-manga-123", "weebcentral", test_manga_data, user_id=None)
        print("✓ Cache write completed")
        
        print("\n2. Testing cache read (global):")
        cached_data = cache_manager.get_cached_manga("test-manga-123", "weebcentral", user_id=None)
        if cached_data:
            print(f"✓ Cache read successful: {cached_data.get('title')}")
        else:
            print("✗ Cache read failed")
        
        print("\n3. Testing cache read (user-specific):")
        cached_data = cache_manager.get_cached_manga("test-manga-123", "weebcentral", user_id=1)
        if cached_data:
            print(f"✓ Cache read successful: {cached_data.get('title')}")
        else:
            print("✗ Cache read failed (expected for user-specific)")
        
        # Clean up test data
        cache_manager.clear_manga_cache(user_id=None, manga_id="test-manga-123", source="weebcentral")
        print("\n✓ Test data cleaned up")
        
    except Exception as e:
        print(f"✗ Cache operation test failed: {e}")

def check_api_logs():
    """Check if there are any API logs or errors"""
    print(f"\n=== API LOGS CHECK ===")
    
    # Check if the service is running
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✓ Service is running")
        else:
            print(f"✗ Service returned {response.status_code}")
    except Exception as e:
        print(f"✗ Service not accessible: {e}")
        print("Make sure the service is running on localhost:5000")

def main():
    """Main debugging function"""
    print("MANGA DETAILS CACHE DEBUGGING")
    print("=" * 50)
    
    # Check current database state
    check_database_cache()
    
    # Check API status
    check_api_logs()
    
    # Test cache operations
    test_cache_operations()
    
    # Test with a real manga (if service is running)
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            # Test with a known manga ID
            test_manga_details_request("bleach", "weebcentral")
        else:
            print("\nSkipping API tests - service not available")
    except:
        print("\nSkipping API tests - service not available")
    
    print("\n" + "=" * 50)
    print("DEBUGGING COMPLETE")

if __name__ == "__main__":
    main() 
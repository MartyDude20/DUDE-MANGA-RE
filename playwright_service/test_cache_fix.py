#!/usr/bin/env python3
"""
Test script to verify manga details cache is working correctly
"""

import sqlite3
import json
import time
import requests
from datetime import datetime
from typing import Dict, Optional

def test_cache_operations():
    """Test cache operations step by step"""
    print("=== TESTING CACHE OPERATIONS ===")
    
    try:
        # Import cache manager
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from cache_manager import CacheManager
        cache_manager = CacheManager()
        
        # Test data
        test_manga_data = {
            'title': 'Test Manga Cache',
            'image': 'test.jpg',
            'status': 'Ongoing',
            'author': 'Test Author',
            'description': 'Test description for cache testing',
            'chapters': [{'title': 'Chapter 1', 'url': 'test1'}, {'title': 'Chapter 2', 'url': 'test2'}]
        }
        
        test_manga_id = "test-cache-123"
        test_source = "weebcentral"
        test_user_id = None  # Global cache
        
        print(f"1. Writing test data to cache...")
        cache_manager.cache_manga_details(test_manga_id, test_source, test_manga_data, test_user_id)
        print("✓ Write completed")
        
        print(f"\n2. Reading test data from cache...")
        cached_data = cache_manager.get_cached_manga(test_manga_id, test_source, test_user_id)
        if cached_data:
            print(f"✓ Read successful: {cached_data.get('title')}")
            print(f"  Chapters: {len(cached_data.get('chapters', []))}")
            print(f"  Author: {cached_data.get('author')}")
        else:
            print("✗ Read failed")
            return False
        
        print(f"\n3. Verifying database directly...")
        with sqlite3.connect("manga_cache.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, manga_id, source, title, chapters 
                FROM manga_cache 
                WHERE manga_id = ? AND source = ?
            """, (test_manga_id, test_source))
            
            entries = cursor.fetchall()
            print(f"  Found {len(entries)} database entries:")
            for entry in entries:
                user_id, manga_id, source, title, chapters = entry
                user_type = "Global" if user_id is None else f"User {user_id}"
                chapter_count = len(json.loads(chapters)) if chapters else 0
                print(f"    - {user_type}: {title} ({chapter_count} chapters)")
        
        print(f"\n4. Testing cache update...")
        updated_data = test_manga_data.copy()
        updated_data['title'] = 'Updated Test Manga'
        updated_data['chapters'].append({'title': 'Chapter 3', 'url': 'test3'})
        
        cache_manager.cache_manga_details(test_manga_id, test_source, updated_data, test_user_id)
        print("✓ Update completed")
        
        print(f"\n5. Reading updated data...")
        updated_cached_data = cache_manager.get_cached_manga(test_manga_id, test_source, test_user_id)
        if updated_cached_data:
            print(f"✓ Read successful: {updated_cached_data.get('title')}")
            print(f"  Chapters: {len(updated_cached_data.get('chapters', []))}")
        else:
            print("✗ Read failed")
            return False
        
        print(f"\n6. Verifying only one entry exists...")
        with sqlite3.connect("manga_cache.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM manga_cache 
                WHERE manga_id = ? AND source = ?
            """, (test_manga_id, test_source))
            
            count = cursor.fetchone()[0]
            print(f"  Found {count} entries (should be 1)")
            if count == 1:
                print("✓ Unique constraint working correctly")
            else:
                print("✗ Multiple entries found - unique constraint not working")
                return False
        
        # Clean up
        cache_manager.clear_manga_cache(user_id=test_user_id, manga_id=test_manga_id, source=test_source)
        print(f"\n✓ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_api_cache():
    """Test cache through the API"""
    print(f"\n=== TESTING API CACHE ===")
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code != 200:
            print("✗ Service not running")
            return False
    except:
        print("✗ Service not accessible")
        return False
    
    # Test with a real manga
    test_manga_id = "bleach"
    test_source = "weebcentral"
    
    print(f"1. First API request (should be fresh):")
    start_time = time.time()
    
    try:
        response = requests.get(f"http://localhost:5000/manga/{test_source}/{test_manga_id}")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success ({duration:.2f}s)")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Cached: {data.get('cached', 'N/A')}")
            print(f"  Chapters: {len(data.get('chapters', []))}")
        else:
            print(f"✗ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False
    
    print(f"\n2. Second API request (should be cached):")
    start_time = time.time()
    
    try:
        response = requests.get(f"http://localhost:5000/manga/{test_source}/{test_manga_id}")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success ({duration:.2f}s)")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Cached: {data.get('cached', 'N/A')}")
            print(f"  Chapters: {len(data.get('chapters', []))}")
            
            # Check if it was actually cached
            if data.get('cached') == True:
                print("✓ API correctly reported cached data")
                return True
            else:
                print("✗ API reported fresh data instead of cached")
                return False
        else:
            print(f"✗ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("MANGA DETAILS CACHE TESTING")
    print("=" * 50)
    
    # Test direct cache operations
    cache_success = test_cache_operations()
    
    if cache_success:
        print("\n✓ Direct cache operations working correctly")
    else:
        print("\n✗ Direct cache operations failed")
        return
    
    # Test API cache
    api_success = test_api_cache()
    
    if api_success:
        print("\n✓ API cache working correctly")
    else:
        print("\n✗ API cache failed")
    
    print("\n" + "=" * 50)
    if cache_success and api_success:
        print("ALL TESTS PASSED - CACHE IS WORKING CORRECTLY")
    else:
        print("SOME TESTS FAILED - CACHE HAS ISSUES")

if __name__ == "__main__":
    main() 
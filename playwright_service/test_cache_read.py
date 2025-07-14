#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cache_manager import CacheManager

def test_cache_read():
    cache_manager = CacheManager()
    
    # Test reading the data we know exists
    test_manga_id = "test-cache-123"
    test_source = "weebcentral"
    test_user_id = None
    
    print(f"Testing cache read for: {test_manga_id}")
    print(f"Source: {test_source}")
    print(f"User ID: {test_user_id}")
    
    # Read from cache
    cached_data = cache_manager.get_cached_manga(test_manga_id, test_source, test_user_id)
    
    if cached_data:
        print(f"✓ Cache read successful!")
        print(f"  Title: {cached_data.get('title')}")
        print(f"  Chapters: {len(cached_data.get('chapters', []))}")
        print(f"  Author: {cached_data.get('author')}")
    else:
        print("✗ Cache read failed")
        
        # Let's check what's in the database directly
        import sqlite3
        with sqlite3.connect("manga_cache.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, manga_id, source, title, chapters 
                FROM manga_cache 
                WHERE manga_id = ? AND source = ?
            """, (test_manga_id, test_source))
            
            entries = cursor.fetchall()
            print(f"\nDirect database query found {len(entries)} entries:")
            for entry in entries:
                user_id, manga_id, source, title, chapters = entry
                print(f"  - user_id={user_id}, manga_id={manga_id}, source={source}, title={title}")
                
                # Check if user_id matches what we're looking for
                if user_id == test_user_id:
                    print(f"    ✓ user_id matches")
                else:
                    print(f"    ✗ user_id mismatch: expected {test_user_id}, got {user_id}")

if __name__ == "__main__":
    test_cache_read() 
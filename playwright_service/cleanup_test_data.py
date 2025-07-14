#!/usr/bin/env python3
import sqlite3

def cleanup_test_data():
    with sqlite3.connect("manga_cache.db") as conn:
        cursor = conn.cursor()
        
        # Delete test entries
        cursor.execute("DELETE FROM manga_cache WHERE manga_id = 'test-cache-123'")
        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} test entries")
        
        conn.commit()

if __name__ == "__main__":
    cleanup_test_data() 
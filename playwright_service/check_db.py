#!/usr/bin/env python3
import sqlite3
import json

def check_db():
    with sqlite3.connect("manga_cache.db") as conn:
        cursor = conn.cursor()
        
        # Check for our test entry
        cursor.execute("""
            SELECT user_id, manga_id, source, title, chapters 
            FROM manga_cache 
            WHERE manga_id = ?
        """, ("test-cache-123",))
        
        entries = cursor.fetchall()
        print(f"Found {len(entries)} entries for test-cache-123:")
        for entry in entries:
            user_id, manga_id, source, title, chapters = entry
            user_type = "Global" if user_id is None else f"User {user_id}"
            chapter_count = len(json.loads(chapters)) if chapters else 0
            print(f"  - {user_type}: {title} ({chapter_count} chapters)")
        
        # Check all entries
        cursor.execute("""
            SELECT user_id, manga_id, source, title 
            FROM manga_cache 
            ORDER BY last_updated DESC 
            LIMIT 5
        """)
        
        all_entries = cursor.fetchall()
        print(f"\nRecent entries:")
        for entry in all_entries:
            user_id, manga_id, source, title = entry
            user_type = "Global" if user_id is None else f"User {user_id}"
            print(f"  - {user_type}: {manga_id} ({source}) - {title}")

if __name__ == "__main__":
    check_db() 
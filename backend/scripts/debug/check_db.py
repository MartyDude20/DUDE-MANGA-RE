import sqlite3
import json

def check_database():
    """Check the database schema and data"""
    with sqlite3.connect('manga_cache.db') as conn:
        cursor = conn.cursor()
        
        # Check schema
        print("=== DATABASE SCHEMA ===")
        cursor.execute("PRAGMA table_info(manga_cache)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column {col[1]}: {col[2]}")
        
        print("\n=== SAMPLE DATA ===")
        cursor.execute("SELECT * FROM manga_cache LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"Found {len(row)} columns in sample row")
            print(f"Sample data: {row}")
        else:
            print("No data found in manga_cache table")
        
        # Check for WeebCentral data specifically
        print("\n=== WEEB CENTRAL DATA ===")
        cursor.execute("SELECT title, tags, type, released, official_translation, anime_adaptation, adult_content FROM manga_cache WHERE source = 'weebcentral' LIMIT 1")
        weeb_data = cursor.fetchone()
        if weeb_data:
            print(f"Title: {weeb_data[0]}")
            print(f"Tags: {weeb_data[1]}")
            print(f"Type: {weeb_data[2]}")
            print(f"Released: {weeb_data[3]}")
            print(f"Official Translation: {weeb_data[4]}")
            print(f"Anime Adaptation: {weeb_data[5]}")
            print(f"Adult Content: {weeb_data[6]}")
            
            # Parse tags JSON
            if weeb_data[1]:
                try:
                    tags = json.loads(weeb_data[1])
                    print(f"Parsed tags: {tags}")
                except:
                    print("Could not parse tags JSON")
        else:
            print("No WeebCentral data found")

if __name__ == "__main__":
    check_database() 
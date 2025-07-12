"""
Test script for the preloader system
Run this to test preloading and search functionality
"""
import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import PreloadedManga
from services.search_service import search_service
from services.preloader import preloader_service

def test_preloader():
    """Test the preloader functionality"""
    with app.app_context():
        print("🧪 Testing Preloader System\n")
        
        # Test 1: Database connection
        print("1️⃣ Testing database connection...")
        try:
            count = PreloadedManga.query.count()
            print(f"✅ Database connected. Current manga count: {count}")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        
        # Test 2: Search without preloaded data
        print("\n2️⃣ Testing search without preloaded data...")
        try:
            results = search_service.search("naruto", ["weebcentral"], force_refresh=True)
            print(f"✅ Search returned {len(results)} results")
            if results:
                print(f"   First result: {results[0].get('title')}")
                print(f"   Cached: {results[0].get('cached', False)}")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Test 3: Check if results were saved to preloader
        print("\n3️⃣ Checking if results were saved to preloader...")
        try:
            saved_count = PreloadedManga.query.filter(
                PreloadedManga.normalized_title.contains('naruto')
            ).count()
            print(f"✅ Found {saved_count} Naruto manga in preloader cache")
        except Exception as e:
            print(f"❌ Error checking saved results: {e}")
        
        # Test 4: Search with preloaded data
        print("\n4️⃣ Testing search with preloaded data...")
        try:
            results = search_service.search("naruto", ["weebcentral"], force_refresh=False)
            print(f"✅ Search returned {len(results)} results")
            cached_count = sum(1 for r in results if r.get('cached', False))
            print(f"   Cached results: {cached_count}/{len(results)}")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Test 5: Preload a small batch
        print("\n5️⃣ Testing manual preload (this may take a minute)...")
        try:
            initial_count = PreloadedManga.query.count()
            print(f"   Starting with {initial_count} manga in database")
            
            # Preload just 1 page from weebcentral
            preloader_service.preload_source("weebcentral", page_limit=1)
            
            final_count = PreloadedManga.query.count()
            print(f"✅ Preload complete. Now have {final_count} manga (added {final_count - initial_count})")
        except Exception as e:
            print(f"❌ Preload error: {e}")
        
        # Test 6: Popular manga tracking
        print("\n6️⃣ Testing popular manga tracking...")
        try:
            popular = PreloadedManga.query.order_by(
                PreloadedManga.popularity.desc()
            ).limit(5).all()
            
            print(f"✅ Top 5 popular manga:")
            for i, manga in enumerate(popular, 1):
                print(f"   {i}. {manga.title} (popularity: {manga.popularity})")
        except Exception as e:
            print(f"❌ Error getting popular manga: {e}")
        
        print("\n✅ All tests completed!")
        return True

def test_specific_source(source):
    """Test a specific source"""
    with app.app_context():
        print(f"\n🧪 Testing {source} source...")
        
        try:
            # Search for a popular term
            results = search_service.search("one piece", [source], force_refresh=True)
            print(f"✅ {source}: Found {len(results)} results")
            
            if results:
                # Test getting details for the first result
                first_result = results[0]
                manga_id = first_result.get('id')
                if manga_id:
                    details = search_service.get_manga_details(manga_id, source, force_refresh=True)
                    if details:
                        print(f"✅ {source}: Got details for '{details.get('title')}'")
                        print(f"   Chapters: {len(details.get('chapters', []))}")
                    else:
                        print(f"⚠️  {source}: Could not get manga details")
        except Exception as e:
            print(f"❌ {source} error: {e}")

if __name__ == "__main__":
    # Run main tests
    test_preloader()
    
    # Test each source individually
    print("\n" + "="*50)
    print("Testing individual sources...")
    for source in ["weebcentral", "asurascans", "mangadex"]:
        test_specific_source(source)
        time.sleep(2)  # Rate limiting 
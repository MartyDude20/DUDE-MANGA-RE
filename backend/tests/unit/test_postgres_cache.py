from playwright.sync_api import sync_playwright
from sources.weebcentral import get_details, extract_manga_id_from_url
from cache_manager import CacheManager
from cache_config import get_cache_config

def test_postgres_cache():
    """Test PostgreSQL cache functionality"""
    
    # Get cache configuration
    config = get_cache_config()
    print(f"Using cache configuration: {config}")
    
    # Initialize cache manager
    cache_manager = CacheManager(**config)
    
    # Extract manga ID from the URL
    url = "https://weebcentral.com/series/01J76XY7E4JCPK14V53BVQWD9Y/Bleach"
    manga_id = extract_manga_id_from_url(url)
    print(f"Testing manga ID: {manga_id}")
    
    if not manga_id:
        print("Error: Could not extract manga ID from URL")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Get detailed information
            print("Fetching detailed information...")
            details = get_details(page, manga_id)
            print(f"Details fetched: {details.get('title')} by {details.get('author')}")
            print(f"Tags: {details.get('tags')}")
            
            # Save to cache
            print("Saving to cache...")
            cache_manager.cache_manga_details(manga_id, 'weebcentral', details, user_id=None)
            print("Cache save completed")
            
            # Retrieve from cache
            print("Retrieving from cache...")
            cached_details = cache_manager.get_cached_manga(manga_id, 'weebcentral', user_id=None)
            
            if cached_details:
                print("✅ Successfully saved and retrieved from cache!")
                print(f"Title: {cached_details.get('title')}")
                print(f"Author: {cached_details.get('author')}")
                print(f"Tags: {cached_details.get('tags')}")
                print(f"Type: {cached_details.get('type')}")
                print(f"Released: {cached_details.get('released')}")
                print(f"Official Translation: {cached_details.get('official_translation')}")
                print(f"Anime Adaptation: {cached_details.get('anime_adaptation')}")
                print(f"Adult Content: {cached_details.get('adult_content')}")
                print(f"Chapters: {len(cached_details.get('chapters', []))} chapters")
                
                # Test advanced PostgreSQL features
                if cache_manager.use_postgres:
                    print("\n🔍 Testing PostgreSQL-specific features...")
                    test_postgres_features(cache_manager)
            else:
                print("❌ Failed to retrieve from cache")
                
        except Exception as e:
            print(f"Error during testing: {e}")
        finally:
            browser.close()

def test_postgres_features(cache_manager):
    """Test PostgreSQL-specific features like JSONB queries"""
    try:
        with cache_manager._get_connection() as conn:
            cursor = conn.cursor()
            
            # Test JSONB query for tags
            print("Testing JSONB tag search...")
            cursor.execute('''
                SELECT title, tags FROM manga_cache 
                WHERE tags ? 'Action' AND source = 'weebcentral'
                LIMIT 5
            ''')
            
            results = cursor.fetchall()
            print(f"Found {len(results)} manga with 'Action' tag:")
            for title, tags in results:
                print(f"  - {title}: {tags}")
                
    except Exception as e:
        print(f"PostgreSQL feature test failed: {e}")

if __name__ == "__main__":
    test_postgres_cache() 
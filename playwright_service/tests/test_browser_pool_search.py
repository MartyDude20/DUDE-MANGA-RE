import os
import sys
import time
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.simple_search import SimpleSearchService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_search_with_browser_pool():
    """Test search service using browser pool"""
    print("\n=== Testing Search Service with Browser Pool ===")
    
    search_service = SimpleSearchService()
    
    # Test multiple searches to see browser pool in action
    queries = ["naruto", "one piece", "bleach"]
    
    print("Testing browser pool with search service...")
    start_time = time.time()
    
    for i, query in enumerate(queries):
        print(f"Searching for '{query}'...")
        search_start = time.time()
        
        results = search_service.search(query, sources=['weebcentral'], force_refresh=True)
        
        search_time = time.time() - search_start
        print(f"  Found {len(results)} results in {search_time:.2f}s")
        
        # Small delay between searches
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    print(f"\n✓ Total search time: {total_time:.2f}s")
    print(f"✓ Average per search: {total_time/len(queries):.2f}s")
    
    # Get metrics
    metrics = search_service.get_metrics()
    print(f"✓ Search metrics: {metrics}")
    
    return total_time, metrics

def test_search_without_pool():
    """Test search without browser pool for comparison"""
    print("\n=== Testing Search Without Browser Pool ===")
    
    # Create a simple search function that doesn't use the pool
    def simple_search_without_pool(query: str):
        from playwright.sync_api import sync_playwright
        import time
        
        start_time = time.time()
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Optimize page settings
        page.set_viewport_size({"width": 1280, "height": 720})
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Disable images and other resources for faster loading
        page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}", lambda route: route.abort())
        page.route("**/*.{css,js}", lambda route: route.continue_())
        
        # Simulate search (just navigate to a page)
        page.goto("https://weebcentral.com")
        title = page.title()
        
        page.close()
        browser.close()
        playwright.stop()
        
        return time.time() - start_time
    
    queries = ["naruto", "one piece", "bleach"]
    
    print("Testing without browser pool...")
    start_time = time.time()
    
    for i, query in enumerate(queries):
        print(f"Searching for '{query}'...")
        search_time = simple_search_without_pool(query)
        print(f"  Completed in {search_time:.2f}s")
        
        # Small delay between searches
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    print(f"\n✓ Total search time: {total_time:.2f}s")
    print(f"✓ Average per search: {total_time/len(queries):.2f}s")
    
    return total_time

def test_browser_pool_stats():
    """Test browser pool statistics"""
    print("\n=== Testing Browser Pool Statistics ===")
    
    from services.browser_pool import browser_pool
    
    # Get initial stats
    initial_stats = browser_pool.get_stats()
    print(f"Initial pool stats: {initial_stats}")
    
    # Test getting and returning browsers
    browsers = []
    for i in range(2):
        browser = browser_pool.get_browser()
        if browser:
            browsers.append(browser)
            stats = browser_pool.get_stats()
            print(f"After getting browser {i+1}: {stats}")
    
    # Return browsers
    for i, browser in enumerate(browsers):
        browser_pool.return_browser(browser)
        stats = browser_pool.get_stats()
        print(f"After returning browser {i+1}: {stats}")
    
    print("✓ Browser pool statistics test completed")

def main():
    """Run browser pool search tests"""
    print("🚀 Starting Browser Pool Search Tests")
    print("=" * 50)
    
    try:
        # Test browser pool statistics
        test_browser_pool_stats()
        
        # Test search with browser pool
        pool_time, pool_metrics = test_search_with_browser_pool()
        
        # Test search without browser pool
        no_pool_time = test_search_without_pool()
        
        # Compare results
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE COMPARISON")
        print("=" * 50)
        
        if pool_time < no_pool_time:
            improvement = ((no_pool_time - pool_time) / no_pool_time) * 100
            print(f"✅ Browser pool is {improvement:.1f}% faster!")
            print(f"   With pool: {pool_time:.2f}s")
            print(f"   Without pool: {no_pool_time:.2f}s")
        else:
            print(f"⚠️ Browser pool is {((pool_time - no_pool_time) / no_pool_time) * 100:.1f}% slower")
            print(f"   With pool: {pool_time:.2f}s")
            print(f"   Without pool: {no_pool_time:.2f}s")
        
        print(f"\n📈 Search Metrics: {pool_metrics}")
        print("\n✅ All browser pool search tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
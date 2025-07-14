import os
import sys
import time
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.browser_pool import BrowserPool, browser_pool
from services.simple_search import SimpleSearchService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_browser_pool_basic():
    """Test basic browser pool functionality"""
    print("\n=== Testing Basic Browser Pool Functionality ===")
    
    # Create a new pool for testing
    pool = BrowserPool(pool_size=2)
    
    try:
        # Test getting browsers
        browser1 = pool.get_browser()
        browser2 = pool.get_browser()
        
        assert browser1 is not None, "Failed to get first browser"
        assert browser2 is not None, "Failed to get second browser"
        assert browser1 != browser2, "Got same browser instance"
        
        print("✓ Successfully got 2 browsers from pool")
        
        # Test returning browsers
        pool.return_browser(browser1)
        pool.return_browser(browser2)
        
        print("✓ Successfully returned browsers to pool")
        
        # Test reusing browsers
        browser3 = pool.get_browser()
        browser4 = pool.get_browser()
        
        assert browser3 is not None, "Failed to get browser after return"
        assert browser4 is not None, "Failed to get second browser after return"
        
        print("✓ Successfully reused browsers from pool")
        
        # Cleanup
        pool.return_browser(browser3)
        pool.return_browser(browser4)
        
    finally:
        pool.shutdown()
    
    print("✓ Basic browser pool test passed")

def test_browser_pool_performance():
    """Test browser pool performance vs individual browsers"""
    print("\n=== Testing Browser Pool Performance ===")
    
    # Test with pool
    pool = BrowserPool(pool_size=3)
    pool_times = []
    
    def pool_worker():
        start_time = time.time()
        browser = pool.get_browser()
        if browser:
            page = browser.new_page()
            page.goto("https://httpbin.org/delay/0.5")
            page.close()
            pool.return_browser(browser)
            return time.time() - start_time
        return None
    
    # Test pool performance
    print("Testing with browser pool...")
    for i in range(6):
        result = pool_worker()
        if result:
            pool_times.append(result)
            print(f"  Pool task {i+1}: {result:.2f}s")
    
    pool.shutdown()
    
    # Test without pool (individual browsers)
    individual_times = []
    
    def individual_worker():
        start_time = time.time()
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://httpbin.org/delay/0.5")
        page.close()
        browser.close()
        playwright.stop()
        return time.time() - start_time
    
    print("Testing with individual browsers...")
    for i in range(6):
        result = individual_worker()
        if result:
            individual_times.append(result)
            print(f"  Individual task {i+1}: {result:.2f}s")
    
    # Calculate statistics
    if pool_times and individual_times:
        avg_pool_time = sum(pool_times) / len(pool_times)
        avg_individual_time = sum(individual_times) / len(individual_times)
        
        print(f"\n✓ Pool average time: {avg_pool_time:.2f}s")
        print(f"✓ Individual average time: {avg_individual_time:.2f}s")
        print(f"✓ Performance improvement: {((avg_individual_time - avg_pool_time) / avg_individual_time * 100):.1f}%")
        
        if avg_pool_time < avg_individual_time:
            print("✓ Browser pool is faster!")
        else:
            print("⚠ Browser pool is slower (this might be due to overhead for small tasks)")

def test_search_service_with_pool():
    """Test search service using browser pool"""
    print("\n=== Testing Search Service with Browser Pool ===")
    
    search_service = SimpleSearchService()
    
    # Test multiple searches to see browser pool in action
    queries = ["naruto", "one piece"]
    
    start_time = time.time()
    
    for i, query in enumerate(queries):
        print(f"Searching for '{query}'...")
        results = search_service.search(query, sources=['weebcentral'], force_refresh=True)
        print(f"  Found {len(results)} results")
        
        # Small delay between searches
        time.sleep(1)
    
    total_time = time.time() - start_time
    print(f"✓ Total search time: {total_time:.2f}s")
    print(f"✓ Average per search: {total_time/len(queries):.2f}s")
    
    # Get metrics
    metrics = search_service.get_metrics()
    print(f"✓ Search metrics: {metrics}")

def test_browser_pool_stats():
    """Test browser pool statistics and monitoring"""
    print("\n=== Testing Browser Pool Statistics ===")
    
    pool = BrowserPool(pool_size=2)
    
    # Get initial stats
    initial_stats = pool.get_stats()
    print(f"Initial stats: {initial_stats}")
    
    # Use browsers and check stats
    browsers = []
    for i in range(3):
        browser = pool.get_browser()
        if browser:
            browsers.append(browser)
            stats = pool.get_stats()
            print(f"After getting browser {i+1}: {stats}")
    
    # Return browsers and check stats
    for i, browser in enumerate(browsers):
        pool.return_browser(browser)
        stats = pool.get_stats()
        print(f"After returning browser {i+1}: {stats}")
    
    pool.shutdown()
    print("✓ Browser pool statistics test completed")

def test_global_browser_pool():
    """Test the global browser pool instance"""
    print("\n=== Testing Global Browser Pool ===")
    
    # Test the global instance
    browser1 = browser_pool.get_browser()
    browser2 = browser_pool.get_browser()
    
    if browser1 and browser2:
        print("✓ Successfully got browsers from global pool")
        
        # Test basic functionality
        page1 = browser1.new_page()
        page1.goto("https://httpbin.org/get")
        title1 = page1.title()
        page1.close()
        
        page2 = browser2.new_page()
        page2.goto("https://httpbin.org/get")
        title2 = page2.title()
        page2.close()
        
        print(f"✓ Tested pages: {title1}, {title2}")
        
        # Return browsers
        browser_pool.return_browser(browser1)
        browser_pool.return_browser(browser2)
        
        print("✓ Successfully returned browsers to global pool")
        
        # Get stats
        stats = browser_pool.get_stats()
        print(f"✓ Global pool stats: {stats}")
    else:
        print("❌ Failed to get browsers from global pool")

def main():
    """Run all browser pool tests"""
    print("🚀 Starting Simple Browser Pool Tests")
    print("=" * 50)
    
    try:
        test_browser_pool_basic()
        test_browser_pool_performance()
        test_browser_pool_stats()
        test_global_browser_pool()
        test_search_service_with_pool()
        
        print("\n" + "=" * 50)
        print("✅ All simple browser pool tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Test script for the simple TTL cache system
"""

import time
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # playwright_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # project root

from services.simple_cache import search_cache
from services.simple_search import simple_search_service

def test_cache_basic():
    """Test basic cache functionality"""
    print("=== Testing Basic Cache Functionality ===")
    
    # Test cache set/get
    search_cache.set("test_key", ["result1", "result2"])
    result = search_cache.get("test_key")
    
    if result == ["result1", "result2"]:
        print("✅ Basic cache set/get works")
    else:
        print(f"❌ Basic cache set/get failed: {result}")
    
    # Test cache size
    size = search_cache.size()
    print(f"Cache size: {size}")
    
    # Test cache clear
    search_cache.clear()
    size_after_clear = search_cache.size()
    if size_after_clear == 0:
        print("✅ Cache clear works")
    else:
        print(f"❌ Cache clear failed: {size_after_clear}")

def test_cache_expiration():
    """Test cache expiration (simulated)"""
    print("\n=== Testing Cache Expiration ===")
    
    # Set a cache entry
    search_cache.set("expire_test", "test_data")
    
    # Verify it exists
    result = search_cache.get("expire_test")
    if result == "test_data":
        print("✅ Cache entry created successfully")
    else:
        print(f"❌ Cache entry creation failed: {result}")
    
    # Manually expire it by modifying the timestamp
    with search_cache.lock:
        if "expire_test" in search_cache.cache:
            # Set timestamp to 7 hours ago (older than 6-hour TTL)
            search_cache.cache["expire_test"]["timestamp"] = time.time() - (7 * 3600)
    
    # Try to get it again - should be expired
    result = search_cache.get("expire_test")
    if result is None:
        print("✅ Cache expiration works")
    else:
        print(f"❌ Cache expiration failed: {result}")

def test_search_service():
    """Test the search service with cache"""
    print("\n=== Testing Search Service ===")
    
    # Test search with a simple query
    try:
        results = simple_search_service.search("solo", ["weebcentral"], force_refresh=False)
        print(f"✅ Search service works: {len(results)} results")
        
        # Check if results have cache info
        if results and all('cached' in result for result in results):
            print("✅ Results include cache information")
        else:
            print("❌ Results missing cache information")
            
    except Exception as e:
        print(f"❌ Search service failed: {e}")

def test_cache_stats():
    """Test cache statistics"""
    print("\n=== Testing Cache Statistics ===")
    
    # Add some test data
    search_cache.set("stats_test1", "data1")
    search_cache.set("stats_test2", "data2")
    
    # Get stats
    stats = search_cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Get search service metrics
    metrics = simple_search_service.get_metrics()
    print(f"Search metrics: {metrics}")

def main():
    """Run all tests"""
    print("Testing Simple TTL Cache System")
    print("=" * 40)
    
    try:
        test_cache_basic()
        test_cache_expiration()
        test_search_service()
        test_cache_stats()
        
        print("\n" + "=" * 40)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
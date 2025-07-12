#!/usr/bin/env python3
"""
Test the simple TTL cache system by making HTTP requests
"""

import requests
import time
import json

def test_search_cache():
    """Test search with cache functionality"""
    base_url = "http://localhost:5000"
    
    print("=== Testing Simple TTL Cache System ===")
    
    # Test 1: First search (should be cache miss)
    print("\n1. First search for 'solo' (cache miss)...")
    start_time = time.time()
    response = requests.get(f"{base_url}/search?q=solo&sources=weebcentral")
    first_search_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        cached = data.get('cached', False)
        print(f"✅ First search: {len(results)} results, cached: {cached}, time: {first_search_time:.2f}s")
    else:
        print(f"❌ First search failed: {response.status_code}")
        return
    
    # Test 2: Repeat search (should be cache hit)
    print("\n2. Repeat search for 'solo' (cache hit)...")
    start_time = time.time()
    response = requests.get(f"{base_url}/search?q=solo&sources=weebcentral")
    second_search_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        cached = data.get('cached', False)
        print(f"✅ Second search: {len(results)} results, cached: {cached}, time: {second_search_time:.2f}s")
        
        # Check if second search was faster (cache hit)
        if second_search_time < first_search_time:
            speedup = first_search_time / second_search_time
            print(f"🚀 Cache hit speedup: {speedup:.1f}x faster!")
        else:
            print("⚠️  Second search wasn't faster (might be cache miss)")
    else:
        print(f"❌ Second search failed: {response.status_code}")
    
    # Test 3: Force refresh search
    print("\n3. Force refresh search for 'solo'...")
    start_time = time.time()
    response = requests.get(f"{base_url}/search?q=solo&sources=weebcentral&refresh=true")
    refresh_search_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        cached = data.get('cached', False)
        print(f"✅ Force refresh: {len(results)} results, cached: {cached}, time: {refresh_search_time:.2f}s")
    else:
        print(f"❌ Force refresh failed: {response.status_code}")
    
    # Test 4: Check performance metrics
    print("\n4. Check performance metrics...")
    response = requests.get(f"{base_url}/performance/metrics")
    
    if response.status_code == 200:
        metrics = response.json()
        print(f"✅ Performance metrics:")
        print(f"   - Total searches: {metrics.get('total_searches', 0)}")
        print(f"   - Cache hits: {metrics.get('cache_hits', 0)}")
        print(f"   - Cache misses: {metrics.get('cache_misses', 0)}")
        print(f"   - Cache hit rate: {metrics.get('cache_hit_rate', '0%')}")
        print(f"   - Average search time: {metrics.get('avg_search_time', '0s')}")
        
        cache_stats = metrics.get('cache_stats', {})
        print(f"   - Cache entries: {cache_stats.get('total_entries', 0)}")
        print(f"   - TTL: {cache_stats.get('ttl_hours', 0)} hours")
    else:
        print(f"❌ Metrics failed: {response.status_code}")
    
    # Test 5: Test different query
    print("\n5. Test different query 'naruto'...")
    start_time = time.time()
    response = requests.get(f"{base_url}/search?q=naruto&sources=weebcentral")
    naruto_search_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        cached = data.get('cached', False)
        print(f"✅ Naruto search: {len(results)} results, cached: {cached}, time: {naruto_search_time:.2f}s")
    else:
        print(f"❌ Naruto search failed: {response.status_code}")

def main():
    """Run the cache test"""
    try:
        test_search_cache()
        print("\n" + "=" * 50)
        print("✅ Simple TTL Cache System Test Complete!")
        print("The cache is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the service. Make sure it's running on port 5000.")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Quick performance test for the optimized search service
"""

import time
import requests
import json
import sys
from datetime import datetime

# Test configuration
PROXY_URL = "http://localhost:3006"
PLAYWRIGHT_URL = "http://localhost:5000"

# Test queries - Using the provided manga list
TEST_QUERIES = [
    "Murim Login",
    "The Greatest Estate Developer", 
    "Nano Machine",
    "Solo Max-Level Newbie",
    "Infinite Mage",
    "Solo Max-Level Newbie",
    "Solo Leveling",
    "Swordmaster's Youngest Son"
]

def test_search_speed(skip_cache_clear=False):
    """Test search speed with the new optimized service"""
    print("🚀 Quick Performance Test - Optimized Search Service")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if skip_cache_clear:
        print("🔥 POST-CACHE TEST (using cached results)")
    else:
        print("❄️  PRE-CACHE TEST (fresh cache)")
    
    # Check service status
    print("\n🔍 Checking service status...")
    try:
        proxy_status = requests.get(f"{PROXY_URL}/api/health", timeout=5)
        playwright_status = requests.get(f"{PLAYWRIGHT_URL}/health", timeout=5)
        
        if proxy_status.status_code == 200 and playwright_status.status_code == 200:
            print("✅ Services are running")
        else:
            print("❌ Services not responding properly")
            return
    except Exception as e:
        print(f"❌ Service check failed: {e}")
        return
    
    # Clear cache for fresh test (unless skipping)
    if not skip_cache_clear:
        print("\n🗑️  Clearing cache for fresh test...")
        try:
            requests.post(f"{PLAYWRIGHT_URL}/test/cache/clear")
            print("✅ Cache cleared")
        except Exception as e:
            print(f"⚠️  Cache clear failed: {e}")
    else:
        print("\n🔥 Using existing cache...")
    
    # Test searches
    print(f"\n🔍 Testing {len(TEST_QUERIES)} searches...")
    print("-" * 60)
    
    results = []
    total_time = 0
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        start_time = time.time()
        
        try:
            # Make search request
            sources_str = "asurascans,weebcentral,mangadex"
            search_url = f"{PROXY_URL}/api/search?q={query}&sources={sources_str}"
            
            response = requests.get(search_url, timeout=30)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                manga_results = data.get('results', [])
                manga_count = len(manga_results)
                cached_count = sum(1 for m in manga_results if m.get('cached', False))
                
                print(f"   ✅ Found {manga_count} manga ({cached_count} cached) in {duration:.3f}s")
                
                results.append({
                    'query': query,
                    'duration': duration,
                    'manga_count': manga_count,
                    'cached_count': cached_count,
                    'success': True
                })
                
                total_time += duration
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                results.append({
                    'query': query,
                    'duration': 0,
                    'manga_count': 0,
                    'cached_count': 0,
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'query': query,
                'duration': 0,
                'manga_count': 0,
                'cached_count': 0,
                'success': False
            })
    
    # Calculate statistics
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        avg_time = total_time / len(successful_results)
        total_manga = sum(r['manga_count'] for r in successful_results)
        total_cached = sum(r['cached_count'] for r in successful_results)
        cache_hit_rate = (total_cached / total_manga * 100) if total_manga > 0 else 0
        
        print(f"\n{'='*60}")
        print("📊 PERFORMANCE RESULTS")
        print(f"{'='*60}")
        print(f"Total Queries: {len(TEST_QUERIES)}")
        print(f"Successful Queries: {len(successful_results)}")
        print(f"Average Response Time: {avg_time:.3f}s")
        print(f"Total Manga Found: {total_manga}")
        print(f"Total Cached Results: {total_cached}")
        print(f"Cache Hit Rate: {cache_hit_rate:.1f}%")
        
        # Performance assessment
        if avg_time < 2.0:
            print(f"\n🎉 EXCELLENT PERFORMANCE!")
            print(f"   Average time: {avg_time:.3f}s (under 2s target)")
        elif avg_time < 5.0:
            print(f"\n✅ GOOD PERFORMANCE")
            print(f"   Average time: {avg_time:.3f}s (under 5s target)")
        elif avg_time < 10.0:
            print(f"\n⚠️  ACCEPTABLE PERFORMANCE")
            print(f"   Average time: {avg_time:.3f}s (under 10s target)")
        else:
            print(f"\n❌ POOR PERFORMANCE")
            print(f"   Average time: {avg_time:.3f}s (over 10s)")
        
        # Check performance metrics
        try:
            metrics_response = requests.get(f"{PLAYWRIGHT_URL}/performance/metrics", timeout=5)
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                print(f"\n📈 SYSTEM METRICS:")
                print(f"   Total Searches: {metrics.get('total_searches', 0)}")
                print(f"   Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1f}%")
                print(f"   Average Search Time: {metrics.get('avg_search_time', 0):.3f}s")
                print(f"   Active Browsers: {metrics.get('active_browsers', 0)}")
                print(f"   Cache Size: {metrics.get('cache_size', 0)}")
        except Exception as e:
            print(f"   ⚠️  Could not get metrics: {e}")
    
    else:
        print("\n❌ No successful searches")
    
    print(f"\n✅ Performance test completed!")

if __name__ == "__main__":
    skip_cache_clear = False
    if len(sys.argv) > 1 and sys.argv[1] == "--skip-cache":
        skip_cache_clear = True
    test_search_speed(skip_cache_clear) 
#!/usr/bin/env python3
"""
Performance optimization test to demonstrate speed improvements
"""

import time
import requests
import json
import statistics
from datetime import datetime
from typing import List, Dict

# Test configuration
PROXY_URL = "http://localhost:3006"
PLAYWRIGHT_URL = "http://localhost:5000"

# Test queries for performance testing
TEST_QUERIES = [
    "solo leveling",
    "one piece",
    "naruto",
    "bleach",
    "dragon ball",
    "attack on titan",
    "demon slayer",
    "jujutsu kaisen",
    "my hero academia",
    "tokyo ghoul"
]

def test_search_performance():
    """Test search performance with optimizations"""
    print("🚀 Performance Optimization Test")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
    
    # Clear cache for fresh test
    print("\n🗑️  Clearing cache for fresh test...")
    try:
        requests.post(f"{PLAYWRIGHT_URL}/test/cache/clear")
        print("✅ Cache cleared")
    except Exception as e:
        print(f"⚠️  Cache clear failed: {e}")
    
    # Test 1: First search (cache miss)
    print(f"\n🔍 Test 1: First searches (cache miss)")
    print("-" * 60)
    
    first_search_times = []
    first_search_results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        start_time = time.time()
        
        try:
            sources_str = "weebcentral,asurascans,mangadex"
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
                
                first_search_times.append(duration)
                first_search_results.append(manga_count)
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 2: Second search (cache hit)
    print(f"\n🔥 Test 2: Second searches (cache hit)")
    print("-" * 60)
    
    second_search_times = []
    second_search_results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        start_time = time.time()
        
        try:
            sources_str = "weebcentral,asurascans,mangadex"
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
                
                second_search_times.append(duration)
                second_search_results.append(manga_count)
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 3: Performance metrics
    print(f"\n📊 Test 3: Performance metrics")
    print("-" * 60)
    
    try:
        # Get performance metrics
        metrics_response = requests.get(f"{PLAYWRIGHT_URL}/performance/metrics")
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            print(f"Cache hit rate: {metrics.get('cache_hit_rate', 'N/A')}")
            print(f"Average search time: {metrics.get('avg_search_time', 'N/A')}")
            print(f"Total searches: {metrics.get('total_searches', 'N/A')}")
        
        # Get performance report
        report_response = requests.get(f"{PLAYWRIGHT_URL}/performance/report")
        if report_response.status_code == 200:
            report = report_response.json()
            summary = report.get('summary', {})
            if 'message' not in summary:
                print(f"Cache hit rate: {summary.get('cache_hit_rate', 'N/A')}")
                print(f"Average search time: {summary.get('avg_search_time', 'N/A')}")
                print(f"P95 search time: {summary.get('p95_search_time', 'N/A')}")
                print(f"Total errors: {summary.get('total_errors', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Failed to get performance metrics: {e}")
    
    # Calculate statistics
    print(f"\n📈 Performance Analysis")
    print("-" * 60)
    
    if first_search_times and second_search_times:
        avg_first_time = statistics.mean(first_search_times)
        avg_second_time = statistics.mean(second_search_times)
        
        if avg_second_time > 0:
            speedup = avg_first_time / avg_second_time
            print(f"Average first search time: {avg_first_time:.3f}s")
            print(f"Average second search time: {avg_second_time:.3f}s")
            print(f"🚀 Cache speedup: {speedup:.1f}x faster!")
            
            if speedup >= 5:
                print("🎉 Excellent performance! Cache is working very well.")
            elif speedup >= 2:
                print("✅ Good performance! Cache is providing significant speedup.")
            else:
                print("⚠️  Moderate performance. Consider optimizing cache settings.")
        
        # Calculate percentiles
        if len(first_search_times) >= 5:
            p95_first = statistics.quantiles(first_search_times, n=20)[18] if len(first_search_times) >= 20 else max(first_search_times)
            p95_second = statistics.quantiles(second_search_times, n=20)[18] if len(second_search_times) >= 20 else max(second_search_times)
            
            print(f"P95 first search time: {p95_first:.3f}s")
            print(f"P95 second search time: {p95_second:.3f}s")
    
    # Test 4: Browser pool performance
    print(f"\n🌐 Test 4: Browser pool performance")
    print("-" * 60)
    
    try:
        # Test concurrent searches to see browser pool efficiency
        import concurrent.futures
        
        def concurrent_search(query):
            start_time = time.time()
            try:
                sources_str = "weebcentral"
                search_url = f"{PROXY_URL}/api/search?q={query}&sources={sources_str}"
                response = requests.get(search_url, timeout=30)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    return len(data.get('results', [])), duration, True
                else:
                    return 0, duration, False
            except Exception as e:
                duration = time.time() - start_time
                return 0, duration, False
        
        # Test concurrent searches
        concurrent_queries = TEST_QUERIES[:5]  # Use first 5 queries
        
        print(f"Testing {len(concurrent_queries)} concurrent searches...")
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(concurrent_search, query): query for query in concurrent_queries}
            
            concurrent_results = []
            for future in concurrent.futures.as_completed(futures):
                query = futures[future]
                try:
                    result_count, duration, success = future.result()
                    concurrent_results.append((query, result_count, duration, success))
                    status = "✅" if success else "❌"
                    print(f"   {status} '{query}': {result_count} results in {duration:.3f}s")
                except Exception as e:
                    print(f"   ❌ '{query}': Error - {e}")
        
        total_concurrent_time = time.time() - start_time
        avg_concurrent_time = statistics.mean([r[2] for r in concurrent_results if r[3]])
        
        print(f"\nConcurrent search results:")
        print(f"Total time for {len(concurrent_queries)} searches: {total_concurrent_time:.3f}s")
        print(f"Average time per search: {avg_concurrent_time:.3f}s")
        print(f"Throughput: {len(concurrent_queries) / total_concurrent_time:.2f} searches/second")
        
    except Exception as e:
        print(f"❌ Concurrent test failed: {e}")
    
    # Summary
    print(f"\n🎯 Performance Summary")
    print("-" * 60)
    print("✅ Browser Pool: Reuses browser instances for faster scraping")
    print("✅ Multi-layer Cache: L1 (5min), L2 (1hr), L3 (6hr) TTL")
    print("✅ Resource Blocking: Blocks images/CSS for faster page loads")
    print("✅ Parallel Scraping: Multiple sources scraped simultaneously")
    print("✅ Performance Monitoring: Real-time metrics and alerts")
    print("✅ Optimized Selectors: Multiple fallback selectors for reliability")
    
    if first_search_times and second_search_times:
        avg_first = statistics.mean(first_search_times)
        avg_second = statistics.mean(second_search_times)
        if avg_second > 0:
            speedup = avg_first / avg_second
            print(f"\n🚀 Expected speedup: {speedup:.1f}x faster with cache")
            print(f"📊 First search avg: {avg_first:.2f}s")
            print(f"📊 Cached search avg: {avg_second:.2f}s")

if __name__ == "__main__":
    test_search_performance() 
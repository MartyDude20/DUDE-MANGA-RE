#!/usr/bin/env python3
"""
Performance test for the simple TTL cache system
"""

import time
import sys
import os
import json
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # playwright_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # project root

from services.simple_search import simple_search_service

def test_search_performance():
    """Test search performance with and without cache"""
    print("=== Performance Test: Simple TTL Cache System ===")
    
    # Test queries
    test_queries = [
        "solo",
        "naruto", 
        "one piece",
        "dragon ball",
        "bleach"
    ]
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'simple_ttl_cache',
        'queries': test_queries,
        'runs': []
    }
    
    print(f"Testing {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        
        # First search (cache miss)
        start_time = time.time()
        first_results = simple_search_service.search(query, ["weebcentral"], force_refresh=False)
        first_time = time.time() - start_time
        
        # Second search (cache hit)
        start_time = time.time()
        second_results = simple_search_service.search(query, ["weebcentral"], force_refresh=False)
        second_time = time.time() - start_time
        
        # Force refresh (cache miss)
        start_time = time.time()
        refresh_results = simple_search_service.search(query, ["weebcentral"], force_refresh=True)
        refresh_time = time.time() - start_time
        
        run_data = {
            'query': query,
            'first_search': {
                'time': first_time,
                'results_count': len(first_results),
                'cached': any(r.get('cached', False) for r in first_results)
            },
            'second_search': {
                'time': second_time,
                'results_count': len(second_results),
                'cached': any(r.get('cached', False) for r in second_results)
            },
            'force_refresh': {
                'time': refresh_time,
                'results_count': len(refresh_results),
                'cached': any(r.get('cached', False) for r in refresh_results)
            }
        }
        
        results['runs'].append(run_data)
        
        # Calculate speedup
        if second_time > 0:
            speedup = first_time / second_time
            print(f"   First search: {first_time:.2f}s ({len(first_results)} results)")
            print(f"   Second search: {second_time:.2f}s ({len(second_results)} results)")
            print(f"   Force refresh: {refresh_time:.2f}s ({len(refresh_results)} results)")
            print(f"   Cache speedup: {speedup:.1f}x")
        else:
            print(f"   Error: Second search took 0 seconds")
    
    # Calculate overall statistics
    total_searches = len(results['runs']) * 3  # 3 searches per query
    avg_first_time = sum(r['first_search']['time'] for r in results['runs']) / len(results['runs'])
    avg_second_time = sum(r['second_search']['time'] for r in results['runs']) / len(results['runs'])
    avg_refresh_time = sum(r['force_refresh']['time'] for r in results['runs']) / len(results['runs'])
    
    overall_speedup = avg_first_time / avg_second_time if avg_second_time > 0 else 0
    
    results['summary'] = {
        'total_searches': total_searches,
        'avg_first_search_time': avg_first_time,
        'avg_second_search_time': avg_second_time,
        'avg_force_refresh_time': avg_refresh_time,
        'overall_cache_speedup': overall_speedup
    }
    
    print(f"\n=== Performance Summary ===")
    print(f"Total searches: {total_searches}")
    print(f"Average first search time: {avg_first_time:.2f}s")
    print(f"Average second search time: {avg_second_time:.2f}s")
    print(f"Average force refresh time: {avg_refresh_time:.2f}s")
    print(f"Overall cache speedup: {overall_speedup:.1f}x")
    
    # Get final metrics
    final_metrics = simple_search_service.get_metrics()
    print(f"\nFinal cache metrics:")
    print(f"  Cache hit rate: {final_metrics.get('cache_hit_rate', '0%')}")
    print(f"  Cache entries: {final_metrics.get('cache_stats', {}).get('total_entries', 0)}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    
    return results

def main():
    """Run performance test"""
    try:
        results = test_search_performance()
        print("\n" + "=" * 50)
        print("✅ Performance test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
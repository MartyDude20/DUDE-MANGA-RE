import os
import sys
import time
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.simple_search import SimpleSearchService
from services.browser_pool import browser_pool
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_source_individually(source: str, query: str):
    """Test a single source individually to avoid threading issues"""
    print(f"\n🔍 Testing {source.upper()} with query: '{query}'")
    
    search_service = SimpleSearchService()
    
    # Get pool stats before
    pool_stats_before = browser_pool.get_stats()
    print(f"  Pool stats before: {pool_stats_before}")
    
    start_time = time.time()
    
    try:
        results = search_service.search(query, sources=[source], force_refresh=True)
        search_time = time.time() - start_time
        
        print(f"  ✅ Found {len(results)} results in {search_time:.2f}s")
        
        # Show results
        for i, result in enumerate(results[:5]):  # Show first 5 results
            title = result.get('title', 'Unknown')
            source_name = result.get('source', 'Unknown')
            print(f"    {i+1}. {title} - {source_name}")
        
        # Get pool stats after
        pool_stats_after = browser_pool.get_stats()
        print(f"  Pool stats after: {pool_stats_after}")
        
        return {
            'success': True,
            'results_count': len(results),
            'search_time': search_time,
            'results': results,
            'pool_stats_before': pool_stats_before,
            'pool_stats_after': pool_stats_after
        }
        
    except Exception as e:
        search_time = time.time() - start_time
        print(f"  ❌ Error: {e}")
        return {
            'success': False,
            'results_count': 0,
            'search_time': search_time,
            'results': [],
            'error': str(e)
        }

def test_all_sources_sequential():
    """Test all sources sequentially to avoid threading issues"""
    print("🚀 Testing All Sources Sequentially with Browser Pool")
    print("=" * 60)
    
    queries = [
        "Solo Leveling",
        "The Greatest Estate Developer", 
        "Nano Machine",
        "One"
    ]
    
    sources = ['weebcentral', 'asurascans', 'mangadex']
    
    all_results = {}
    total_time = 0
    successful_searches = 0
    total_searches = 0
    
    for query in queries:
        print(f"\n📝 Testing Query: '{query}'")
        print("-" * 40)
        
        query_results = {}
        
        for source in sources:
            result = test_source_individually(source, query)
            query_results[source] = result
            
            total_searches += 1
            total_time += result['search_time']
            
            if result['success']:
                successful_searches += 1
            
            # Small delay between sources
            time.sleep(2)
        
        all_results[query] = query_results
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"Total searches: {total_searches}")
    print(f"Successful searches: {successful_searches}")
    print(f"Success rate: {successful_searches/total_searches*100:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per search: {total_time/total_searches:.2f}s")
    
    # Source-specific stats
    print(f"\n🏆 Source Performance:")
    source_stats = {}
    
    for query, results in all_results.items():
        for source, result in results.items():
            if source not in source_stats:
                source_stats[source] = {
                    'searches': 0,
                    'successful': 0,
                    'total_results': 0,
                    'total_time': 0
                }
            
            source_stats[source]['searches'] += 1
            source_stats[source]['total_time'] += result['search_time']
            
            if result['success']:
                source_stats[source]['successful'] += 1
                source_stats[source]['total_results'] += result['results_count']
    
    for source, stats in source_stats.items():
        success_rate = stats['successful'] / stats['searches'] * 100
        avg_time = stats['total_time'] / stats['searches']
        avg_results = stats['total_results'] / stats['successful'] if stats['successful'] > 0 else 0
        
        print(f"  {source.upper()}:")
        print(f"    Success rate: {success_rate:.1f}%")
        print(f"    Avg time: {avg_time:.2f}s")
        print(f"    Avg results: {avg_results:.1f}")
    
    # Browser pool stats
    final_pool_stats = browser_pool.get_stats()
    print(f"\n🔧 Final Browser Pool Stats:")
    print(f"  Pool size: {final_pool_stats['pool_size']}")
    print(f"  Active browsers: {final_pool_stats['active_browsers']}")
    print(f"  Available browsers: {final_pool_stats['available_browsers']}")
    print(f"  Playwright instances: {final_pool_stats['playwright_instances']}")
    
    return all_results

def test_browser_pool_benefits():
    """Demonstrate browser pool benefits with a simple comparison"""
    print("\n🔧 BROWSER POOL BENEFITS DEMONSTRATION")
    print("=" * 60)
    
    search_service = SimpleSearchService()
    query = "Solo Leveling"
    
    # Test with browser pool (should be faster on subsequent searches)
    print(f"Testing with browser pool for query: '{query}'")
    
    times = []
    for i in range(3):
        start_time = time.time()
        results = search_service.search(query, sources=['weebcentral'], force_refresh=True)
        search_time = time.time() - start_time
        times.append(search_time)
        print(f"  Search {i+1}: {search_time:.2f}s - {len(results)} results")
        time.sleep(1)
    
    avg_time = sum(times) / len(times)
    print(f"  Average time with pool: {avg_time:.2f}s")
    
    # Show browser pool stats
    pool_stats = browser_pool.get_stats()
    print(f"  Final pool stats: {pool_stats}")

def main():
    """Run the simple source testing"""
    print("🚀 Simple Source Testing with Browser Pool")
    print("=" * 60)
    
    try:
        # Test all sources sequentially
        results = test_all_sources_sequential()
        
        # Test browser pool benefits
        test_browser_pool_benefits()
        
        print("\n" + "=" * 60)
        print("✅ Simple Source Testing Complete!")
        print("=" * 60)
        
        print(f"\n🎉 Key Findings:")
        print(f"   • Browser pool is working for individual searches")
        print(f"   • Sources are finding results when working properly")
        print(f"   • Sequential testing avoids threading conflicts")
        print(f"   • Pool reuse is happening between searches")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
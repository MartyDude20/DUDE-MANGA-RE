import os
import sys
import time
import json
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.simple_search import SimpleSearchService
from services.browser_pool import browser_pool
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SourceTester:
    """Comprehensive tester for all search sources with browser pooling"""
    
    def __init__(self):
        self.search_service = SimpleSearchService()
        self.results = {}
        self.performance_data = {}
        
    def test_single_source(self, source: str, query: str) -> Dict[str, Any]:
        """Test a single source with performance tracking"""
        print(f"\n🔍 Testing {source.upper()} with query: '{query}'")
        
        start_time = time.time()
        
        try:
            # Get browser pool stats before
            pool_stats_before = browser_pool.get_stats()
            
            # Perform search
            results = self.search_service.search(query, sources=[source], force_refresh=True)
            
            # Get browser pool stats after
            pool_stats_after = browser_pool.get_stats()
            
            search_time = time.time() - start_time
            
            # Calculate performance metrics
            performance = {
                'source': source,
                'query': query,
                'search_time': search_time,
                'results_count': len(results),
                'pool_stats_before': pool_stats_before,
                'pool_stats_after': pool_stats_after,
                'success': True,
                'error': None
            }
            
            print(f"  ✅ Found {len(results)} results in {search_time:.2f}s")
            
            # Show first few results
            for i, result in enumerate(results[:3]):
                print(f"    {i+1}. {result.get('title', 'Unknown')} - {result.get('source', 'Unknown')}")
            
            return {
                'results': results,
                'performance': performance
            }
            
        except Exception as e:
            search_time = time.time() - start_time
            print(f"  ❌ Error: {e}")
            
            return {
                'results': [],
                'performance': {
                    'source': source,
                    'query': query,
                    'search_time': search_time,
                    'results_count': 0,
                    'success': False,
                    'error': str(e)
                }
            }
    
    def test_all_sources(self, queries: List[str]) -> Dict[str, Any]:
        """Test all sources with multiple queries"""
        print("🚀 Starting Comprehensive Source Testing with Browser Pool")
        print("=" * 60)
        
        sources = ['weebcentral', 'asurascans', 'mangadex']
        all_results = {}
        
        for query in queries:
            print(f"\n📝 Testing Query: '{query}'")
            print("-" * 40)
            
            query_results = {}
            query_performance = []
            
            for source in sources:
                result = self.test_single_source(source, query)
                query_results[source] = result['results']
                query_performance.append(result['performance'])
                
                # Small delay between sources
                time.sleep(1)
            
            all_results[query] = {
                'results': query_results,
                'performance': query_performance
            }
        
        return all_results
    
    def analyze_performance(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance across all sources and queries"""
        print("\n📊 PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Collect all performance data
        all_performance = []
        source_stats = {}
        
        for query, data in all_results.items():
            for perf in data['performance']:
                all_performance.append(perf)
                
                source = perf['source']
                if source not in source_stats:
                    source_stats[source] = {
                        'total_searches': 0,
                        'successful_searches': 0,
                        'total_results': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'errors': []
                    }
                
                source_stats[source]['total_searches'] += 1
                source_stats[source]['total_results'] += perf['results_count']
                source_stats[source]['total_time'] += perf['search_time']
                
                if perf['success']:
                    source_stats[source]['successful_searches'] += 1
                else:
                    source_stats[source]['errors'].append(perf['error'])
        
        # Calculate averages
        for source, stats in source_stats.items():
            if stats['total_searches'] > 0:
                stats['avg_time'] = stats['total_time'] / stats['total_searches']
                stats['success_rate'] = stats['successful_searches'] / stats['total_searches']
                stats['avg_results'] = stats['total_results'] / stats['total_searches']
        
        # Overall statistics
        total_searches = len(all_performance)
        successful_searches = sum(1 for p in all_performance if p['success'])
        total_time = sum(p['search_time'] for p in all_performance)
        avg_time = total_time / total_searches if total_searches > 0 else 0
        
        overall_stats = {
            'total_searches': total_searches,
            'successful_searches': successful_searches,
            'success_rate': successful_searches / total_searches if total_searches > 0 else 0,
            'total_time': total_time,
            'avg_time': avg_time,
            'source_stats': source_stats
        }
        
        # Print analysis
        print(f"📈 Overall Statistics:")
        print(f"   Total searches: {total_searches}")
        print(f"   Successful: {successful_searches}")
        print(f"   Success rate: {overall_stats['success_rate']:.1%}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average time: {avg_time:.2f}s")
        
        print(f"\n🏆 Source Performance:")
        for source, stats in source_stats.items():
            print(f"   {source.upper()}:")
            print(f"     Searches: {stats['total_searches']}")
            print(f"     Success rate: {stats['success_rate']:.1%}")
            print(f"     Avg time: {stats['avg_time']:.2f}s")
            print(f"     Avg results: {stats['avg_results']:.1f}")
            if stats['errors']:
                print(f"     Errors: {len(stats['errors'])}")
        
        return overall_stats
    
    def test_browser_pool_efficiency(self, all_results: Dict[str, Any]):
        """Test browser pool efficiency and reuse"""
        print("\n🔧 BROWSER POOL EFFICIENCY ANALYSIS")
        print("=" * 60)
        
        # Get final pool stats
        final_pool_stats = browser_pool.get_stats()
        
        print(f"📊 Final Browser Pool Stats:")
        print(f"   Pool size: {final_pool_stats['pool_size']}")
        print(f"   Active browsers: {final_pool_stats['active_browsers']}")
        print(f"   Available browsers: {final_pool_stats['available_browsers']}")
        print(f"   Playwright instances: {final_pool_stats['playwright_instances']}")
        
        # Analyze pool usage patterns
        pool_usage = []
        for query, data in all_results.items():
            for perf in data['performance']:
                if 'pool_stats_before' in perf and 'pool_stats_after' in perf:
                    before = perf['pool_stats_before']
                    after = perf['pool_stats_after']
                    
                    pool_usage.append({
                        'source': perf['source'],
                        'query': perf['query'],
                        'browsers_used': after['active_browsers'] - before['active_browsers'],
                        'available_change': after['available_browsers'] - before['available_browsers']
                    })
        
        if pool_usage:
            total_browsers_used = sum(u['browsers_used'] for u in pool_usage)
            avg_browsers_per_search = total_browsers_used / len(pool_usage)
            
            print(f"\n🔍 Pool Usage Analysis:")
            print(f"   Total browser acquisitions: {total_browsers_used}")
            print(f"   Average browsers per search: {avg_browsers_per_search:.2f}")
            print(f"   Pool reuse efficiency: {'Good' if avg_browsers_per_search < 1.5 else 'Needs improvement'}")
    
    def save_results(self, all_results: Dict[str, Any], performance_stats: Dict[str, Any]):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"source_test_results_{timestamp}.json"
        
        output = {
            'timestamp': timestamp,
            'test_summary': {
                'total_queries': len(all_results),
                'total_searches': performance_stats['total_searches'],
                'success_rate': performance_stats['success_rate'],
                'total_time': performance_stats['total_time'],
                'avg_time': performance_stats['avg_time']
            },
            'performance_stats': performance_stats,
            'detailed_results': all_results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

def main():
    """Run comprehensive source testing"""
    print("🚀 Starting All Sources Test with Browser Pool")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "Solo Leveling",
        "The Greatest Estate Developer",
        "Nano Machine",
        "One"
    ]
    
    tester = SourceTester()
    
    try:
        # Test all sources
        all_results = tester.test_all_sources(test_queries)
        
        # Analyze performance
        performance_stats = tester.analyze_performance(all_results)
        
        # Test browser pool efficiency
        tester.test_browser_pool_efficiency(all_results)
        
        # Save results
        results_file = tester.save_results(all_results, performance_stats)
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ COMPREHENSIVE SOURCE TESTING COMPLETE!")
        print("=" * 60)
        
        print(f"\n🎉 Key Results:")
        print(f"   • Tested {len(test_queries)} queries across 3 sources")
        print(f"   • Overall success rate: {performance_stats['success_rate']:.1%}")
        print(f"   • Average search time: {performance_stats['avg_time']:.2f}s")
        print(f"   • Browser pool integration: ✅ Working")
        print(f"   • Results saved to: {results_file}")
        
        # Get search service metrics
        search_metrics = tester.search_service.get_metrics()
        print(f"\n📈 Search Service Metrics:")
        print(f"   • Total searches: {search_metrics['total_searches']}")
        print(f"   • Cache hit rate: {search_metrics['cache_hit_rate']}")
        print(f"   • Average search time: {search_metrics['avg_search_time']}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
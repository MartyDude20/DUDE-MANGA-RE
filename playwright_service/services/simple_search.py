import os
import sys
import time
import concurrent.futures
from typing import List, Dict, Optional
import logging
from playwright.sync_api import sync_playwright

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources import weebcentral, asurascans, mangadex
from services.simple_cache import search_cache

logger = logging.getLogger(__name__)

class SimpleSearchService:
    """Simplified search service using TTL cache instead of complex preloader"""
    
    def __init__(self):
        self.sources = {
            'weebcentral': weebcentral,
            'asurascans': asurascans,
            'mangadex': mangadex
        }
        
        # Performance metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_searches': 0,
            'avg_search_time': 0.0
        }
    
    def search(self, query: str, sources: Optional[List[str]] = None, force_refresh: bool = False) -> List[Dict]:
        """
        Search for manga with simple TTL caching
        
        Args:
            query: Search query string
            sources: List of sources to search (defaults to all)
            force_refresh: Force scraping instead of using cache
            
        Returns:
            List of manga results with cache info
        """
        start_time = time.time()
        self.metrics['total_searches'] += 1
        
        if sources is None:
            sources = list(self.sources.keys())
        
        # Create cache key
        cache_key = f"search:{query.lower().strip()}:{','.join(sorted(sources))}"
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_results = search_cache.get(cache_key)
            if cached_results and isinstance(cached_results, list):
                self.metrics['cache_hits'] += 1
                search_time = time.time() - start_time
                self._update_avg_time(search_time)
                
                logger.info(f"Cache HIT for '{query}' - {len(cached_results)} results in {search_time:.2f}s")
                return self._add_cache_info(cached_results, True)
        
        # Cache miss - scrape fresh data
        self.metrics['cache_misses'] += 1
        logger.info(f"Cache MISS for '{query}' - scraping fresh data")
        
        fresh_results = self._scrape_search(query, sources)
        
        # Cache the results for 6 hours
        search_cache.set(cache_key, fresh_results)
        
        search_time = time.time() - start_time
        self._update_avg_time(search_time)
        
        logger.info(f"Fresh search for '{query}' - {len(fresh_results)} results in {search_time:.2f}s")
        return self._add_cache_info(fresh_results, False)
    
    def _scrape_search(self, query: str, sources: List[str]) -> List[Dict]:
        """Scrape search results from sources"""
        all_results = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {}
            
            for source in sources:
                if source in self.sources:
                    future = executor.submit(self._scrape_source, query, source)
                    future_to_source[future] = source
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results = future.result()
                    if results:
                        all_results.extend(results)
                        logger.debug(f"Got {len(results)} results from {source}")
                except Exception as e:
                    logger.error(f"Error scraping {source}: {e}")
        
        return all_results
    
    def _scrape_source(self, query: str, source: str) -> List[Dict]:
        """Scrape a single source"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                source_module = self.sources[source]
                results = source_module.search(page, query)
                
                # Add source information to results
                for result in results:
                    result['source'] = source
                    result['cached'] = False
                
                browser.close()
                return results
                
        except Exception as e:
            logger.error(f"Failed to scrape {source}: {e}")
            return []
    
    def _add_cache_info(self, results: List[Dict], from_cache: bool) -> List[Dict]:
        """Add cache information to results"""
        for result in results:
            result['cached'] = from_cache
            result['cache_timestamp'] = int(time.time()) if from_cache else None
        
        return results
    
    def _update_avg_time(self, search_time: float) -> None:
        """Update average search time metric"""
        total = self.metrics['total_searches']
        current_avg = self.metrics['avg_search_time']
        
        # Calculate running average
        self.metrics['avg_search_time'] = (current_avg * (total - 1) + search_time) / total
    
    def get_metrics(self) -> Dict:
        """Get search performance metrics"""
        cache_hit_rate = 0
        if self.metrics['total_searches'] > 0:
            cache_hit_rate = self.metrics['cache_hits'] / self.metrics['total_searches']
        
        return {
            'total_searches': self.metrics['total_searches'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.2%}",
            'avg_search_time': f"{self.metrics['avg_search_time']:.2f}s",
            'cache_stats': search_cache.get_stats()
        }
    
    def clear_cache(self) -> None:
        """Clear the search cache"""
        search_cache.clear()
        logger.info("Search cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return search_cache.get_stats()

# Global search service instance
simple_search_service = SimpleSearchService() 
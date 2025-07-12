import os
import sys
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, PreloadedManga
from sources import weebcentral, asurascans, mangadex
from playwright.sync_api import sync_playwright
from flask import current_app
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchService:
    """High-performance service for searching manga with preloaded data fallback"""
    
    def __init__(self):
        self.sources = {
            'weebcentral': weebcentral,
            'asurascans': asurascans,
            'mangadex': mangadex
        }
        
        # Connection pool for database operations
        self._session_pool = None
        
        # Cache for recent searches (in-memory)
        self._search_cache = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = 300  # 5 minutes
        
        # Performance metrics
        self._metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_search_time': 0,
            'total_searches': 0
        }
    
    def search(self, query: str, sources: List[str] = None, force_refresh: bool = False) -> List[Dict]:
        """
        High-performance search for manga across sources
        
        Args:
            query: Search query string
            sources: List of sources to search (defaults to all)
            force_refresh: Force scraping instead of using cache
            
        Returns:
            List of manga results
        """
        start_time = time.time()
        
        if not sources:
            sources = list(self.sources.keys())
        
        normalized_query = PreloadedManga.normalize_title(query)
        results = []
        
        # Check in-memory cache first (fastest)
        cache_key = f"{normalized_query}:{','.join(sorted(sources))}"
        if not force_refresh:
            cached_results = self._get_from_cache(cache_key)
            if cached_results:
                self._metrics['cache_hits'] += 1
                self._update_metrics(time.time() - start_time)
                return cached_results
        
        self._metrics['cache_misses'] += 1
        
        if not force_refresh:
            # Try preloaded database cache (fast)
            db_results = self._search_preloaded_data(normalized_query, sources)
            if db_results:
                results.extend(db_results)
                
                # If we have enough results, return them
                if len(results) >= 10:
                    self._cache_results(cache_key, results)
                    self._update_metrics(time.time() - start_time)
                    return results
        
        # Fall back to parallel scraping (slow but necessary)
        scraped_results = self._parallel_scrape_search(query, sources)
        results.extend(scraped_results)
        
        # Remove duplicates and cache results
        unique_results = self._deduplicate_results(results)
        self._cache_results(cache_key, unique_results)
        
        # Save new results to database in background
        if scraped_results:
            self._save_to_preloaded_async(scraped_results)
        
        self._update_metrics(time.time() - start_time)
        return unique_results
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Get results from in-memory cache"""
        with self._cache_lock:
            if cache_key in self._search_cache:
                cache_entry = self._search_cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                    return cache_entry['results']
                else:
                    del self._search_cache[cache_key]
        return None
    
    def _cache_results(self, cache_key: str, results: List[Dict]):
        """Cache results in memory"""
        with self._cache_lock:
            self._search_cache[cache_key] = {
                'results': results,
                'timestamp': time.time()
            }
            # Limit cache size
            if len(self._search_cache) > 1000:
                # Remove oldest entries
                oldest_key = min(self._search_cache.keys(), 
                               key=lambda k: self._search_cache[k]['timestamp'])
                del self._search_cache[oldest_key]
    
    def _search_preloaded_data(self, normalized_query: str, sources: List[str]) -> List[Dict]:
        """Search preloaded database data with optimized queries"""
        try:
            with current_app.app_context():
                # Use optimized query with proper indexing
                db_results = PreloadedManga.query.filter(
                    and_(
                        or_(
                            PreloadedManga.normalized_title.contains(normalized_query),
                            PreloadedManga.title.ilike(f'%{normalized_query}%')
                        ),
                        PreloadedManga.source.in_(sources),
                        PreloadedManga.last_updated > datetime.utcnow() - timedelta(days=7)
                    )
                ).order_by(
                    PreloadedManga.popularity.desc(),
                    PreloadedManga.last_accessed.desc()
                ).limit(50).all()
                
                if not db_results:
                    return []
                
                # Update access times in bulk
                manga_ids = [m.id for m in db_results]
                PreloadedManga.query.filter(PreloadedManga.id.in_(manga_ids)).update(
                    {
                        PreloadedManga.last_accessed: datetime.utcnow(),
                        PreloadedManga.popularity: PreloadedManga.popularity + 1
                    },
                    synchronize_session=False
                )
                db.session.commit()
                
                # Convert to result format
                results = []
                for manga in db_results:
                    results.append({
                        'id': self._extract_manga_id(manga.source_url, manga.source),
                        'title': manga.title,
                        'status': manga.status or '',
                        'chapter': f"{len(manga.chapters or [])} chapters" if manga.chapters else '',
                        'image': manga.cover_url,
                        'details_url': manga.source_url,
                        'source': manga.source,
                        'cached': True,
                        'last_updated': manga.last_updated.isoformat() if manga.last_updated else None
                    })
                
                logger.info(f"Found {len(results)} cached results for '{normalized_query}'")
                return results
                
        except Exception as e:
            logger.error(f"Error searching preloaded data: {e}")
            db.session.rollback()
        
        return []
    
    def _parallel_scrape_search(self, query: str, sources: List[str]) -> List[Dict]:
        """Perform parallel scraping across multiple sources"""
        results = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
            # Submit scraping tasks
            future_to_source = {
                executor.submit(self._scrape_single_source, query, source): source 
                for source in sources if source in self.sources
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    source_results = future.result()
                    if source_results:
                        results.extend(source_results)
                        logger.info(f"Scraped {len(source_results)} results from {source}")
                except Exception as e:
                    logger.error(f"Scraping failed for {source}: {e}")
        
        return results
    
    def _scrape_single_source(self, query: str, source: str) -> List[Dict]:
        """Scrape a single source with thread-safe browser creation"""
        try:
            # Create a new Playwright context for this thread (thread-safe)
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                page = browser.new_page()
                
                # Set page optimizations
                page.set_viewport_size({"width": 1280, "height": 720})
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                source_module = self.sources[source]
                source_results = source_module.search(page, query)
                
                # Add metadata
                for result in source_results:
                    result['cached'] = False
                    result['source'] = source
                
                page.close()
                browser.close()
                return source_results
            
        except Exception as e:
            logger.error(f"Single source scraping failed for {source}: {e}")
            return []
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on source_url"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('details_url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _save_to_preloaded_async(self, results: List[Dict]):
        """Save results to database asynchronously"""
        def save_async():
            try:
                with current_app.app_context():
                    # Bulk insert/update
                    for result in results:
                        if not result.get('details_url'):
                            continue
                            
                        existing = PreloadedManga.query.filter_by(
                            source_url=result.get('details_url')
                        ).first()
                        
                        if existing:
                            # Update existing
                            existing.last_updated = datetime.utcnow()
                            existing.popularity += 1
                        else:
                            # Create new
                            manga = PreloadedManga(
                                title=result.get('title', 'Unknown'),
                                normalized_title=PreloadedManga.normalize_title(result.get('title', '')),
                                source_url=result.get('details_url'),
                                cover_url=result.get('image'),
                                source=result.get('source'),
                                status=result.get('status'),
                                last_updated=datetime.utcnow(),
                                popularity=1,
                                last_accessed=datetime.utcnow()
                            )
                            db.session.add(manga)
                    
                    db.session.commit()
                    logger.info(f"Saved {len(results)} results to preloaded data")
                    
            except Exception as e:
                logger.error(f"Failed to save to preloaded data: {e}")
                db.session.rollback()
        
        # Run in background thread
        threading.Thread(target=save_async, daemon=True).start()
    
    def _update_metrics(self, search_time: float):
        """Update performance metrics"""
        self._metrics['total_searches'] += 1
        self._metrics['avg_search_time'] = (
            (self._metrics['avg_search_time'] * (self._metrics['total_searches'] - 1) + search_time) 
            / self._metrics['total_searches']
        )
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        cache_hit_rate = 0
        if self._metrics['total_searches'] > 0:
            cache_hit_rate = (self._metrics['cache_hits'] / 
                            (self._metrics['cache_hits'] + self._metrics['cache_misses'])) * 100
        
        return {
            'total_searches': self._metrics['total_searches'],
            'cache_hits': self._metrics['cache_hits'],
            'cache_misses': self._metrics['cache_misses'],
            'cache_hit_rate': cache_hit_rate,
            'avg_search_time': self._metrics['avg_search_time'],
            'active_browsers': 0, # No longer tracking browsers
            'cache_size': len(self._search_cache)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        # No longer managing browser pool, so no cleanup needed here
        
        # Clear old cache entries
        current_time = time.time()
        with self._cache_lock:
            expired_keys = [
                k for k, v in self._search_cache.items() 
                if current_time - v['timestamp'] > self._cache_ttl
            ]
            for key in expired_keys:
                del self._search_cache[key]
    
    def _extract_manga_id(self, url: str, source: str) -> Optional[str]:
        """Extract manga ID from URL based on source"""
        try:
            if source == 'weebcentral':
                parts = url.split('/')
                if 'series' in parts:
                    idx = parts.index('series')
                    return parts[idx + 1] if idx + 1 < len(parts) else None
            
            elif source == 'asurascans':
                parts = url.split('/')
                return parts[-1] or parts[-2]
            
            elif source == 'mangadex':
                import re
                match = re.search(r'/title/([a-f0-9-]+)', url)
                return match.group(1) if match else None
                
        except Exception as e:
            logger.error(f"Failed to extract manga ID from {url}: {e}")
        
        return url  # Fallback to full URL if ID extraction fails
    
    def get_manga_details(self, manga_id: str, source: str, force_refresh: bool = False) -> Optional[Dict]:
        """Get manga details with caching"""
        if not force_refresh:
            try:
                with current_app.app_context():
                    manga = PreloadedManga.query.filter(
                        and_(
                            PreloadedManga.source == source,
                            PreloadedManga.source_url.contains(manga_id)
                        )
                    ).first()
                    
                    if manga and manga.chapters:
                        manga.last_accessed = datetime.utcnow()
                        manga.popularity += 1
                        db.session.commit()
                        
                        return {
                            'id': manga_id,
                            'title': manga.title,
                            'image': manga.cover_url,
                            'description': manga.description,
                            'author': manga.author,
                            'status': manga.status,
                            'chapters': manga.chapters,
                            'url': manga.source_url,
                            'source': manga.source,
                            'cached': True,
                            'last_updated': manga.last_updated.isoformat() if manga.last_updated else None
                        }
            
            except Exception as e:
                logger.error(f"Error getting preloaded manga details: {e}")
        
        # Fall back to scraping
        return self._scrape_manga_details(manga_id, source)
    
    def _scrape_manga_details(self, manga_id: str, source: str) -> Optional[Dict]:
        """Scrape manga details from source"""
        try:
            # Create a new Playwright context for this thread (thread-safe)
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                page = browser.new_page()
                source_module = self.sources.get(source)
                if not source_module:
                    return None
                
                details = source_module.get_details(page, manga_id)
                page.close()
                browser.close()
                
                if details:
                    details['cached'] = False
                    # Save to preloaded data in background
                    threading.Thread(
                        target=self._save_manga_details_async, 
                        args=(details, source), 
                        daemon=True
                    ).start()
                
                return details
                
        except Exception as e:
            logger.error(f"Failed to scrape manga details: {e}")
            return None
    
    def _save_manga_details_async(self, details: Dict, source: str):
        """Save manga details asynchronously"""
        try:
            with current_app.app_context():
                manga = PreloadedManga.query.filter_by(
                    source_url=details.get('url')
                ).first()
                
                if manga:
                    manga.description = details.get('description', manga.description)
                    manga.author = details.get('author', manga.author)
                    manga.status = details.get('status', manga.status)
                    manga.chapters = details.get('chapters', manga.chapters)
                    manga.last_updated = datetime.utcnow()
                else:
                    manga = PreloadedManga(
                        title=details.get('title', 'Unknown'),
                        normalized_title=PreloadedManga.normalize_title(details.get('title', '')),
                        source_url=details.get('url'),
                        cover_url=details.get('image'),
                        description=details.get('description'),
                        author=details.get('author'),
                        status=details.get('status'),
                        chapters=details.get('chapters'),
                        source=source,
                        last_updated=datetime.utcnow(),
                        popularity=1,
                        last_accessed=datetime.utcnow()
                    )
                    db.session.add(manga)
                
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Failed to save manga details: {e}")
            db.session.rollback()

# Create singleton instance
search_service = SearchService() 
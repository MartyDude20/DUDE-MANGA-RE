import sqlite3
import json
import os
import random
import time
import requests
import threading
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from models import db, PreloadJob, PreloadStats, RobotsTxtCache
from sources import weebcentral, asurascans, mangadex
from cache_manager import CacheManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreloadManager:
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.running = False
        self.worker_thread = None
        
        # Source configurations with rate limits and delays
        self.source_configs = {
            'weebcentral': {
                'base_delay': 2.0,  # seconds between requests
                'crawl_delay': 1.0,  # from robots.txt
                'max_requests_per_hour': 100,
                'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
                'domain': 'weebcentral.com'
            },
            'asurascans': {
                'base_delay': 3.0,
                'crawl_delay': 2.0,
                'max_requests_per_hour': 50,
                'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
                'domain': 'asura.gg'
            },
            'mangadex': {
                'base_delay': 1.0,
                'crawl_delay': 0.5,
                'max_requests_per_hour': 200,
                'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
                'domain': 'api.mangadex.org'
            }
        }
        
        # Popular search terms for preloading
        self.popular_searches = [
            'one piece', 'naruto', 'dragon ball', 'bleach', 'attack on titan',
            'my hero academia', 'demon slayer', 'jujutsu kaisen', 'spy x family',
            'chainsaw man', 'tokyo ghoul', 'death note', 'fullmetal alchemist',
            'hunter x hunter', 'fairy tail', 'black clover', 'seven deadly sins',
            'sword art online', 're:zero', 'overlord', 'that time i got reincarnated',
            'konosuba', 'no game no life', 'log horizon', 'shield hero'
        ]
        
        # Initialize robots.txt cache (only when needed)
        # self.init_robots_txt_cache()
    
    def init_robots_txt_cache(self):
        """Initialize robots.txt cache for all sources"""
        for source, config in self.source_configs.items():
            domain = config['domain']
            existing = RobotsTxtCache.query.filter_by(domain=domain).first()
            if not existing:
                self.update_robots_txt_cache(domain)
    
    def update_robots_txt_cache(self, domain: str) -> bool:
        """Fetch and cache robots.txt for a domain"""
        try:
            robots_url = f"https://{domain}/robots.txt"
            response = requests.get(robots_url, timeout=10, 
                                  headers={'User-Agent': 'MangaReader/1.0'})
            
            if response.status_code == 200:
                robots_content = response.text
                crawl_delay = self.parse_robots_txt(robots_content)
                
                # Update or create cache entry
                cache_entry = RobotsTxtCache.query.filter_by(domain=domain).first()
                if cache_entry:
                    cache_entry.robots_content = robots_content
                    cache_entry.crawl_delay = crawl_delay
                    cache_entry.last_updated = datetime.utcnow()
                else:
                    cache_entry = RobotsTxtCache(
                        domain=domain,
                        robots_content=robots_content,
                        crawl_delay=crawl_delay,
                        user_agent='MangaReader/1.0',
                        is_allowed=True
                    )
                    db.session.add(cache_entry)
                
                db.session.commit()
                logger.info(f"Updated robots.txt cache for {domain}")
                return True
            else:
                logger.warning(f"Failed to fetch robots.txt for {domain}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating robots.txt cache for {domain}: {e}")
            return False
    
    def parse_robots_txt(self, robots_content: str) -> float:
        """Parse robots.txt content to extract crawl delay"""
        try:
            lines = robots_content.lower().split('\n')
            for line in lines:
                if line.startswith('crawl-delay:'):
                    delay = float(line.split(':', 1)[1].strip())
                    return max(delay, 0.5)  # Minimum 0.5 seconds
        except:
            pass
        return 1.0  # Default delay
    
    def get_respectful_delay(self, source: str) -> float:
        """Get a respectful delay for a source, including randomization"""
        config = self.source_configs.get(source, {})
        base_delay = config.get('base_delay', 2.0)
        crawl_delay = config.get('crawl_delay', 1.0)
        
        # Use the maximum of base delay and robots.txt crawl delay
        min_delay = max(base_delay, crawl_delay)
        
        # Add randomization (±20%)
        random_factor = random.uniform(0.8, 1.2)
        delay = min_delay * random_factor
        
        return delay
    
    def create_daily_preload_jobs(self):
        """Create daily preload jobs for all sources"""
        tomorrow = datetime.now() + timedelta(days=1)
        scheduled_time = tomorrow.replace(hour=random.randint(2, 6), 
                                        minute=random.randint(0, 59),
                                        second=0, microsecond=0)
        
        jobs_created = 0
        
        # Create search preload jobs
        for source in self.source_configs.keys():
            if source == 'asurascans':
                # For AsuraScans, create a pagination job instead of search jobs
                job = PreloadJob(
                    job_type='asurascans_pagination',
                    source=source,
                    target_id='50',  # Max 50 pages
                    status='pending',
                    priority=random.randint(1, 10),
                    scheduled_at=scheduled_time
                )
                db.session.add(job)
                jobs_created += 1
            else:
                # For other sources, use search terms
                for search_term in random.sample(self.popular_searches, 5):  # Random 5 searches per source
                    job = PreloadJob(
                        job_type='search',
                        source=source,
                        target_id=search_term,
                        status='pending',
                        priority=random.randint(1, 10),
                        scheduled_at=scheduled_time
                    )
                    db.session.add(job)
                    jobs_created += 1
        
        # Create manga details preload jobs (based on recent searches)
        recent_searches = self.get_recent_popular_searches()
        for search_result in recent_searches[:10]:  # Top 10 recent popular manga
            job = PreloadJob(
                job_type='manga_details',
                source=search_result['source'],
                target_id=search_result['manga_id'],
                status='pending',
                priority=random.randint(1, 8),
                scheduled_at=scheduled_time
            )
            db.session.add(job)
            jobs_created += 1
        
        # Create chapter images preload jobs (for recent manga)
        recent_manga = self.get_recent_popular_manga()
        for manga in recent_manga[:5]:  # Top 5 recent popular manga
            chapters = manga.get('chapters', [])
            if chapters:
                # Preload first 2 chapters
                for chapter in chapters[:2]:
                    job = PreloadJob(
                        job_type='chapter_images',
                        source=manga['source'],
                        target_id=chapter['url'],
                        status='pending',
                        priority=random.randint(1, 6),
                        scheduled_at=scheduled_time
                    )
                    db.session.add(job)
                    jobs_created += 1
        
        db.session.commit()
        logger.info(f"Created {jobs_created} daily preload jobs for {scheduled_time}")
        return jobs_created
    
    def get_recent_popular_searches(self) -> List[Dict]:
        """Get recent popular search results from cache"""
        try:
            with sqlite3.connect(self.cache_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT query, source, results, created_at 
                    FROM search_cache 
                    WHERE created_at > datetime('now', '-7 days')
                    ORDER BY created_at DESC
                    LIMIT 50
                ''')
                
                results = []
                for row in cursor.fetchall():
                    query, source, results_json, created_at = row
                    try:
                        search_results = json.loads(results_json)
                        for result in search_results:
                            results.append({
                                'source': source,
                                'manga_id': result.get('id', ''),
                                'title': result.get('title', ''),
                                'created_at': created_at
                            })
                    except:
                        continue
                
                return results
        except Exception as e:
            logger.error(f"Error getting recent popular searches: {e}")
            return []
    
    def get_recent_popular_manga(self) -> List[Dict]:
        """Get recent popular manga from cache"""
        try:
            with sqlite3.connect(self.cache_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT manga_id, source, title, chapters, last_updated 
                    FROM manga_cache 
                    WHERE last_updated > datetime('now', '-7 days')
                    ORDER BY last_updated DESC
                    LIMIT 20
                ''')
                
                results = []
                for row in cursor.fetchall():
                    manga_id, source, title, chapters_json, last_updated = row
                    try:
                        chapters = json.loads(chapters_json) if chapters_json else []
                        results.append({
                            'source': source,
                            'manga_id': manga_id,
                            'title': title,
                            'chapters': chapters,
                            'last_updated': last_updated
                        })
                    except:
                        continue
                
                return results
        except Exception as e:
            logger.error(f"Error getting recent popular manga: {e}")
            return []
    
    def start_preload_worker(self):
        """Start the preload worker thread"""
        if self.running:
            logger.warning("Preload worker is already running")
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._preload_worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Preload worker started")
    
    def stop_preload_worker(self):
        """Stop the preload worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Preload worker stopped")
    
    def _preload_worker_loop(self):
        """Main worker loop for processing preload jobs"""
        while self.running:
            try:
                # Get pending jobs that are due
                pending_jobs = PreloadJob.query.filter(
                    PreloadJob.status == 'pending',
                    PreloadJob.scheduled_at <= datetime.utcnow()
                ).order_by(PreloadJob.priority, PreloadJob.scheduled_at).limit(5).all()
                
                for job in pending_jobs:
                    if not self.running:
                        break
                    
                    self._process_job(job)
                    
                    # Respectful delay between jobs
                    delay = self.get_respectful_delay(job.source)
                    time.sleep(delay)
                
                # Sleep for a bit before checking for more jobs
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in preload worker loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _process_job(self, job: PreloadJob):
        """Process a single preload job"""
        start_time = time.time()
        
        try:
            job.status = 'running'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Processing job: {job.job_type} for {job.source} - {job.target_id}")
            
            if job.job_type == 'search':
                success = self._preload_search(job.source, job.target_id)
            elif job.job_type == 'manga_details':
                success = self._preload_manga_details(job.source, job.target_id)
            elif job.job_type == 'chapter_images':
                success = self._preload_chapter_images(job.source, job.target_id)
            elif job.job_type == 'asurascans_pagination':
                # For pagination jobs, target_id contains max_pages as string
                max_pages = int(job.target_id) if job.target_id.isdigit() else 50
                success = self._preload_asurascans_pagination(max_pages)
            else:
                logger.error(f"Unknown job type: {job.job_type}")
                success = False
            
            # Update job status
            job.completed_at = datetime.utcnow()
            if success:
                job.status = 'completed'
            else:
                job.status = 'failed'
                job.error_message = "Job failed"
            
            # Update statistics
            self._update_stats(job, time.time() - start_time, success)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error processing job {job.id}: {e}")
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
    
    def _preload_search(self, source: str, query: str) -> bool:
        """Preload search results"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': self.source_configs[source]['user_agent']
                })
                
                source_module = self._get_source_module(source)
                if not source_module:
                    return False
                
                results = source_module.search(page, query)
                
                # Cache results for anonymous users (global cache)
                self.cache_manager.cache_search_results(query, source, results, user_id=None)
                
                page.close()
                browser.close()
                
                logger.info(f"Preloaded search: {query} for {source} - {len(results)} results")
                return True
                
        except Exception as e:
            logger.error(f"Error preloading search {query} for {source}: {e}")
            return False

    def _preload_asurascans_pagination(self, max_pages: int = 50) -> bool:
        """Preload all AsuraScans manga using pagination"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': self.source_configs['asurascans']['user_agent']
                })
                
                # Get all manga from pagination
                all_manga = asurascans.get_all_manga_from_pagination(page, max_pages)
                
                if not all_manga:
                    logger.warning("No manga found during AsuraScans pagination preload")
                    return False
                
                # Cache all manga as search results with a special key
                cache_key = "asurascans_all_manga"
                self.cache_manager.cache_search_results(cache_key, 'asurascans', all_manga, user_id=None)
                
                # Also cache individual manga details for popular ones
                popular_manga = all_manga[:20]  # Cache details for first 20 manga
                for manga in popular_manga:
                    try:
                        # Add delay between requests
                        time.sleep(self.get_respectful_delay('asurascans'))
                        
                        details = asurascans.get_details(page, manga['id'])
                        self.cache_manager.cache_manga_details(manga['id'], 'asurascans', details, user_id=None)
                        
                        logger.info(f"Preloaded details for AsuraScans manga: {manga['title']}")
                        
                    except Exception as e:
                        logger.error(f"Error preloading details for {manga['id']}: {e}")
                        continue
                
                page.close()
                browser.close()
                
                logger.info(f"Preloaded AsuraScans pagination: {len(all_manga)} total manga, {len(popular_manga)} detailed")
                return True
                
        except Exception as e:
            logger.error(f"Error preloading AsuraScans pagination: {e}")
            return False
    
    def _preload_manga_details(self, source: str, manga_id: str) -> bool:
        """Preload manga details"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': self.source_configs[source]['user_agent']
                })
                
                source_module = self._get_source_module(source)
                if not source_module:
                    return False
                
                details = source_module.get_details(page, manga_id)
                
                # Cache details for anonymous users (global cache)
                self.cache_manager.cache_manga_details(manga_id, source, details, user_id=None)
                
                page.close()
                browser.close()
                
                logger.info(f"Preloaded manga details: {manga_id} for {source}")
                return True
                
        except Exception as e:
            logger.error(f"Error preloading manga details {manga_id} for {source}: {e}")
            return False
    
    def _preload_chapter_images(self, source: str, chapter_url: str) -> bool:
        """Preload chapter images"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': self.source_configs[source]['user_agent']
                })
                
                source_module = self._get_source_module(source)
                if not source_module:
                    return False
                
                # Get chapter images
                if source == 'mangadex':
                    # For MangaDex, extract UUID from URL
                    import re
                    uuid_match = re.search(r'/([a-f0-9-]{36})', chapter_url)
                    if uuid_match:
                        chapter_uuid = uuid_match.group(1)
                        images = source_module.get_chapter_images(page, chapter_uuid)
                    else:
                        logger.error(f"Invalid MangaDex chapter URL: {chapter_url}")
                        return False
                else:
                    images = source_module.get_chapter_images(page, chapter_url)
                
                # Cache images for anonymous users (global cache)
                self.cache_manager.cache_chapter_images(chapter_url, source, images, user_id=None)
                
                page.close()
                browser.close()
                
                logger.info(f"Preloaded chapter images: {chapter_url} for {source} - {len(images)} images")
                return True
                
        except Exception as e:
            logger.error(f"Error preloading chapter images {chapter_url} for {source}: {e}")
            return False
    
    def _get_source_module(self, source: str):
        """Get the source module for a given source"""
        source_modules = {
            'weebcentral': weebcentral,
            'asurascans': asurascans,
            'mangadex': mangadex
        }
        return source_modules.get(source)
    
    def _update_stats(self, job: PreloadJob, response_time: float, success: bool):
        """Update preload statistics"""
        today = date.today()
        
        stats = PreloadStats.query.filter_by(
            source=job.source,
            job_type=job.job_type,
            date=today
        ).first()
        
        if not stats:
            stats = PreloadStats(
                source=job.source,
                job_type=job.job_type,
                date=today
            )
            db.session.add(stats)
        
        stats.total_jobs += 1
        if success:
            stats.successful_jobs += 1
        else:
            stats.failed_jobs += 1
            stats.total_errors += 1
        
        # Update average response time
        if stats.avg_response_time is None:
            stats.avg_response_time = response_time
        else:
            stats.avg_response_time = (stats.avg_response_time + response_time) / 2
    
    def get_preload_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get preload statistics for the last N days"""
        try:
            start_date = date.today() - timedelta(days=days)
            
            stats = PreloadStats.query.filter(
                PreloadStats.date >= start_date
            ).all()
            
            # Group by source and job type
            result = {}
            for stat in stats:
                key = f"{stat.source}_{stat.job_type}"
                if key not in result:
                    result[key] = {
                        'source': stat.source,
                        'job_type': stat.job_type,
                        'total_jobs': 0,
                        'successful_jobs': 0,
                        'failed_jobs': 0,
                        'total_errors': 0,
                        'avg_response_time': 0,
                        'success_rate': 0
                    }
                
                result[key]['total_jobs'] += stat.total_jobs
                result[key]['successful_jobs'] += stat.successful_jobs
                result[key]['failed_jobs'] += stat.failed_jobs
                result[key]['total_errors'] += stat.total_errors
                
                # Calculate weighted average response time
                if stat.total_jobs > 0:
                    weight = stat.total_jobs / result[key]['total_jobs']
                    result[key]['avg_response_time'] += stat.avg_response_time * weight
            
            # Calculate success rates
            for key in result:
                if result[key]['total_jobs'] > 0:
                    result[key]['success_rate'] = (
                        result[key]['successful_jobs'] / result[key]['total_jobs'] * 100
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting preload stats: {e}")
            return {}
    
    def cleanup_old_jobs(self, days: int = 7):
        """Clean up old completed/failed jobs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old completed jobs
            completed_count = PreloadJob.query.filter(
                PreloadJob.status == 'completed',
                PreloadJob.completed_at < cutoff_date
            ).delete()
            
            # Delete old failed jobs (keep for longer for debugging)
            failed_cutoff = datetime.utcnow() - timedelta(days=days * 2)
            failed_count = PreloadJob.query.filter(
                PreloadJob.status == 'failed',
                PreloadJob.completed_at < failed_cutoff
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Cleaned up {completed_count} completed and {failed_count} failed jobs")
            
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {e}")
    
    def update_robots_txt_all_sources(self):
        """Update robots.txt for all sources"""
        for source, config in self.source_configs.items():
            self.update_robots_txt_cache(config['domain'])
            time.sleep(1)  # Small delay between requests 
import os
import sys
import threading
import time
from datetime import datetime, timedelta
import logging
import schedule

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.preloader import preloader_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for scheduling periodic preloading and updates"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.sources = ['weebcentral', 'asurascans', 'mangadex']
        self.flask_app = None  # Will hold Flask app reference
    
    def set_app(self, app):
        """Set the Flask app reference for context management"""
        self.flask_app = app
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")
        
        # Schedule initial preload after a short delay
        threading.Timer(10.0, self._initial_preload).start()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        # Schedule daily preloading at 3 AM
        schedule.every().day.at("03:00").do(self._daily_preload)
        
        # Schedule popular manga updates every 6 hours
        schedule.every(6).hours.do(self._update_popular_manga)
        
        # Schedule cleanup every week
        schedule.every().sunday.at("04:00").do(self._cleanup_old_entries)
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _initial_preload(self):
        """Perform initial preload when starting"""
        logger.info("Starting comprehensive initial preload")
        
        if not self.flask_app:
            logger.error("Flask app not set in SchedulerService")
            return
        
        # First, do comprehensive preload from all sources
        for source in self.sources:
            try:
                logger.info(f"Initial comprehensive preload for {source}")
                with self.flask_app.app_context():
                    preloader_service.preload_source(source, page_limit=2)  # Load 2 pages per URL initially
            except Exception as e:
                logger.error(f"Initial comprehensive preload failed for {source}: {e}")
        
        # Then, preload popular search terms for better coverage
        # DISABLED: Popular search terms preloading
        # try:
        #     logger.info("Initial popular search terms preload")
        #     with self.flask_app.app_context():
        #         preloader_service.preload_popular_search_terms()
        # except Exception as e:
        #     logger.error(f"Initial popular search terms preload failed: {e}")
    
    def _daily_preload(self):
        """Daily preload task"""
        logger.info("Starting comprehensive daily preload")
        
        if not self.flask_app:
            logger.error("Flask app not set in SchedulerService")
            return
        
        for source in self.sources:
            try:
                logger.info(f"Daily comprehensive preload for {source}")
                with self.flask_app.app_context():
                    preloader_service.preload_source(source, page_limit=3)
                
                # Add delay between sources to avoid overloading
                time.sleep(300)  # 5 minutes between sources
                
            except Exception as e:
                logger.error(f"Daily comprehensive preload failed for {source}: {e}")
        
        # Weekly popular search terms update
        # DISABLED: Weekly popular search terms preloading
        # if datetime.now().weekday() == 0:  # Monday
        #     try:
        #         logger.info("Weekly popular search terms preload")
        #         with self.flask_app.app_context():
        #             preloader_service.preload_popular_search_terms()
        #     except Exception as e:
        #         logger.error(f"Weekly popular search terms preload failed: {e}")
    
    def _update_popular_manga(self):
        """Update popular manga task"""
        logger.info("Starting popular manga update")
        
        if not self.flask_app:
            logger.error("Flask app not set in SchedulerService")
            return
        
        try:
            with self.flask_app.app_context():
                preloader_service.update_popular_manga(limit=100)
        except Exception as e:
            logger.error(f"Popular manga update failed: {e}")
    
    def _cleanup_old_entries(self):
        """Cleanup old entries task"""
        logger.info("Starting cleanup of old entries")
        
        if not self.flask_app:
            logger.error("Flask app not set in SchedulerService")
            return
        
        try:
            with self.flask_app.app_context():
                preloader_service.cleanup_old_entries(days=30)
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def trigger_preload(self, source: str = None):
        """Manually trigger a preload for testing or on-demand updates"""
        if not self.flask_app:
            logger.error("Flask app not set in SchedulerService")
            return
        
        if source:
            sources = [source] if source in self.sources else []
        else:
            sources = self.sources
        
        for src in sources:
            try:
                logger.info(f"Manual preload triggered for {src}")
                with self.flask_app.app_context():
                    preloader_service.preload_source(src, page_limit=2)
            except Exception as e:
                logger.error(f"Manual preload failed for {src}: {e}")
    
    def get_schedule_info(self):
        """Get information about scheduled jobs"""
        jobs = []
        for job in schedule.jobs:
            jobs.append({
                'job': str(job),
                'next_run': job.next_run.isoformat() if job.next_run else None
            })
        return {
            'running': self.running,
            'jobs': jobs
        }

# Create singleton instance
scheduler_service = SchedulerService() 
import threading
import time
import queue
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)

class BrowserPool:
    """Thread-safe browser pool for efficient Playwright usage"""
    
    def __init__(self, pool_size: int = 3, max_idle_time: int = 300):
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.browsers: queue.Queue = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self.active_browsers = 0
        self.playwright_instances = {}  # Thread-local playwright instances
        self.cleanup_thread = None
        self.running = True
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"Browser pool initialized with {pool_size} browsers")
    
    def _get_playwright_for_thread(self):
        """Get or create Playwright instance for current thread"""
        thread_id = threading.get_ident()
        if thread_id not in self.playwright_instances:
            self.playwright_instances[thread_id] = sync_playwright().start()
            logger.debug(f"Created Playwright instance for thread {thread_id}")
        return self.playwright_instances[thread_id]
    
    def get_browser(self) -> Optional[Browser]:
        """Get a browser from the pool or create a new one"""
        try:
            # Try to get from pool first
            browser = self.browsers.get_nowait()
            logger.debug("Reused browser from pool")
            return browser
        except queue.Empty:
            # Create new browser if under limit
            with self.lock:
                if self.active_browsers < self.pool_size:
                    playwright = self._get_playwright_for_thread()
                    browser = playwright.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--disable-web-security',
                            '--disable-features=VizDisplayCompositor',
                            '--disable-background-timer-throttling',
                            '--disable-backgrounding-occluded-windows',
                            '--disable-renderer-backgrounding',
                            '--disable-field-trial-config',
                            '--disable-ipc-flooding-protection',
                            '--memory-pressure-off',
                            '--max_old_space_size=4096'
                        ]
                    )
                    self.active_browsers += 1
                    logger.debug(f"Created new browser (active: {self.active_browsers})")
                    return browser
                else:
                    # Wait for a browser to become available
                    logger.debug("Waiting for browser to become available")
                    try:
                        browser = self.browsers.get(timeout=30)
                        return browser
                    except queue.Empty:
                        logger.error("Timeout waiting for browser to become available")
                        return None
        except Exception as e:
            logger.error(f"Error getting browser: {e}")
            return None
    
    def return_browser(self, browser: Browser):
        """Return a browser to the pool"""
        try:
            # Check if browser is still responsive
            try:
                # Try to create a new page to test browser health
                test_page = browser.new_page()
                test_page.close()
                
                # Return to pool if healthy
                self.browsers.put_nowait(browser)
                logger.debug("Browser returned to pool")
            except Exception:
                # Browser is unhealthy, close it and create a new one
                logger.warning("Browser was unhealthy, closing it")
                self._close_browser(browser)
                
        except queue.Full:
            # Pool is full, close the browser
            logger.debug("Pool is full, closing browser")
            self._close_browser(browser)
        except Exception as e:
            logger.error(f"Error returning browser: {e}")
            self._close_browser(browser)
    
    def _close_browser(self, browser: Browser):
        """Close a browser and update counters"""
        try:
            browser.close()
            with self.lock:
                self.active_browsers = max(0, self.active_browsers - 1)
            logger.debug(f"Browser closed (active: {self.active_browsers})")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def _cleanup_loop(self):
        """Background thread to clean up idle browsers"""
        while self.running:
            try:
                time.sleep(60)  # Check every minute
                self._cleanup_idle_browsers()
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def _cleanup_idle_browsers(self):
        """Remove browsers that have been idle too long"""
        # For now, we'll keep browsers alive as they're expensive to create
        # In a more sophisticated implementation, we could track last usage time
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            'pool_size': self.pool_size,
            'active_browsers': self.active_browsers,
            'available_browsers': self.browsers.qsize(),
            'max_idle_time': self.max_idle_time,
            'playwright_instances': len(self.playwright_instances)
        }
    
    def shutdown(self):
        """Shutdown the browser pool"""
        self.running = False
        
        # Close all browsers in pool
        while not self.browsers.empty():
            try:
                browser = self.browsers.get_nowait()
                self._close_browser(browser)
            except queue.Empty:
                break
        
        # Close all Playwright instances
        for thread_id, playwright in self.playwright_instances.items():
            try:
                playwright.stop()
                logger.debug(f"Closed Playwright instance for thread {thread_id}")
            except Exception as e:
                logger.error(f"Error closing Playwright instance for thread {thread_id}: {e}")
        
        self.playwright_instances.clear()
        logger.info("Browser pool shutdown complete")

# Global browser pool instance
browser_pool = BrowserPool(pool_size=3) 
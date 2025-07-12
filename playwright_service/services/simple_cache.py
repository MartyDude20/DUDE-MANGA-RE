import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache with TTL for manga search results"""
    
    def __init__(self, ttl_hours: int = 6):
        self.cache = {}
        self.ttl_seconds = ttl_hours * 60 * 60
        self.lock = threading.Lock()
        self.cleanup_interval = 3600  # Cleanup every hour
        self.last_cleanup = time.time()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Dict]:
        """Get value from cache if not expired"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl_seconds:
                    logger.debug(f"Cache HIT for key: {key}")
                    return entry['data']
                else:
                    # Expired, remove it
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED for key: {key}")
            
            logger.debug(f"Cache MISS for key: {key}")
            return None
    
    def set(self, key: str, data: Any) -> None:
        """Set value in cache with current timestamp"""
        with self.lock:
            self.cache[key] = {
                'data': data,
                'timestamp': time.time()
            }
            logger.debug(f"Cache SET for key: {key}")
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache DELETE for key: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get number of cache entries"""
        with self.lock:
            return len(self.cache)
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.cache.items():
                if current_time - entry['timestamp'] >= self.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _cleanup_loop(self) -> None:
        """Background thread to periodically cleanup expired entries"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                current_time = time.time()
                
                if current_time - self.last_cleanup >= self.cleanup_interval:
                    self._cleanup_expired()
                    self.last_cleanup = current_time
                    
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            current_time = time.time()
            total_entries = len(self.cache)
            expired_entries = sum(
                1 for entry in self.cache.values()
                if current_time - entry['timestamp'] >= self.ttl_seconds
            )
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'valid_entries': total_entries - expired_entries,
                'ttl_hours': self.ttl_seconds / 3600
            }

# Global cache instance
search_cache = SimpleCache(ttl_hours=6) 
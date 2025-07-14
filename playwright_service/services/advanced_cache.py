import time
import threading
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class AdvancedCache:
    """Multi-layer cache system for maximum performance"""
    
    def __init__(self):
        # L1: In-memory cache (fastest, limited size)
        self.l1_cache = {}
        self.l1_lock = threading.Lock()
        self.l1_ttl = 300  # 5 minutes
        self.l1_max_size = 1000
        
        # L2: Extended memory cache (larger, longer TTL)
        self.l2_cache = {}
        self.l2_lock = threading.Lock()
        self.l2_ttl = 3600  # 1 hour
        self.l2_max_size = 5000
        
        # L3: Database cache (persistent, longest TTL)
        self.l3_ttl = 21600  # 6 hours
        
        # Statistics
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'l3_hits': 0,
            'misses': 0,
            'total_requests': 0
        }
        self.stats_lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-layer cache"""
        self._increment_stat('total_requests')
        
        # Try L1 cache first (fastest)
        result = self._get_from_l1(key)
        if result is not None:
            self._increment_stat('l1_hits')
            return result
        
        # Try L2 cache
        result = self._get_from_l2(key)
        if result is not None:
            self._increment_stat('l2_hits')
            # Promote to L1 cache
            self._set_l1(key, result)
            return result
        
        # Try L3 cache (database)
        result = self._get_from_l3(key)
        if result is not None:
            self._increment_stat('l3_hits')
            # Promote to L1 and L2 cache
            self._set_l1(key, result)
            self._set_l2(key, result)
            return result
        
        self._increment_stat('misses')
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in all cache layers"""
        # Set in L1 and L2 cache
        self._set_l1(key, value, ttl if ttl is not None else self.l1_ttl)
        self._set_l2(key, value, ttl if ttl is not None else self.l2_ttl)
        
        # Set in L3 cache (database) for persistence
        self._set_l3(key, value, ttl if ttl is not None else self.l3_ttl)
    
    def _get_from_l1(self, key: str) -> Optional[Any]:
        """Get from L1 cache"""
        with self.l1_lock:
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if time.time() - entry['timestamp'] < entry['ttl']:
                    return entry['value']
                else:
                    del self.l1_cache[key]
        return None
    
    def _get_from_l2(self, key: str) -> Optional[Any]:
        """Get from L2 cache"""
        with self.l2_lock:
            if key in self.l2_cache:
                entry = self.l2_cache[key]
                if time.time() - entry['timestamp'] < entry['ttl']:
                    return entry['value']
                else:
                    del self.l2_cache[key]
        return None
    
    def _get_from_l3(self, key: str) -> Optional[Any]:
        """Get from L3 cache (database)"""
        try:
            # This would integrate with your existing database cache
            # For now, we'll return None to keep it simple
            return None
        except Exception as e:
            logger.error(f"L3 cache error: {e}")
            return None
    
    def _set_l1(self, key: str, value: Any, ttl: int) -> None:
        """Set in L1 cache"""
        with self.l1_lock:
            # Evict if cache is full
            if len(self.l1_cache) >= self.l1_max_size:
                self._evict_l1()
            
            self.l1_cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
    
    def _set_l2(self, key: str, value: Any, ttl: int) -> None:
        """Set in L2 cache"""
        with self.l2_lock:
            # Evict if cache is full
            if len(self.l2_cache) >= self.l2_max_size:
                self._evict_l2()
            
            self.l2_cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
    
    def _set_l3(self, key: str, value: Any, ttl: int) -> None:
        """Set in L3 cache (database)"""
        try:
            # This would integrate with your existing database cache
            # For now, we'll just log it
            logger.debug(f"L3 cache set: {key}")
        except Exception as e:
            logger.error(f"L3 cache set error: {e}")
    
    def _evict_l1(self) -> None:
        """Evict oldest entry from L1 cache"""
        oldest_key = min(self.l1_cache.keys(), 
                        key=lambda k: self.l1_cache[k]['timestamp'])
        del self.l1_cache[oldest_key]
    
    def _evict_l2(self) -> None:
        """Evict oldest entry from L2 cache"""
        oldest_key = min(self.l2_cache.keys(), 
                        key=lambda k: self.l2_cache[k]['timestamp'])
        del self.l2_cache[oldest_key]
    
    def _increment_stat(self, stat: str) -> None:
        """Increment statistics"""
        with self.stats_lock:
            self.stats[stat] += 1
    
    def _cleanup_loop(self) -> None:
        """Background cleanup thread"""
        while True:
            try:
                time.sleep(60)  # Run every minute
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from all cache layers"""
        current_time = time.time()
        
        # Clean L1 cache
        with self.l1_lock:
            expired_keys = [
                k for k, v in self.l1_cache.items()
                if current_time - v['timestamp'] > v['ttl']
            ]
            for key in expired_keys:
                del self.l1_cache[key]
        
        # Clean L2 cache
        with self.l2_lock:
            expired_keys = [
                k for k, v in self.l2_cache.items()
                if current_time - v['timestamp'] > v['ttl']
            ]
            for key in expired_keys:
                del self.l2_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.stats_lock:
            stats = self.stats.copy()
        
        total_requests = stats['total_requests']
        if total_requests > 0:
            stats['l1_hit_rate'] = f"{(stats['l1_hits'] / total_requests) * 100:.1f}%"
            stats['l2_hit_rate'] = f"{(stats['l2_hits'] / total_requests) * 100:.1f}%"
            stats['l3_hit_rate'] = f"{(stats['l3_hits'] / total_requests) * 100:.1f}%"
            stats['miss_rate'] = f"{(stats['misses'] / total_requests) * 100:.1f}%"
        
        stats['l1_size'] = len(self.l1_cache)
        stats['l2_size'] = len(self.l2_cache)
        
        return stats
    
    def clear(self) -> None:
        """Clear all cache layers"""
        with self.l1_lock:
            self.l1_cache.clear()
        with self.l2_lock:
            self.l2_cache.clear()
        logger.info("All cache layers cleared")

# Global advanced cache instance
advanced_cache = AdvancedCache() 
import time
import threading
import statistics
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics for search and scraping operations"""
    
    def __init__(self):
        self.metrics = {
            'search_times': [],
            'scrape_times': {},
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': {},
            'source_performance': {},
            'total_requests': 0
        }
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'search_timeout': 30.0,  # seconds
            'scrape_timeout': 15.0,  # seconds
            'error_threshold': 0.1,  # 10% error rate
            'slow_threshold': 5.0    # seconds
        }
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def record_search(self, query: str, sources: List[str], duration: float, 
                     results_count: int, cached: bool, errors: Optional[List[str]] = None):
        """Record search performance metrics"""
        with self.lock:
            self.metrics['total_requests'] += 1
            self.metrics['search_times'].append(duration)
            
            if cached:
                self.metrics['cache_hits'] += 1
            else:
                self.metrics['cache_misses'] += 1
            
            # Track source performance
            for source in sources:
                if source not in self.metrics['source_performance']:
                    self.metrics['source_performance'][source] = {
                        'total_searches': 0,
                        'avg_time': 0.0,
                        'success_count': 0,
                        'error_count': 0
                    }
                
                source_metrics = self.metrics['source_performance'][source]
                source_metrics['total_searches'] += 1
                
                # Update average time
                current_avg = source_metrics['avg_time']
                total_searches = source_metrics['total_searches']
                source_metrics['avg_time'] = (current_avg * (total_searches - 1) + duration) / total_searches
                
                if errors:
                    source_metrics['error_count'] += 1
                else:
                    source_metrics['success_count'] += 1
            
            # Record errors
            if errors:
                for error in errors:
                    if error not in self.metrics['errors']:
                        self.metrics['errors'][error] = 0
                    self.metrics['errors'][error] += 1
            
            # Keep only last 1000 search times for memory efficiency
            if len(self.metrics['search_times']) > 1000:
                self.metrics['search_times'] = self.metrics['search_times'][-1000:]
    
    def record_scrape(self, source: str, operation: str, duration: float, success: bool):
        """Record scraping performance metrics"""
        with self.lock:
            if source not in self.metrics['scrape_times']:
                self.metrics['scrape_times'][source] = {}
            
            if operation not in self.metrics['scrape_times'][source]:
                self.metrics['scrape_times'][source][operation] = []
            
            self.metrics['scrape_times'][source][operation].append({
                'duration': duration,
                'success': success,
                'timestamp': time.time()
            })
            
            # Keep only last 100 scrape times per operation
            if len(self.metrics['scrape_times'][source][operation]) > 100:
                self.metrics['scrape_times'][source][operation] = \
                    self.metrics['scrape_times'][source][operation][-100:]
    
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        with self.lock:
            report = {
                'summary': self._get_summary(),
                'search_performance': self._get_search_performance(),
                'source_performance': self._get_source_performance(),
                'error_analysis': self._get_error_analysis(),
                'recommendations': self._get_recommendations()
            }
        return report
    
    def _get_summary(self) -> Dict:
        """Get performance summary"""
        total_requests = self.metrics['total_requests']
        if total_requests == 0:
            return {'message': 'No performance data available'}
        
        cache_hit_rate = (self.metrics['cache_hits'] / total_requests) * 100 if total_requests > 0 else 0
        
        search_times = self.metrics['search_times']
        avg_search_time = statistics.mean(search_times) if search_times else 0
        median_search_time = statistics.median(search_times) if search_times else 0
        p95_search_time = statistics.quantiles(search_times, n=20)[18] if len(search_times) >= 20 else 0
        
        return {
            'total_requests': total_requests,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'avg_search_time': f"{avg_search_time:.2f}s",
            'median_search_time': f"{median_search_time:.2f}s",
            'p95_search_time': f"{p95_search_time:.2f}s",
            'total_errors': sum(self.metrics['errors'].values())
        }
    
    def _get_search_performance(self) -> Dict:
        """Get detailed search performance metrics"""
        search_times = self.metrics['search_times']
        if not search_times:
            return {'message': 'No search data available'}
        
        return {
            'total_searches': len(search_times),
            'avg_time': f"{statistics.mean(search_times):.2f}s",
            'median_time': f"{statistics.median(search_times):.2f}s",
            'min_time': f"{min(search_times):.2f}s",
            'max_time': f"{max(search_times):.2f}s",
            'std_dev': f"{statistics.stdev(search_times):.2f}s" if len(search_times) > 1 else "N/A",
            'slow_searches': len([t for t in search_times if t > self.thresholds['slow_threshold']])
        }
    
    def _get_source_performance(self) -> Dict:
        """Get performance metrics by source"""
        source_perf = {}
        for source, metrics in self.metrics['source_performance'].items():
            total = metrics['total_searches']
            success_rate = (metrics['success_count'] / total * 100) if total > 0 else 0
            
            source_perf[source] = {
                'total_searches': total,
                'avg_time': f"{metrics['avg_time']:.2f}s",
                'success_rate': f"{success_rate:.1f}%",
                'error_count': metrics['error_count']
            }
        
        return source_perf
    
    def _get_error_analysis(self) -> Dict:
        """Analyze error patterns"""
        total_errors = sum(self.metrics['errors'].values())
        if total_errors == 0:
            return {'message': 'No errors recorded'}
        
        error_analysis = {
            'total_errors': total_errors,
            'error_rate': f"{(total_errors / self.metrics['total_requests']) * 100:.1f}%" if self.metrics['total_requests'] > 0 else "0%",
            'top_errors': []
        }
        
        # Get top 5 errors
        sorted_errors = sorted(self.metrics['errors'].items(), key=lambda x: x[1], reverse=True)
        for error, count in sorted_errors[:5]:
            error_analysis['top_errors'].append({
                'error': error,
                'count': count,
                'percentage': f"{(count / total_errors) * 100:.1f}%"
            })
        
        return error_analysis
    
    def _get_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check cache hit rate
        total_requests = self.metrics['total_requests']
        if total_requests > 0:
            cache_hit_rate = self.metrics['cache_hits'] / total_requests
            if cache_hit_rate < 0.5:
                recommendations.append("Low cache hit rate - consider increasing cache TTL or preloading popular searches")
        
        # Check search times
        search_times = self.metrics['search_times']
        if search_times:
            avg_time = statistics.mean(search_times)
            if avg_time > self.thresholds['slow_threshold']:
                recommendations.append(f"Average search time ({avg_time:.2f}s) is above threshold - consider optimizing scrapers or increasing parallelization")
        
        # Check error rates
        total_errors = sum(self.metrics['errors'].values())
        if total_requests > 0:
            error_rate = total_errors / total_requests
            if error_rate > self.thresholds['error_threshold']:
                recommendations.append(f"High error rate ({error_rate:.1%}) - investigate and fix common errors")
        
        # Check source performance
        for source, metrics in self.metrics['source_performance'].items():
            if metrics['total_searches'] > 10:  # Only analyze sources with sufficient data
                success_rate = metrics['success_count'] / metrics['total_searches']
                if success_rate < 0.8:
                    recommendations.append(f"Low success rate for {source} ({success_rate:.1%}) - investigate source reliability")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable ranges")
        
        return recommendations
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                time.sleep(300)  # Check every 5 minutes
                self._check_alerts()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _check_alerts(self):
        """Check for performance alerts"""
        with self.lock:
            # Check for high error rates
            total_requests = self.metrics['total_requests']
            if total_requests > 0:
                total_errors = sum(self.metrics['errors'].values())
                error_rate = total_errors / total_requests
                
                if error_rate > self.thresholds['error_threshold']:
                    logger.warning(f"High error rate detected: {error_rate:.1%}")
                
                # Check for slow searches
                recent_searches = self.metrics['search_times'][-100:]  # Last 100 searches
                if recent_searches:
                    avg_recent_time = statistics.mean(recent_searches)
                    if avg_recent_time > self.thresholds['slow_threshold']:
                        logger.warning(f"Slow search times detected: {avg_recent_time:.2f}s average")
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        with self.lock:
            self.metrics = {
                'search_times': [],
                'scrape_times': {},
                'cache_hits': 0,
                'cache_misses': 0,
                'errors': {},
                'source_performance': {},
                'total_requests': 0
            }
        logger.info("Performance metrics reset")

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 
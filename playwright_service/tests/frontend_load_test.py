#!/usr/bin/env python3
"""
Frontend Load Test - 5-minute sustained test with pre-loading
Simulates real user behavior with search requests
"""

import time
import requests
import json
import random
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import statistics

# Test configuration
PROXY_URL = "http://localhost:3006"
PLAYWRIGHT_URL = "http://localhost:5000"
TEST_DURATION = 300  # 5 minutes
CONCURRENT_USERS = 1
REQUEST_INTERVAL = 2  # seconds between requests per user

# Test manga queries (popular titles)
TEST_QUERIES = [
    "Solo Leveling",
    "Murim Login", 
    "The Greatest Estate Developer",
    "Nano Machine",
    "Solo Max-Level Newbie",
    "Infinite Mage",
    "Swordmaster's Youngest Son",
    "Return Survival",
    "Way to Heaven",
    "Reverse Villain",
    "The Boxer",
    "Sweet Home",
    "Bastard",
    "Shotgun Boy",
    "Pigpen"
]

class LoadTestUser:
    """Simulates a single user making requests"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.requests_made = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.cache_hits = 0
        self.manga_found = 0
        
    def make_search_request(self, query: str) -> dict:
        """Make a search request and return results"""
        start_time = time.time()
        
        try:
            # Make search request through proxy
            sources_str = "asurascans,weebcentral,mangadex"
            search_url = f"{PROXY_URL}/api/search?q={query}&sources={sources_str}"
            
            response = requests.get(search_url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                manga_results = data.get('results', [])
                cached_count = sum(1 for m in manga_results if m.get('cached', False))
                
                return {
                    'success': True,
                    'response_time': end_time - start_time,
                    'manga_count': len(manga_results),
                    'cached_count': cached_count,
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'response_time': end_time - start_time,
                    'error': f"HTTP {response.status_code}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'response_time': end_time - start_time,
                'error': str(e),
                'status_code': None
            }
    
    def run_user_session(self, stop_event):
        """Run user session for the test duration"""
        print(f"👤 User {self.user_id} started")
        
        while not stop_event.is_set():
            # Pick a random query
            query = random.choice(TEST_QUERIES)
            
            # Make request
            result = self.make_search_request(query)
            
            # Update statistics
            self.requests_made += 1
            self.response_times.append(result['response_time'])
            
            if result['success']:
                self.successful_requests += 1
                self.cache_hits += result['cached_count']
                self.manga_found += result['manga_count']
                
                # Log successful request
                print(f"👤 User {self.user_id}: '{query}' - {result['manga_count']} results ({result['cached_count']} cached) in {result['response_time']:.2f}s")
            else:
                self.failed_requests += 1
                print(f"👤 User {self.user_id}: '{query}' - FAILED: {result.get('error', 'Unknown error')}")
            
            # Wait before next request
            time.sleep(REQUEST_INTERVAL)
        
        print(f"👤 User {self.user_id} finished - {self.requests_made} requests")

class LoadTest:
    """Main load test orchestrator"""
    
    def __init__(self):
        self.users = []
        self.start_time = None
        self.stop_event = threading.Event()
        self.test_results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0,
            'response_times': [],
            'cache_hits': 0,
            'manga_found': 0,
            'queries_used': set()
        }
    
    def check_service_health(self):
        """Check if services are running"""
        print("🔍 Checking service health...")
        
        try:
            proxy_status = requests.get(f"{PROXY_URL}/api/health", timeout=5)
            playwright_status = requests.get(f"{PLAYWRIGHT_URL}/health", timeout=5)
            
            if proxy_status.status_code == 200 and playwright_status.status_code == 200:
                print("✅ Services are healthy")
                return True
            else:
                print("❌ Services not responding properly")
                return False
        except Exception as e:
            print(f"❌ Service health check failed: {e}")
            return False
    
    def trigger_preload(self):
        """Trigger preloading of popular manga"""
        print("🚀 Triggering preload of popular manga...")
        
        try:
            # Trigger comprehensive preload
            response = requests.post(f"{PLAYWRIGHT_URL}/preloader/comprehensive", timeout=30)
            if response.status_code == 200:
                print("✅ Preload triggered successfully")
            else:
                print(f"⚠️ Preload trigger failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Preload trigger error: {e}")
    
    def start_users(self):
        """Start all user sessions"""
        print(f"👥 Starting {CONCURRENT_USERS} concurrent users...")
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            # Start user sessions
            futures = []
            for i in range(CONCURRENT_USERS):
                user = LoadTestUser(i + 1)
                self.users.append(user)
                future = executor.submit(user.run_user_session, self.stop_event)
                futures.append(future)
            
            # Wait for test duration
            time.sleep(TEST_DURATION)
            
            # Stop all users
            self.stop_event.set()
            
            # Wait for all users to finish
            for future in futures:
                future.result()
    
    def collect_results(self):
        """Collect and aggregate results from all users"""
        print("📊 Collecting test results...")
        
        for user in self.users:
            self.test_results['total_requests'] += user.requests_made
            self.test_results['successful_requests'] += user.successful_requests
            self.test_results['failed_requests'] += user.failed_requests
            self.test_results['response_times'].extend(user.response_times)
            self.test_results['cache_hits'] += user.cache_hits
            self.test_results['manga_found'] += user.manga_found
        
        # Calculate statistics
        if self.test_results['response_times']:
            self.test_results['avg_response_time'] = statistics.mean(self.test_results['response_times'])
            self.test_results['min_response_time'] = min(self.test_results['response_times'])
            self.test_results['max_response_time'] = max(self.test_results['response_times'])
            self.test_results['median_response_time'] = statistics.median(self.test_results['response_times'])
        else:
            self.test_results['avg_response_time'] = 0
            self.test_results['min_response_time'] = 0
            self.test_results['max_response_time'] = 0
            self.test_results['median_response_time'] = 0
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 FRONTEND LOAD TEST RESULTS")
        print("=" * 80)
        print(f"⏱️  Test Duration: {TEST_DURATION} seconds ({TEST_DURATION/60:.1f} minutes)")
        print(f"👥 Concurrent Users: {CONCURRENT_USERS}")
        print(f"🕐 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📈 REQUEST STATISTICS:")
        print(f"   Total Requests: {self.test_results['total_requests']}")
        print(f"   Successful: {self.test_results['successful_requests']}")
        print(f"   Failed: {self.test_results['failed_requests']}")
        print(f"   Success Rate: {(self.test_results['successful_requests']/self.test_results['total_requests']*100):.1f}%" if self.test_results['total_requests'] > 0 else "   Success Rate: 0%")
        
        print(f"\n⏱️  RESPONSE TIME STATISTICS:")
        print(f"   Average: {self.test_results['avg_response_time']:.3f}s")
        print(f"   Median: {self.test_results['median_response_time']:.3f}s")
        print(f"   Minimum: {self.test_results['min_response_time']:.3f}s")
        print(f"   Maximum: {self.test_results['max_response_time']:.3f}s")
        
        print(f"\n📚 CONTENT STATISTICS:")
        print(f"   Total Manga Found: {self.test_results['manga_found']}")
        print(f"   Cache Hits: {self.test_results['cache_hits']}")
        print(f"   Cache Hit Rate: {(self.test_results['cache_hits']/self.test_results['manga_found']*100):.1f}%" if self.test_results['manga_found'] > 0 else "   Cache Hit Rate: 0%")
        
        print(f"\n🚀 PERFORMANCE ASSESSMENT:")
        avg_time = self.test_results['avg_response_time']
        if avg_time < 2.0:
            print(f"   🎉 EXCELLENT: {avg_time:.3f}s average (under 2s)")
        elif avg_time < 5.0:
            print(f"   ✅ GOOD: {avg_time:.3f}s average (under 5s)")
        elif avg_time < 10.0:
            print(f"   ⚠️  ACCEPTABLE: {avg_time:.3f}s average (under 10s)")
        else:
            print(f"   ❌ POOR: {avg_time:.3f}s average (over 10s)")
        
        # Get system metrics
        try:
            metrics_response = requests.get(f"{PLAYWRIGHT_URL}/performance/metrics", timeout=5)
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                print(f"\n📊 SYSTEM METRICS:")
                print(f"   Total Searches: {metrics.get('total_searches', 0)}")
                print(f"   Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1f}%")
                print(f"   Average Search Time: {metrics.get('avg_search_time', 0):.3f}s")
                print(f"   Cache Size: {metrics.get('cache_size', 0)}")
        except Exception as e:
            print(f"   ⚠️  Could not get system metrics: {e}")
    
    def run_test(self):
        """Run the complete load test"""
        print("🚀 Frontend Load Test - 5 Minutes with Pre-loading")
        print("=" * 80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check service health
        if not self.check_service_health():
            print("❌ Services not ready. Exiting.")
            return
        
        # Trigger preload
        self.trigger_preload()
        
        # Wait a bit for preload to start
        print("⏳ Waiting 10 seconds for preload to begin...")
        time.sleep(10)
        
        # Start the test
        self.start_time = datetime.now()
        print(f"\n🎬 Starting load test at {self.start_time.strftime('%H:%M:%S')}...")
        print(f"⏱️  Test will run for {TEST_DURATION} seconds")
        print(f"👥 {CONCURRENT_USERS} concurrent users will make requests every {REQUEST_INTERVAL} seconds")
        print("-" * 80)
        
        # Start user sessions
        self.start_users()
        
        # Collect and display results
        self.collect_results()
        self.print_results()
        
        print(f"\n✅ Load test completed!")

if __name__ == "__main__":
    load_test = LoadTest()
    load_test.run_test() 
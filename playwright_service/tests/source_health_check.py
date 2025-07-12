#!/usr/bin/env python3
"""
Source Health Check - Test all manga sources for availability and response times
"""

import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources import weebcentral, asurascans, mangadex

# Source configurations
SOURCES = {
    'weebcentral': {
        'module': weebcentral,
        'base_url': 'https://weebcentral.com',
        'search_url': 'https://weebcentral.com/search',
        'test_query': 'solo'
    },
    'asurascans': {
        'module': asurascans,
        'base_url': 'https://asuracomic.net',
        'search_url': 'https://asuracomic.net/series',
        'test_query': 'solo'
    },
    'mangadex': {
        'module': mangadex,
        'base_url': 'https://mangadex.org',
        'search_url': 'https://mangadex.org/titles',
        'test_query': 'solo'
    }
}

def test_http_ping(source_name: str, url: str) -> dict:
    """Test HTTP connectivity to a source"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        end_time = time.time()
        
        return {
            'status': 'success',
            'response_time': round((end_time - start_time) * 1000, 2),  # ms
            'status_code': response.status_code,
            'content_length': len(response.content),
            'error': None
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'response_time': None,
            'status_code': None,
            'content_length': None,
            'error': 'Request timed out after 10 seconds'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'connection_error',
            'response_time': None,
            'status_code': None,
            'content_length': None,
            'error': 'Connection failed'
        }
    except Exception as e:
        return {
            'status': 'error',
            'response_time': None,
            'status_code': None,
            'content_length': None,
            'error': str(e)
        }

def test_playwright_search(source_name: str, source_config: dict) -> dict:
    """Test Playwright-based search functionality"""
    try:
        start_time = time.time()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ])
            
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 720})
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Test search functionality
            source_module = source_config['module']
            test_query = source_config['test_query']
            
            search_start = time.time()
            results = source_module.search(page, test_query)
            search_end = time.time()
            
            page.close()
            browser.close()
            
            end_time = time.time()
            
            return {
                'status': 'success',
                'total_time': round((end_time - start_time) * 1000, 2),  # ms
                'search_time': round((search_end - search_start) * 1000, 2),  # ms
                'results_count': len(results) if results else 0,
                'error': None
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'total_time': None,
            'search_time': None,
            'results_count': None,
            'error': str(e)
        }

def run_health_check():
    """Run comprehensive health check on all sources"""
    print("🔍 Source Health Check - Manga Sources")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    for source_name, source_config in SOURCES.items():
        print(f"📡 Testing {source_name.upper()}...")
        print("-" * 40)
        
        # Test HTTP ping
        print(f"  🌐 HTTP Ping: {source_config['base_url']}")
        http_result = test_http_ping(source_name, source_config['base_url'])
        
        if http_result['status'] == 'success':
            print(f"    ✅ Status: {http_result['status_code']}")
            print(f"    ⏱️  Response: {http_result['response_time']}ms")
            print(f"    📦 Content: {http_result['content_length']} bytes")
        else:
            print(f"    ❌ {http_result['status'].upper()}: {http_result['error']}")
        
        # Test Playwright search
        print(f"  🕷️  Playwright Search: '{source_config['test_query']}'")
        playwright_result = test_playwright_search(source_name, source_config)
        
        if playwright_result['status'] == 'success':
            print(f"    ✅ Search: {playwright_result['results_count']} results")
            print(f"    ⏱️  Total Time: {playwright_result['total_time']}ms")
            print(f"    🔍 Search Time: {playwright_result['search_time']}ms")
        else:
            print(f"    ❌ ERROR: {playwright_result['error']}")
        
        results[source_name] = {
            'http': http_result,
            'playwright': playwright_result
        }
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    for source_name, result in results.items():
        http_status = "✅" if result['http']['status'] == 'success' else "❌"
        playwright_status = "✅" if result['playwright']['status'] == 'success' else "❌"
        
        print(f"{source_name.upper():<15} HTTP: {http_status} | Playwright: {playwright_status}")
        
        if result['http']['status'] == 'success':
            print(f"  🌐 Response: {result['http']['response_time']}ms")
        if result['playwright']['status'] == 'success':
            print(f"  🕷️  Search: {result['playwright']['results_count']} results in {result['playwright']['search_time']}ms")
    
    # Overall health
    healthy_sources = sum(1 for r in results.values() 
                         if r['http']['status'] == 'success' and r['playwright']['status'] == 'success')
    total_sources = len(results)
    
    print(f"\n🏥 OVERALL HEALTH: {healthy_sources}/{total_sources} sources healthy")
    
    if healthy_sources == total_sources:
        print("🎉 All sources are working perfectly!")
    elif healthy_sources > 0:
        print("⚠️  Some sources have issues, but system is functional")
    else:
        print("🚨 All sources are down - system needs attention")

if __name__ == "__main__":
    run_health_check() 
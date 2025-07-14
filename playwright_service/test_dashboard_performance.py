#!/usr/bin/env python3
"""
Test script to measure dashboard performance improvements.
Tests both the old sequential approach and new single endpoint approach.
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3006/api"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123"
}

def login_user():
    """Login and get access token"""
    try:
        response = requests.post(f"{BASE_URL}/login", json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_old_sequential_approach(token):
    """Test the old approach with 3 separate API calls"""
    headers = {'Authorization': f'Bearer {token}'}
    
    start_time = time.time()
    
    try:
        # Make 3 separate calls sequentially
        activity_response = requests.get(f"{BASE_URL}/read-history?limit=5", headers=headers)
        continue_response = requests.get(f"{BASE_URL}/reading-progress/continue", headers=headers)
        stats_response = requests.get(f"{BASE_URL}/reading-stats", headers=headers)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check if all responses were successful
        success = all([
            activity_response.status_code == 200,
            continue_response.status_code == 200,
            stats_response.status_code == 200
        ])
        
        return {
            'success': success,
            'total_time': total_time,
            'activity_status': activity_response.status_code,
            'continue_status': continue_response.status_code,
            'stats_status': stats_response.status_code
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'total_time': time.time() - start_time
        }

def test_new_single_endpoint(token):
    """Test the new approach with single dashboard endpoint"""
    headers = {'Authorization': f'Bearer {token}'}
    
    start_time = time.time()
    
    try:
        # Make single dashboard call
        response = requests.get(f"{BASE_URL}/dashboard?activity_limit=5&continue_limit=3", headers=headers)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'success': response.status_code == 200,
            'total_time': total_time,
            'status_code': response.status_code,
            'data_size': len(response.content) if response.status_code == 200 else 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'total_time': time.time() - start_time
        }

def test_caching_performance(token):
    """Test caching performance by making multiple requests"""
    headers = {'Authorization': f'Bearer {token}'}
    
    print("\n🧪 Testing Caching Performance...")
    
    # First request (should hit database)
    start_time = time.time()
    response1 = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    first_request_time = time.time() - start_time
    
    # Second request (should hit cache)
    start_time = time.time()
    response2 = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    second_request_time = time.time() - start_time
    
    # Third request (should hit cache)
    start_time = time.time()
    response3 = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    third_request_time = time.time() - start_time
    
    return {
        'first_request': {
            'time': first_request_time,
            'status': response1.status_code
        },
        'second_request': {
            'time': second_request_time,
            'status': response2.status_code
        },
        'third_request': {
            'time': third_request_time,
            'status': response3.status_code
        },
        'cache_improvement': first_request_time / second_request_time if second_request_time > 0 else 0
    }

def main():
    print("🚀 Dashboard Performance Test")
    print("=" * 50)
    
    # Login
    print("🔐 Logging in...")
    token = login_user()
    if not token:
        print("❌ Failed to login. Exiting.")
        return
    
    print("✅ Login successful")
    
    # Test old sequential approach
    print("\n📊 Testing Old Sequential Approach...")
    old_results = test_old_sequential_approach(token)
    
    if old_results['success']:
        print(f"✅ Old approach successful")
        print(f"⏱️  Total time: {old_results['total_time']:.3f}s")
        print(f"📈 Activity status: {old_results['activity_status']}")
        print(f"📈 Continue status: {old_results['continue_status']}")
        print(f"📈 Stats status: {old_results['stats_status']}")
    else:
        print(f"❌ Old approach failed: {old_results.get('error', 'Unknown error')}")
        print(f"⏱️  Time taken: {old_results['total_time']:.3f}s")
    
    # Test new single endpoint approach
    print("\n🚀 Testing New Single Endpoint Approach...")
    new_results = test_new_single_endpoint(token)
    
    if new_results['success']:
        print(f"✅ New approach successful")
        print(f"⏱️  Total time: {new_results['total_time']:.3f}s")
        print(f"📊 Data size: {new_results['data_size']} bytes")
    else:
        print(f"❌ New approach failed: {new_results.get('error', 'Unknown error')}")
        print(f"⏱️  Time taken: {new_results['total_time']:.3f}s")
    
    # Compare performance
    if old_results['success'] and new_results['success']:
        improvement = old_results['total_time'] / new_results['total_time']
        time_saved = old_results['total_time'] - new_results['total_time']
        
        print("\n📈 Performance Comparison:")
        print(f"🔄 Speed improvement: {improvement:.2f}x faster")
        print(f"⏰ Time saved: {time_saved:.3f}s")
        print(f"📉 Performance gain: {((improvement - 1) * 100):.1f}%")
    
    # Test caching
    cache_results = test_caching_performance(token)
    
    print(f"\n💾 Caching Results:")
    print(f"🔄 First request (DB): {cache_results['first_request']['time']:.3f}s")
    print(f"⚡ Second request (Cache): {cache_results['second_request']['time']:.3f}s")
    print(f"⚡ Third request (Cache): {cache_results['third_request']['time']:.3f}s")
    
    if cache_results['cache_improvement'] > 1:
        print(f"🚀 Cache improvement: {cache_results['cache_improvement']:.2f}x faster")
    
    # Test data structure
    print("\n🔍 Testing Dashboard Data Structure...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard", headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Data structure validation:")
            print(f"📊 Recent activity items: {len(data.get('recent_activity', []))}")
            print(f"📖 Continue reading items: {len(data.get('continue_reading', []))}")
            print(f"📈 Reading stats keys: {list(data.get('reading_stats', {}).keys())}")
            
            # Validate stats structure
            stats = data.get('reading_stats', {})
            if 'goals' in stats:
                print(f"🎯 Reading goals: {len(stats['goals'])}")
            
        else:
            print(f"❌ Failed to get dashboard data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing data structure: {e}")
    
    print("\n✅ Performance test completed!")

if __name__ == "__main__":
    main() 
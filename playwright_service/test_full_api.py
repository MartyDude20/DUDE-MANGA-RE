#!/usr/bin/env python3
"""
Test the full API flow for manga details caching
"""

import time
import requests
import json

def test_full_api_flow():
    """Test the complete API flow for manga details"""
    print("=== FULL API FLOW TEST ===")
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code != 200:
            print("✗ Service not running")
            return False
        print("✓ Service is running")
    except Exception as e:
        print(f"✗ Service not accessible: {e}")
        return False
    
    # Test with a real manga
    test_manga_id = "bleach"
    test_source = "weebcentral"
    
    print(f"\nTesting with manga: {test_manga_id} from {test_source}")
    
    # First request - should be fresh
    print(f"\n1. First request (should be fresh):")
    start_time = time.time()
    
    try:
        response = requests.get(f"http://localhost:5000/manga/{test_source}/{test_manga_id}")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success ({duration:.2f}s)")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Cached: {data.get('cached', 'N/A')}")
            print(f"  Chapters: {len(data.get('chapters', []))}")
            print(f"  Author: {data.get('author', 'N/A')}")
            
            # Store the response for comparison
            first_response = data
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False
    
    # Wait a moment
    print(f"\nWaiting 2 seconds...")
    time.sleep(2)
    
    # Second request - should be cached
    print(f"\n2. Second request (should be cached):")
    start_time = time.time()
    
    try:
        response = requests.get(f"http://localhost:5000/manga/{test_source}/{test_manga_id}")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success ({duration:.2f}s)")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Cached: {data.get('cached', 'N/A')}")
            print(f"  Chapters: {len(data.get('chapters', []))}")
            print(f"  Author: {data.get('author', 'N/A')}")
            
            # Compare responses
            if data.get('cached') == True:
                print("✓ API correctly reported cached data")
                
                # Check if data is identical
                if (data.get('title') == first_response.get('title') and 
                    len(data.get('chapters', [])) == len(first_response.get('chapters', []))):
                    print("✓ Cached data matches original data")
                    return True
                else:
                    print("✗ Cached data doesn't match original data")
                    return False
            else:
                print("✗ API reported fresh data instead of cached")
                return False
        else:
            print(f"✗ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

def test_multiple_sources():
    """Test caching across multiple sources"""
    print(f"\n=== MULTIPLE SOURCES TEST ===")
    
    sources_to_test = ["weebcentral", "asurascans"]
    test_manga_ids = ["bleach", "bones-7d724e9d"]
    
    for i, (source, manga_id) in enumerate(zip(sources_to_test, test_manga_ids)):
        print(f"\nTesting {source} with {manga_id}:")
        
        # First request
        start_time = time.time()
        response = requests.get(f"http://localhost:5000/manga/{source}/{manga_id}")
        first_duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"  First: {first_duration:.2f}s, Cached: {data.get('cached', 'N/A')}")
        else:
            print(f"  First: Failed ({response.status_code})")
            continue
        
        # Second request
        start_time = time.time()
        response = requests.get(f"http://localhost:5000/manga/{source}/{manga_id}")
        second_duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Second: {second_duration:.2f}s, Cached: {data.get('cached', 'N/A')}")
            
            if data.get('cached') == True and second_duration < first_duration:
                print(f"  ✓ Cache working for {source}")
            else:
                print(f"  ✗ Cache not working for {source}")
        else:
            print(f"  Second: Failed ({response.status_code})")

def main():
    """Main test function"""
    print("FULL API FLOW TESTING")
    print("=" * 50)
    
    # Test basic flow
    success = test_full_api_flow()
    
    if success:
        print(f"\n✓ Basic API flow working correctly")
    else:
        print(f"\n✗ Basic API flow failed")
        return
    
    # Test multiple sources
    test_multiple_sources()
    
    print(f"\n" + "=" * 50)
    print("API FLOW TESTING COMPLETE")

if __name__ == "__main__":
    main() 
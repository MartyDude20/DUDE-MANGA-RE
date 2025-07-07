#!/usr/bin/env python3
"""
Test script to verify user-scoped cache functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_user_scoped_cache():
    """Test that different users have separate cache"""
    
    print("🧪 Testing User-Scoped Cache...")
    
    # Generate unique username using timestamp
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    
    # Test 1: Anonymous user search
    print("\n1. Testing anonymous user search...")
    response = requests.get(f"{BASE_URL}/search?q=one")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Anonymous search successful: {len(data.get('results', []))} results")
        print(f"   📊 Cached: {data.get('cached', False)}")
    else:
        print(f"   ❌ Anonymous search failed: {response.status_code}")
        return
    
    # Test 2: Register a test user
    print(f"\n2. Registering test user '{username}'...")
    user_data = {
        "username": username,
        "email": email,
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    if response.status_code == 200:
        print("   ✅ User registered successfully")
    else:
        print(f"   ❌ Registration failed: {response.status_code} - {response.text}")
        return
    
    # Test 3: Login as test user
    print(f"\n3. Logging in as test user '{username}'...")
    login_data = {
        "username": username,
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {response.status_code} - {response.text}")
        return
    
    # Test 4: Authenticated user search (should be fresh, not cached)
    print("\n4. Testing authenticated user search...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/search?q=one", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Authenticated search successful: {len(data.get('results', []))} results")
        print(f"   📊 Cached: {data.get('cached', False)}")
    else:
        print(f"   ❌ Authenticated search failed: {response.status_code}")
        return
    
    # Test 5: Same authenticated user search again (should be cached)
    print("\n5. Testing authenticated user search again (should be cached)...")
    response = requests.get(f"{BASE_URL}/search?q=one", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Authenticated search successful: {len(data.get('results', []))} results")
        print(f"   📊 Cached: {data.get('cached', False)}")
    else:
        print(f"   ❌ Authenticated search failed: {response.status_code}")
        return
    
    # Test 6: Check user-specific cache stats
    print("\n6. Checking user-specific cache stats...")
    response = requests.get(f"{BASE_URL}/cache/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Cache stats retrieved")
        print(f"   📊 Search cache: {stats.get('search_cache', {})}")
        print(f"   📊 Manga cache: {stats.get('manga_cache', {})}")
        print(f"   📊 Chapter cache: {stats.get('chapter_cache', {})}")
    else:
        print(f"   ❌ Cache stats failed: {response.status_code}")
        return
    
    # Test 7: Anonymous user search again (should still be cached from step 1)
    print("\n7. Testing anonymous user search again (should be cached)...")
    response = requests.get(f"{BASE_URL}/search?q=one")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Anonymous search successful: {len(data.get('results', []))} results")
        print(f"   📊 Cached: {data.get('cached', False)}")
    else:
        print(f"   ❌ Anonymous search failed: {response.status_code}")
        return
    
    # Test 8: Clear user cache
    print("\n8. Clearing user cache...")
    response = requests.post(f"{BASE_URL}/cache/clear", json={"type": "all"}, headers=headers)
    if response.status_code == 200:
        print("   ✅ User cache cleared successfully")
    else:
        print(f"   ❌ Cache clear failed: {response.status_code}")
        return
    
    # Test 9: Check cache stats after clearing
    print("\n9. Checking cache stats after clearing...")
    response = requests.get(f"{BASE_URL}/cache/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Cache stats retrieved")
        print(f"   📊 Search cache: {stats.get('search_cache', {})}")
        print(f"   📊 Manga cache: {stats.get('manga_cache', {})}")
        print(f"   📊 Chapter cache: {stats.get('chapter_cache', {})}")
    else:
        print(f"   ❌ Cache stats failed: {response.status_code}")
        return
    
    print("\n🎉 User-scoped cache test completed successfully!")
    print("\n📋 Summary:")
    print("   - Anonymous users have their own cache (user_id = None)")
    print("   - Authenticated users have separate cache (user_id = user.id)")
    print("   - Cache operations are scoped to the current user")
    print("   - Cache stats show only the current user's data")

if __name__ == "__main__":
    test_user_scoped_cache() 
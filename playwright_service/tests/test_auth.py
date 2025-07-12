import requests
import time

BASE_URL = 'http://localhost:5000'

def test_auth_system():
    """Test the complete authentication system"""
    session = requests.Session()
    
    # Generate unique username using timestamp
    timestamp = int(time.time())
    username = f'testuser_{timestamp}'
    
    print("🔐 Testing JWT Authentication System")
    print("=" * 50)
    
    # Test 1: Register a new user
    print(f"\n1. Testing User Registration... (username: {username})")
    register_data = {
        'username': username,
        'email': f'{username}@example.com',
        'password': 'securepass123'
    }
    
    response = session.post(f'{BASE_URL}/register', json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Registration failed!")
        return
    
    print("✅ Registration successful!")
    
    # Test 2: Login
    print("\n2. Testing Login...")
    login_data = {
        'username': username,
        'password': 'securepass123'
    }
    
    response = session.post(f'{BASE_URL}/login', json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
    
    # Extract access token from response headers
    access_token = response.headers.get('Authorization', '').replace('Bearer ', '')
    if access_token:
        session.headers.update({'Authorization': f'Bearer {access_token}'})
        print("✅ Login successful! Access token received.")
    else:
        print("❌ No access token received!")
        return
    
    # Test 3: Get current user info
    print("\n3. Testing Get Current User...")
    response = session.get(f'{BASE_URL}/me')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ User info retrieved successfully!")
    else:
        print("❌ Failed to get user info!")
    
    # Test 4: Test protected endpoint (cache stats)
    print("\n4. Testing Protected Endpoint (Cache Stats)...")
    response = session.get(f'{BASE_URL}/cache/stats')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Protected endpoint accessible!")
    else:
        print("❌ Protected endpoint failed!")
    
    # Test 5: Test token refresh
    print("\n5. Testing Token Refresh...")
    response = session.post(f'{BASE_URL}/refresh')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        # Update access token if new one provided
        new_access_token = response.headers.get('Authorization', '').replace('Bearer ', '')
        if new_access_token:
            session.headers.update({'Authorization': f'Bearer {new_access_token}'})
            print("✅ Token refreshed successfully!")
        else:
            print("❌ No new access token received!")
    else:
        print("❌ Token refresh failed!")
    
    # Test 6: Test logout
    print("\n6. Testing Logout...")
    response = session.post(f'{BASE_URL}/logout')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Logout successful!")
    else:
        print("❌ Logout failed!")
    
    # Test 7: Verify logout worked (should fail)
    print("\n7. Verifying Logout (should fail)...")
    response = session.get(f'{BASE_URL}/me')
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Logout verification successful - token is invalid!")
    else:
        print("❌ Logout verification failed - token still valid!")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")

if __name__ == '__main__':
    test_auth_system() 
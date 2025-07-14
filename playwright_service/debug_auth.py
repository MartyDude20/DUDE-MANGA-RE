#!/usr/bin/env python3
"""
Debug script to test authentication flow
"""

import requests
import json
import time

def test_auth_flow():
    """Test the complete authentication flow"""
    print("=== AUTHENTICATION FLOW DEBUG ===")
    
    # Test 1: Check if services are running
    print("1. Checking services...")
    
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✓ Backend service running")
        else:
            print("✗ Backend service not responding")
            return
    except Exception as e:
        print(f"✗ Backend service error: {e}")
        return
    
    try:
        response = requests.get("http://localhost:3006/api/health")
        if response.status_code == 200:
            print("✓ Proxy service running")
        else:
            print("✗ Proxy service not responding")
            return
    except Exception as e:
        print(f"✗ Proxy service error: {e}")
        return
    
    # Test 2: Test /me endpoint directly on backend
    print("\n2. Testing /me endpoint on backend...")
    try:
        response = requests.get("http://localhost:5000/me")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Backend /me endpoint working (correctly requires auth)")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Backend /me error: {e}")
    
    # Test 3: Test /api/me endpoint through proxy
    print("\n3. Testing /api/me endpoint through proxy...")
    try:
        response = requests.get("http://localhost:3006/api/me")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Proxy /api/me endpoint working (correctly requires auth)")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Proxy /api/me error: {e}")
    
    # Test 4: Test with invalid token
    print("\n4. Testing with invalid token...")
    try:
        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = requests.get("http://localhost:3006/api/me", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Invalid token correctly rejected")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Invalid token test error: {e}")
    
    # Test 5: Test login flow
    print("\n5. Testing login flow...")
    try:
        # First, try to register a test user
        test_username = f"testuser_{int(time.time())}"
        register_data = {
            'username': test_username,
            'email': f'{test_username}@example.com',
            'password': 'testpass123'
        }
        
        response = requests.post("http://localhost:3006/api/register", json=register_data)
        print(f"Register status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Registration successful")
            
            # Now try to login
            login_data = {
                'username': test_username,
                'password': 'testpass123'
            }
            
            response = requests.post("http://localhost:3006/api/login", json=login_data)
            print(f"Login status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Login successful")
                
                # Extract access token
                access_token = response.headers.get('Authorization', '').replace('Bearer ', '')
                if access_token:
                    print(f"✓ Access token received: {access_token[:20]}...")
                    
                    # Test /api/me with valid token
                    print("\n6. Testing /api/me with valid token...")
                    headers = {'Authorization': f'Bearer {access_token}'}
                    response = requests.get("http://localhost:3006/api/me", headers=headers)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        print(f"✓ User info retrieved: {user_data.get('username')}")
                        
                        # Test token refresh
                        print("\n7. Testing token refresh...")
                        response = requests.post("http://localhost:3006/api/refresh")
                        print(f"Refresh status: {response.status_code}")
                        
                        if response.status_code == 200:
                            new_token = response.headers.get('Authorization', '').replace('Bearer ', '')
                            if new_token:
                                print("✓ Token refresh successful")
                            else:
                                print("✗ No new token received")
                        else:
                            print(f"✗ Token refresh failed: {response.text}")
                    else:
                        print(f"✗ /api/me failed: {response.text}")
                else:
                    print("✗ No access token received")
            else:
                print(f"✗ Login failed: {response.text}")
        else:
            print(f"✗ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Login flow error: {e}")

def test_frontend_auth_context():
    """Test what the frontend AuthContext would see"""
    print("\n=== FRONTEND AUTH CONTEXT SIMULATION ===")
    
    # Simulate the frontend's token verification process
    print("1. Simulating frontend token verification...")
    
    # Check if there's a token in localStorage (we can't access this directly)
    # But we can test the /api/me endpoint that the frontend calls
    
    try:
        response = requests.get("http://localhost:3006/api/me")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Frontend would see: No valid token (401)")
            print("  This would trigger logout() in AuthContext")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Frontend simulation error: {e}")

def main():
    """Main debug function"""
    print("AUTHENTICATION DEBUGGING")
    print("=" * 50)
    
    test_auth_flow()
    test_frontend_auth_context()
    
    print("\n" + "=" * 50)
    print("DEBUGGING COMPLETE")
    
    print("\nPOSSIBLE ISSUES:")
    print("1. Token not being stored in localStorage")
    print("2. Token being cleared on page refresh")
    print("3. Token expiration")
    print("4. CORS issues")
    print("5. Cookie issues with refresh tokens")

if __name__ == "__main__":
    main() 
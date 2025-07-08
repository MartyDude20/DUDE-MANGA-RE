#!/usr/bin/env python3
"""
Test Password Reset Endpoint
Tests the actual password reset functionality
"""

import requests
import json

def test_password_reset():
    """Test the password reset endpoint"""
    
    # Test data
    test_email = input("Enter email to test password reset: ")
    
    # Test password reset request
    print(f"📧 Testing password reset for: {test_email}")
    
    try:
        response = requests.post(
            'http://localhost:5000/password-reset/request',
            json={'email': test_email},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Password reset request successful!")
            print("   Check your email for the reset link")
        else:
            print("❌ Password reset request failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        print("   Make sure the backend is running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Password Reset Endpoint Test")
    print("=" * 40)
    test_password_reset()
    print("=" * 40) 
#!/usr/bin/env python3
"""
Simple Email Test Script
Tests email sending functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the playwright_service directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'playwright_service'))

def test_email_sending():
    """Test email sending functionality"""
    try:
        from flask import Flask
        from email_config import send_password_reset_email
        
        # Load environment variables
        load_dotenv()
        
        # Check if email settings are configured
        email = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        
        if not email or not password:
            print("❌ Email settings not configured in .env file")
            print("   Please set MAIL_USERNAME and MAIL_PASSWORD")
            return False
        
        # Create a test Flask app
        app = Flask(__name__)
        
        # Configure email
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
        app.config['MAIL_USERNAME'] = email
        app.config['MAIL_PASSWORD'] = password
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', email)
        
        with app.app_context():
            # Test sending an email
            test_email = input("Enter test email address: ")
            reset_url = "http://localhost:5173/reset-password?token=test-token"
            
            print(f"📧 Sending test email to {test_email}...")
            
            success, error = send_password_reset_email(test_email, "TestUser", reset_url)
            
            if success:
                print("✅ Test email sent successfully!")
                print("   Check your email inbox (and spam folder)")
                return True
            else:
                print(f"❌ Failed to send email: {error}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

def main():
    print("🧪 Email Test Script")
    print("=" * 40)
    
    # Check if Flask-Mail is installed
    try:
        import flask_mail
        print("✅ Flask-Mail is installed")
    except ImportError:
        print("❌ Flask-Mail is NOT installed")
        print("   Run: pip install flask-mail==0.9.1")
        return
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Create a .env file with your email settings")
        return
    
    print("✅ .env file found")
    
    # Test email sending
    print()
    success = test_email_sending()
    
    if success:
        print("\n🎉 Email test completed successfully!")
    else:
        print("\n⚠️  Email test failed. Check your configuration.")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main() 
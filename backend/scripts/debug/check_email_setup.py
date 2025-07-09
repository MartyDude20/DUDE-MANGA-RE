#!/usr/bin/env python3
"""
Email Setup Checker
This script checks if Flask-Mail is installed and tests email configuration
"""

import sys
import os
from dotenv import load_dotenv

def check_flask_mail():
    """Check if Flask-Mail is installed"""
    try:
        import flask_mail
        print("✅ Flask-Mail is installed")
        print(f"   Version: {flask_mail.__version__}")
        return True
    except ImportError:
        print("❌ Flask-Mail is NOT installed")
        print("   Run: pip install flask-mail==0.9.1")
        return False

def check_env_file():
    """Check if .env file exists and has email settings"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        print("   Create a .env file in your project root")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    load_dotenv()
    
    # Check email settings
    email_settings = {
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': os.getenv('MAIL_PORT'),
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER')
    }
    
    missing_settings = []
    for key, value in email_settings.items():
        if not value:
            missing_settings.append(key)
        else:
            # Hide password for security
            display_value = value if key != 'MAIL_PASSWORD' else '***' if value != 'your-app-password' else 'NOT SET'
            print(f"   {key}: {display_value}")
    
    if missing_settings:
        print(f"❌ Missing email settings: {', '.join(missing_settings)}")
        return False
    
    if email_settings['MAIL_PASSWORD'] == 'your-app-password':
        print("❌ MAIL_PASSWORD is not set to a real password")
        return False
    
    print("✅ All email settings are configured")
    return True

def test_email_config():
    """Test email configuration with Flask"""
    try:
        from flask import Flask
        from playwright_service.email_config import init_email
        
        app = Flask(__name__)
        init_email(app)
        
        print("✅ Email configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False

def main():
    print("🔍 Email Setup Checker")
    print("=" * 50)
    
    flask_mail_ok = check_flask_mail()
    print()
    
    env_ok = check_env_file()
    print()
    
    if flask_mail_ok and env_ok:
        config_ok = test_email_config()
        print()
        
        if config_ok:
            print("🎉 Email setup looks good!")
            print("   You can now test password reset functionality")
        else:
            print("⚠️  Email configuration has issues")
    else:
        print("⚠️  Please fix the issues above before testing email")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 
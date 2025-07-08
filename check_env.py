#!/usr/bin/env python3
"""
Check .env file contents and email configuration
"""

import os
from dotenv import load_dotenv

def check_env_file():
    """Check .env file contents"""
    print("🔍 Checking .env file contents...")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    load_dotenv()
    
    # Check email settings
    email_settings = {
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': os.getenv('MAIL_PORT'),
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS'),
        'MAIL_USE_SSL': os.getenv('MAIL_USE_SSL'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER')
    }
    
    print("\n📧 Email Configuration:")
    print("-" * 30)
    
    for key, value in email_settings.items():
        if key == 'MAIL_PASSWORD':
            # Hide password for security
            if value:
                display_value = '*' * len(value) if value != 'your-app-password' else 'NOT SET'
            else:
                display_value = 'NOT SET'
        else:
            display_value = value or 'NOT SET'
        
        print(f"{key}: {display_value}")
    
    # Check for common issues
    print("\n🔍 Potential Issues:")
    print("-" * 30)
    
    issues = []
    
    if not email_settings['MAIL_SERVER']:
        issues.append("❌ MAIL_SERVER is not set")
    elif email_settings['MAIL_SERVER'] != 'smtp.gmail.com':
        issues.append(f"⚠️  MAIL_SERVER is '{email_settings['MAIL_SERVER']}', expected 'smtp.gmail.com'")
    
    if not email_settings['MAIL_PORT']:
        issues.append("❌ MAIL_PORT is not set")
    elif email_settings['MAIL_PORT'] != '587':
        issues.append(f"⚠️  MAIL_PORT is '{email_settings['MAIL_PORT']}', expected '587'")
    
    if not email_settings['MAIL_USERNAME']:
        issues.append("❌ MAIL_USERNAME is not set")
    
    if not email_settings['MAIL_PASSWORD']:
        issues.append("❌ MAIL_PASSWORD is not set")
    elif email_settings['MAIL_PASSWORD'] == 'your-app-password':
        issues.append("❌ MAIL_PASSWORD is still set to placeholder value")
    
    if not email_settings['MAIL_DEFAULT_SENDER']:
        issues.append("❌ MAIL_DEFAULT_SENDER is not set")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ All email settings look correct")
    
    return len(issues) == 0

def test_smtp_connection():
    """Test SMTP connection with current settings"""
    print("\n🔍 Testing SMTP connection...")
    print("-" * 30)
    
    load_dotenv()
    
    server = os.getenv('MAIL_SERVER') or ''
    port = os.getenv('MAIL_PORT') or ''
    username = os.getenv('MAIL_USERNAME') or ''
    password = os.getenv('MAIL_PASSWORD') or ''
    
    if not all([server, port, username, password]):
        print("❌ Missing required email settings")
        return False
    
    try:
        import smtplib
        
        print(f"Connecting to {server}:{port}...")
        
        # Create SMTP connection
        smtp = smtplib.SMTP(server, int(port))
        smtp.starttls()
        
        print("✅ SMTP connection established")
        print("Attempting login...")
        
        smtp.login(username, password)
        print("✅ SMTP authentication successful")
        
        smtp.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 .env File and Email Configuration Checker")
    print("=" * 60)
    
    env_ok = check_env_file()
    
    if env_ok:
        print("\n" + "=" * 60)
        smtp_ok = test_smtp_connection()
        
        if smtp_ok:
            print("\n🎉 Email configuration is working!")
        else:
            print("\n⚠️  Email configuration has issues")
    else:
        print("\n⚠️  Please fix the issues above")
    
    print("\n" + "=" * 60) 
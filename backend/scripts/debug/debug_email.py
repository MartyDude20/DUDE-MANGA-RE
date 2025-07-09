#!/usr/bin/env python3
"""
Enhanced Email Debugging Script
Tests email sending with detailed error reporting
"""

import os
import sys
import smtplib
from dotenv import load_dotenv

# Add the playwright_service directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'playwright_service'))

def test_smtp_connection():
    """Test SMTP connection directly"""
    load_dotenv()
    
    server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    port = int(os.getenv('MAIL_PORT', 587))
    username = os.getenv('MAIL_USERNAME') or ''
    password = os.getenv('MAIL_PASSWORD') or ''
    use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    
    print(f"🔍 Testing SMTP connection to {server}:{port}")
    print(f"   Username: {username}")
    print(f"   TLS: {use_tls}")
    
    try:
        # Create SMTP connection
        if use_tls:
            smtp = smtplib.SMTP(server, port)
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(server, port)
        
        # Login
        smtp.login(username, password)
        print("✅ SMTP connection and authentication successful")
        
        # Test sending a simple email
        test_email = input("Enter test email address: ")
        
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = username or ''
        msg['To'] = test_email
        msg['Subject'] = "Test Email - Dude Manga"
        
        body = "This is a test email from Dude Manga to verify email functionality."
        msg.attach(MIMEText(body, 'plain'))
        
        print(f"📧 Sending test email to {test_email}...")
        smtp.send_message(msg)
        print("✅ Test email sent successfully via direct SMTP")
        
        smtp.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication failed: {e}")
        print("   This usually means:")
        print("   - Wrong password")
        print("   - For Gmail: You need an App Password, not your regular password")
        print("   - 2-Factor Authentication not enabled")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection failed: {e}")
        print("   This usually means:")
        print("   - Wrong server/port")
        print("   - Firewall blocking connection")
        print("   - Network issues")
        return False
        
    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_flask_mail():
    """Test Flask-Mail functionality"""
    try:
        from flask import Flask
        from email_config import init_email, send_password_reset_email
        
        print("\n🔍 Testing Flask-Mail configuration...")
        
        # Create Flask app
        app = Flask(__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Configure email
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
        
        # Initialize email
        init_email(app)
        
        with app.app_context():
            test_email = input("Enter test email for Flask-Mail: ")
            reset_url = "http://localhost:5173/reset-password?token=test-token"
            
            print(f"📧 Testing Flask-Mail email to {test_email}...")
            success, error = send_password_reset_email(test_email, "TestUser", reset_url)
            
            if success:
                print("✅ Flask-Mail email sent successfully!")
                return True
            else:
                print(f"❌ Flask-Mail failed: {error}")
                return False
                
    except Exception as e:
        print(f"❌ Flask-Mail test error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    print("🔧 Enhanced Email Debugging")
    print("=" * 50)
    
    # Check environment
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return
    
    load_dotenv()
    
    # Check required settings
    required_settings = ['MAIL_USERNAME', 'MAIL_PASSWORD']
    missing = [s for s in required_settings if not os.getenv(s)]
    
    if missing:
        print(f"❌ Missing settings: {', '.join(missing)}")
        return
    
    print("✅ Environment variables loaded")
    
    # Test 1: Direct SMTP
    print("\n" + "=" * 30)
    print("TEST 1: Direct SMTP Connection")
    print("=" * 30)
    smtp_success = test_smtp_connection()
    
    # Test 2: Flask-Mail
    print("\n" + "=" * 30)
    print("TEST 2: Flask-Mail Integration")
    print("=" * 30)
    flask_success = test_flask_mail()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if smtp_success and flask_success:
        print("🎉 All tests passed! Email functionality is working.")
    elif smtp_success and not flask_success:
        print("⚠️  SMTP works but Flask-Mail has issues.")
        print("   This might be a Flask-Mail configuration problem.")
    elif not smtp_success and flask_success:
        print("⚠️  Flask-Mail works but direct SMTP failed.")
        print("   This is unusual - there might be a configuration issue.")
    else:
        print("❌ Both tests failed.")
        print("   Check your email credentials and network connection.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 
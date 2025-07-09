"""
Email configuration for password reset functionality
"""
import os
from flask_mail import Mail, Message
from flask import current_app, render_template_string

# Initialize Flask-Mail
mail = Mail()

def init_email(app):
    """Initialize email configuration with Flask app"""
    # Ensure environment variables are loaded
    from dotenv import load_dotenv
    load_dotenv()
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Test the configuration
    print(f"📧 Email configured: {app.config['MAIL_USERNAME']} via {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    
    # Verify configuration
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("⚠️  Warning: Email credentials not properly configured")
    else:
        print("✅ Email credentials configured")

def send_password_reset_email(user_email, username, reset_url):
    """
    Send password reset email to user
    
    Args:
        user_email (str): User's email address
        username (str): User's username
        reset_url (str): Password reset URL with token
    """
    try:
        # Email template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset - Dude Manga</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #1f2937; color: white; padding: 20px; text-align: center; }
                .content { background: #f9fafb; padding: 30px; }
                .button { display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
                .footer { background: #e5e7eb; padding: 20px; text-align: center; font-size: 14px; color: #6b7280; }
                .warning { background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Dude Manga</h1>
                    <p>Password Reset Request</p>
                </div>
                
                <div class="content">
                    <h2>Hello {{ username }},</h2>
                    
                    <p>We received a request to reset your password for your Dude Manga account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{{ reset_url }}" class="button">Reset Password</a>
                    </div>
                    
                    <div class="warning">
                        <strong>Important:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this password reset, please ignore this email</li>
                            <li>For security, this link can only be used once</li>
                        </ul>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #3b82f6;">{{ reset_url }}</p>
                    
                    <p>Thanks,<br>The Dude Manga Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>If you have any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_template = """
        Password Reset Request - Dude Manga
        
        Hello {{ username }},
        
        We received a request to reset your password for your Dude Manga account.
        
        To reset your password, visit this link:
        {{ reset_url }}
        
        Important:
        - This link will expire in 1 hour
        - If you didn't request this password reset, please ignore this email
        - For security, this link can only be used once
        
        Thanks,
        The Dude Manga Team
        
        This is an automated message. Please do not reply to this email.
        """
        
        # Render templates
        html_content = render_template_string(html_template, username=username, reset_url=reset_url)
        text_content = render_template_string(text_template, username=username, reset_url=reset_url)
        
        # Create message
        msg = Message(
            subject="Password Reset Request - Dude Manga",
            recipients=[user_email],
            body=text_content,
            html=html_content
        )
        
        # Add headers to improve deliverability
        msg.extra_headers = {
            'X-Priority': '1',
            'X-MSMail-Priority': 'High',
            'Importance': 'high',
            'X-Mailer': 'Dude Manga App'
        }
        
        # Send email
        print(f"📧 Attempting to send email to {user_email}...")
        
        # Get current app context for debugging
        from flask import current_app
        if current_app:
            print(f"   Using server: {current_app.config.get('MAIL_SERVER', 'NOT SET')}")
            print(f"   Using port: {current_app.config.get('MAIL_PORT', 'NOT SET')}")
            print(f"   Using username: {current_app.config.get('MAIL_USERNAME', 'NOT SET')}")
        
        mail.send(msg)
        print(f"✅ Email sent successfully to {user_email}")
        
        return True, None
        
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False, str(e)

def send_password_reset_success_email(user_email, username):
    """
    Send confirmation email when password is successfully reset
    
    Args:
        user_email (str): User's email address
        username (str): User's username
    """
    try:
        # Email template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset Successful - Dude Manga</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #059669; color: white; padding: 20px; text-align: center; }
                .content { background: #f9fafb; padding: 30px; }
                .footer { background: #e5e7eb; padding: 20px; text-align: center; font-size: 14px; color: #6b7280; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Dude Manga</h1>
                    <p>Password Reset Successful</p>
                </div>
                
                <div class="content">
                    <h2>Hello {{ username }},</h2>
                    
                    <p>Your password has been successfully reset for your Dude Manga account.</p>
                    
                    <p>You can now log in to your account using your new password.</p>
                    
                    <p>If you did not perform this password reset, please contact our support team immediately.</p>
                    
                    <p>Thanks,<br>The Dude Manga Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_template = """
        Password Reset Successful - Dude Manga
        
        Hello {{ username }},
        
        Your password has been successfully reset for your Dude Manga account.
        
        You can now log in to your account using your new password.
        
        If you did not perform this password reset, please contact our support team immediately.
        
        Thanks,
        The Dude Manga Team
        
        This is an automated message. Please do not reply to this email.
        """
        
        # Render templates
        html_content = render_template_string(html_template, username=username)
        text_content = render_template_string(text_template, username=username)
        
        # Create message
        msg = Message(
            subject="Password Reset Successful - Dude Manga",
            recipients=[user_email],
            body=text_content,
            html=html_content
        )
        
        # Send email
        mail.send(msg)
        
        return True, None
        
    except Exception as e:
        return False, str(e) 
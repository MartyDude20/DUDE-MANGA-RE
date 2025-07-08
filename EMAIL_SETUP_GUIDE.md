# Email Service Setup Guide

## Quick Setup (Recommended)

Run the automated setup script:
```bash
setup_email.bat
```

This will:
1. Install Flask-Mail dependency
2. Prompt for your email credentials
3. Create a `.env` file with all necessary settings

## Manual Setup

### Step 1: Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate

# Install Flask-Mail
pip install flask-mail==0.9.1
```

### Step 2: Create .env File

Create a `.env` file in your project root with these settings:

#### For Gmail:
```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

#### For Outlook/Hotmail:
```env
# Email Configuration
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@outlook.com
```

### Step 3: Gmail App Password Setup

If using Gmail, you MUST create an App Password:

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click "Security" in the left sidebar
3. Enable "2-Step Verification" if not already enabled
4. Go to "App passwords" (under 2-Step Verification)
5. Select "Mail" as the app and "Other" as device
6. Click "Generate"
7. Copy the 16-character password
8. Use this password in your `MAIL_PASSWORD` setting

### Step 4: Test the Setup

1. Start your backend server:
   ```bash
   cd playwright_service
   python app.py
   ```

2. Test password reset:
   - Go to your app's login page
   - Click "Forgot your password?"
   - Enter an email address
   - Check if the email is received

## Troubleshooting

### Common Issues:

1. **"Authentication failed" error**
   - Make sure you're using an App Password for Gmail
   - Check that 2-Factor Authentication is enabled

2. **"Connection refused" error**
   - Check your firewall settings
   - Verify the SMTP server and port are correct

3. **"Email not received"**
   - Check spam/junk folder
   - Verify email address is correct
   - Check server logs for errors

### Debug Mode:

To see detailed email errors, check your backend console output. Failed emails will be logged with error details.

## Security Notes

- Never commit your `.env` file to version control
- Use App Passwords instead of regular passwords
- Consider using environment variables in production
- Regularly rotate your email passwords

## Production Setup

For production, consider using:
- **SendGrid**: Professional email service
- **Mailgun**: Reliable email delivery
- **AWS SES**: Cost-effective for high volume

Update the SMTP settings accordingly for your chosen service. 
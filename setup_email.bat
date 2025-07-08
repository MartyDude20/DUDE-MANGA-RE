@echo off
echo Setting up Email Service for Dude Manga...
echo.

echo Step 1: Installing Flask-Mail...
cd /d "%~dp0"
call venv\Scripts\activate
pip install flask-mail==0.9.1

echo.
echo Step 2: Creating .env file with email configuration...
echo.

set /p EMAIL_ADDRESS="Enter your email address (e.g., your-email@gmail.com): "
set /p EMAIL_PASSWORD="Enter your email password or app password: "

echo Creating .env file...
(
echo FIRECRAWL_API_KEY=your_firecrawl_api_key_here
echo FLASK_PORT=3006
echo PLAYWRIGHT_PORT=5000
echo REACT_PORT=3005
echo.
echo # Database Configuration
echo DATABASE_URL=postgresql://username:password@localhost:5432/manga_db
echo SECRET_KEY=your-secret-key-change-this-in-production
echo.
echo # Email Configuration ^(for password reset^)
echo MAIL_SERVER=smtp.gmail.com
echo MAIL_PORT=587
echo MAIL_USE_TLS=true
echo MAIL_USE_SSL=false
echo MAIL_USERNAME=%EMAIL_ADDRESS%
echo MAIL_PASSWORD=%EMAIL_PASSWORD%
echo MAIL_DEFAULT_SENDER=%EMAIL_ADDRESS%
) > .env

echo.
echo Email configuration created successfully!
echo.
echo IMPORTANT: If using Gmail, make sure to:
echo 1. Enable 2-Factor Authentication
echo 2. Generate an App Password at: https://myaccount.google.com/apppasswords
echo 3. Use the App Password instead of your regular password
echo.
echo Your .env file has been created with the email settings.
echo You can now start the backend server and test password reset functionality.
echo.
pause 
@echo off
echo Starting Dude Manga Services...
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Install Python dependencies if requirements.txt exists
if exist requirements.txt (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo.
echo Starting services...
echo ================================================

REM Start Playwright service in background
echo Starting Playwright service...
start "Playwright Service" cmd /k "cd playwright_service && python app.py"

REM Wait a moment for Playwright to start
timeout /t 3 /nobreak >nul

REM Start Flask proxy in background
echo Starting Flask proxy...
start "Flask Proxy" cmd /k "cd proxy && python app.py"

REM Wait a moment for Flask to start
timeout /t 2 /nobreak >nul

REM Start React frontend
echo Starting React frontend...
echo.
echo ================================================
echo All services are starting...
echo React Frontend will open at: http://localhost:3005
echo Flask Proxy is running at: http://localhost:3006
echo Playwright Service is running at: http://localhost:5000
echo ================================================
echo.
echo Press any key to stop all services...
pause >nul

REM Kill all background processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo Services stopped.
pause 
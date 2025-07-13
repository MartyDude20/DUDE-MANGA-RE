@echo off
echo Starting Enhanced Dude Manga Reader Services...
echo.

echo [1/4] Starting Backend (Port 5000)...
start "Backend" cmd /k "cd playwright_service && python app.py"

echo [2/4] Starting Proxy (Port 3006)...
start "Proxy" cmd /k "cd proxy && python app.py"

echo [3/4] Starting Frontend (Port 5173)...
start "Frontend" cmd /k "npm run dev"

echo [4/4] Running Database Migration...
cd playwright_service
python migrate_database.py
cd ..

echo.
echo All services are starting up...
echo.
echo Service URLs:
echo - Frontend: http://localhost:5173
echo - Proxy: http://localhost:3006
echo - Backend: http://localhost:5000
echo.
echo Please wait for all services to fully start before accessing the application.
echo.
pause 
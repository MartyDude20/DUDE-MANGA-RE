@echo off
echo Installing Flask-Mail dependency...
cd /d "%~dp0"
call venv\Scripts\activate
pip install flask-mail==0.9.1
echo Installation complete!
pause 
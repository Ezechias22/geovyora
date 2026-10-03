@echo off
cd /d "%~dp0"
if not exist .venv py -3 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
python manage.py migrate
python -c "from db import one; exit(0 if one('SELECT id FROM staff LIMIT 1') else 1)"
if errorlevel 1 python manage.py create-admin
start "Geovyora Worker" cmd /k "python worker.py"
start "" python -c "import time,webbrowser; time.sleep(2); webbrowser.open('http://localhost:8000')"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause

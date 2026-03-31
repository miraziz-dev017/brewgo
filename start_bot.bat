@echo off
setlocal

cd /d "%~dp0"

if not exist ".env" (
  echo [XATO] .env topilmadi.
  echo .env.example faylidan nusxa oling va .env deb nomlang.
  echo Keyin BOT_TOKEN, PUBLIC_BASE_URL, WEBHOOK_SECRET ni toldiring.
  pause
  exit /b 1
)

where py >nul 2>nul
if %errorlevel% neq 0 (
  echo [XATO] Python topilmadi. Python 3.11+ ornating.
  pause
  exit /b 1
)

if not exist ".venv" (
  echo Virtual env yaratilmoqda...
  py -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Paketlar ornatilmoqda...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Bot server ishga tushmoqda...
python -m uvicorn bot_server:app --host 0.0.0.0 --port 8000

endlocal

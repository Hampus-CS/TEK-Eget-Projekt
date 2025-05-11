@echo off
cd /d %~dp0

REM -------------------------------------------------
REM 0) Installera Python-dependencies i venv
IF EXIST ".\venv\Scripts\activate.bat" (
    call .\venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    echo Virtualenv inte funnen vid .\venv\Scripts\activate.bat
    echo Skapa en venv med: python -m venv venv
)

REM -------------------------------------------------
REM 1) Starta Flask-API/UI
start "API UI" cmd /k "python api_ui.py"

REM -------------------------------------------------
REM 2) Vänta så Flask hinner starta
timeout /t 5 /nobreak >nul

REM -------------------------------------------------
REM 3) Starta system_monitor
start "System Monitor" cmd /k "python system_monitor.py"

REM -------------------------------------------------
REM 4) Öppna webbläsaren
start "" "http://127.0.0.1:5000"

exit /b

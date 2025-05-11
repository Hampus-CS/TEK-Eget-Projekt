@echo off
REM -------------------------------------------------
REM Se till att vi är i projektets rot-katalog
cd /d %~dp0

REM -------------------------------------------------
REM 1) Aktivera Python-virtualenv (justera sökväg vid behov)
IF EXIST ".\venv\Scripts\activate.bat" (
    call .\venv\Scripts\activate.bat
) ELSE (
    echo Virtualenv inte funnen vid .\venv\Scripts\activate.bat
    echo Skapa en venv med: python -m venv venv
)

REM -------------------------------------------------
REM 2) Starta Flask-API/UI i eget fönster
start "API UI" cmd /k "python api_ui.py"

REM -------------------------------------------------
REM 3) Vänta så att Flask-servern hinner starta
timeout /t 5 /nobreak >nul

REM -------------------------------------------------
REM 4) Starta system_monitor i eget fönster
start "System Monitor" cmd /k "python system_monitor.py"

REM -------------------------------------------------
REM 5) Öppna webbläsaren
start "" "http://127.0.0.1:5000"

exit /b

@echo off
rem Double-click to start BikeFit. Close this window to stop it.
title BikeFit
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo BikeFit is not installed yet. Run these two commands in this folder once:
    echo.
    echo     python -m venv .venv
    echo     .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" app.py %*
rem Keep the window open after an error, for example when the port is already in use.
if errorlevel 1 pause

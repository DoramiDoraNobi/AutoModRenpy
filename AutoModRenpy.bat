@echo off
REM AutoModRenpy Launcher for Windows
REM Double-click this file to launch the GUI

echo ================================================
echo   AutoModRenpy - Android Renpy Mod Installer
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or newer from python.org
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Launching AutoModRenpy GUI...
echo.

REM Launch GUI
python main.py

if errorlevel 1 (
    echo.
    echo Program exited with errors
    pause
)

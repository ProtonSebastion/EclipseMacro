@echo off
title Eclipse Launcher
color 0a

echo.
echo  ✦ ECLIPSE MACRO ✦
echo  Checking requirements...
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo  [OK] Python found.

:: Check required libraries
echo  Checking libraries...

python -c "import customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [INSTALLING] customtkinter...
    pip install customtkinter
)

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [INSTALLING] pillow...
    pip install pillow
)

python -c "import pystray" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [INSTALLING] pystray...
    pip install pystray
)

python -c "import psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [INSTALLING] psutil...
    pip install psutil
)

echo  [OK] All libraries ready.
echo.
echo  Launching Eclipse Macro...
echo.

start "" pythonw Main.py
exit
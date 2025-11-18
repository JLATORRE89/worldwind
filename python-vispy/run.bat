@echo off
REM WorldWind Python - Launch Script for Windows

echo ==========================================
echo WorldWind Python - VisPy 3D Globe
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import vispy" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    pip install -r requirements.txt
    echo Dependencies installed
) else (
    echo Dependencies already installed
)

echo.
echo Launching WorldWind Python...
echo.

REM Run the application
python worldwind.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause

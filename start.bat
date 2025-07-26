@echo off
setlocal

:: Set the name of the virtual environment folder
set VENV_DIR=venv

:: Check if venv exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

:: Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

:: Install requirements
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

:: Run the Python script
echo Starting main.py...
python main.py

endlocal
pause

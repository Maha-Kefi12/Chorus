@echo off
setlocal enabledelayedexpansion

REM Python Scripts Runner for Windows
REM Fixes Unicode encoding issues

echo.
echo ========================================
echo   Python XML Generator Scripts
echo ========================================
echo.

REM Set console to UTF-8 encoding
chcp 65001 >nul 2>&1

REM Set Python environment variables for UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

echo Setting up Python environment for UTF-8...
echo Console encoding: UTF-8 (65001)
echo Python IO encoding: %PYTHONIOENCODING%

echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

python --version

echo.
echo Running Python XML generation scripts...
echo.

REM Try to run the Windows-specific version first
if exist "spring-ftl\src\main\resources\scripts\main_windows.py" (
    echo Using Windows-compatible script...
    cd "spring-ftl\src\main\resources\scripts"
    python main_windows.py
    cd ..\..\..\..\..
) else if exist "spring-ftl\src\main\resources\scripts\main.py" (
    echo Using standard script...
    cd "spring-ftl\src\main\resources\scripts"
    python main.py
    cd ..\..\..\..\..
) else (
    echo ERROR: Python scripts not found
    echo Expected location: spring-ftl\src\main\resources\scripts\
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Python Scripts Completed
echo ========================================
echo.
pause
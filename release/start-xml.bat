@echo off
REM Robust XML Generator Only Script

REM Ensure we are in the script's directory
cd /d %~dp0

echo ========================================
echo XML Generator Only
echo ========================================
echo.

REM Check if the executable exists
if not exist "xml-generator.exe" (
    echo ERROR: xml-generator.exe not found in current directory
    echo Please make sure you're running this from the correct directory
    echo.
    echo Available files in current directory:
    dir *.exe /b 2>nul
    echo.
    pause
    exit /b 1
)

REM Ensure output directory exists
if not exist ".idea\demo" mkdir ".idea\demo"

echo Starting XML Generator application...
echo This will generate XML files in the .idea/demo directory...
echo.

REM Start the XML generator and wait for it to complete
xml-generator.exe

REM Check if the application completed successfully
if %errorlevel% equ 0 (
    echo.
    echo XML generation completed successfully!
    echo Check the .idea/demo directory for generated XML files
) else (
    echo.
    echo ERROR: XML generation failed with error code: %errorlevel%
    echo Please check for error messages above or run start-debug.bat for more details.
)

echo.
echo Press any key to exit...
pause >nul 
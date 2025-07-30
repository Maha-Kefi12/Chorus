@echo off
echo ========================================
echo XML Generator Debug Mode
echo ========================================
echo.

REM Check current directory
echo Current directory: %CD%
echo.

REM Check if the executable exists
if exist "xml-generator.exe" (
    echo ✅ Found xml-generator.exe
    echo File size: 
    dir xml-generator.exe | findstr "xml-generator.exe"
) else (
    echo ❌ xml-generator.exe not found
    echo.
    echo Available files in current directory:
    dir *.exe
    echo.
    pause
    exit /b 1
)

echo.
echo Starting XML Generator with debug output...
echo ========================================
echo.

REM Start the XML generator with full output
xml-generator.exe

REM Capture the exit code
set EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo XML Generator finished
echo Exit code: %EXIT_CODE%
echo ========================================

REM Check if output directory was created
if exist ".idea\demo" (
    echo ✅ Output directory .idea\demo exists
    echo.
    echo Generated files:
    dir .idea\demo\*.xml /b 2>nul
    if %errorlevel% neq 0 (
        echo No XML files found in .idea\demo
    )
) else (
    echo ❌ Output directory .idea\demo not found
)

echo.
echo Press any key to exit...
pause >nul 
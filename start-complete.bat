@echo off
setlocal enabledelayedexpansion

REM Complete Application Startup Script for Windows
REM Starts Spring Boot application and runs Python XML generator scripts

echo.
echo ========================================
echo   Complete Application Startup
echo ========================================
echo.

REM Set console to UTF-8 encoding
chcp 65001 >nul 2>&1

REM Set Python environment variables for UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

REM Check Java installation
echo Checking Java installation...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 17 or higher to run this application
    pause
    exit /b 1
)

REM Display Java version
java -version

echo.
echo Starting Spring Boot application on port 8081...

REM Check if JAR file exists
if not exist "spring-ftl.jar" (
    if not exist "spring-ftl\target\spring-ftl-0.0.1-SNAPSHOT.jar" (
        echo ERROR: Spring Boot JAR file not found
        echo Please ensure spring-ftl.jar exists in the current directory
        echo OR build the application first: cd spring-ftl && mvnw clean package -DskipTests
        pause
        exit /b 1
    ) else (
        echo Using JAR from build directory...
        copy "spring-ftl\target\spring-ftl-0.0.1-SNAPSHOT.jar" "spring-ftl.jar" >nul
    )
)

echo.
echo Starting Spring Boot application...
start "Spring Boot Application" /B java -jar spring-ftl.jar --server.port=8081

echo Waiting 15 seconds for Spring Boot to start...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo   Running Python XML Generator
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Python is not installed or not in PATH
    echo Skipping Python XML generation scripts...
    goto :skip_python
)

python --version
echo Python environment configured for UTF-8

REM Run Python scripts
if exist "spring-ftl\src\main\resources\scripts\main_windows.py" (
    echo Using Windows-compatible Python script...
    cd "spring-ftl\src\main\resources\scripts"
    python main_windows.py
    cd ..\..\..\..\..
) else if exist "spring-ftl\src\main\resources\scripts\main.py" (
    echo Using standard Python script...
    cd "spring-ftl\src\main\resources\scripts"
    python main.py
    cd ..\..\..\..\..
) else (
    echo WARNING: Python scripts not found, skipping...
)

:skip_python

echo.
echo ========================================
echo   Startup Complete!
echo ========================================
echo.
echo Spring Boot Application: http://localhost:8081
echo.
echo To stop the application:
echo 1. Close the Spring Boot window that opened
echo 2. Or press Ctrl+C in the Spring Boot window  
echo 3. Or use Task Manager to end java.exe process
echo.

REM Run xml-generator.exe if it exists
if exist "xml-generator.exe" (
    echo Running xml-generator.exe...
    xml-generator.exe
    echo.
)

echo All processes completed!
pause
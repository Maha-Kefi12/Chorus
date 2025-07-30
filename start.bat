@echo off
setlocal enabledelayedexpansion

REM Spring Boot Application Startup Script for Windows
REM This script starts the Spring Boot application on port 8081

echo.
echo ========================================
echo   Spring Boot Application Startup
echo ========================================
echo.

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
echo Starting application...
start "Spring Boot Application" /B java -jar spring-ftl.jar --server.port=8081

echo Waiting 20 seconds for application to start...
timeout /t 20 /nobreak >nul

echo.
echo ========================================
echo   Application Started Successfully!
echo ========================================
echo.
echo Application URL: http://localhost:8081
echo.
echo To stop the application:
echo 1. Close the Spring Boot window that opened
echo 2. Or press Ctrl+C in the Spring Boot window
echo 3. Or use Task Manager to end java.exe process
echo.

REM Run XML generator if it exists
if exist "xml-generator.exe" (
    echo Running XML generator...
    xml-generator.exe
    echo.
    echo Process completed!
) else (
    echo xml-generator.exe not found, skipping XML generation...
)

echo.
echo All processes completed!
pause
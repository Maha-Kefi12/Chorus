@echo off
REM Robust Spring Boot Server Only Script

REM Ensure we are in the script's directory
cd /d %~dp0

echo ========================================
echo Spring Boot Server Only
echo ========================================
echo.

REM Check if Java is available
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 17 or later and try again
    pause
    exit /b 1
)

REM Check if the JAR file exists
if exist "spring-ftl.jar" (
    set JAR_FILE=spring-ftl.jar
) else (
    REM Try to find any JAR file
    for %%f in (spring-ftl-*.jar) do set JAR_FILE=%%f
    if not defined JAR_FILE (
        echo ERROR: No JAR file found in current directory
        echo Please make sure you're running this from the correct directory
        echo.
        echo Available files in current directory:
        dir *.jar /b 2>nul
        echo.
        pause
        exit /b 1
    )
)

echo Starting Spring Boot application...
echo JAR file: %JAR_FILE%
echo This will start a web server on http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Spring Boot application
java -jar %JAR_FILE%

echo.
echo ========================================
echo Spring Boot application has stopped.
echo ========================================
echo.

REM Print available endpoints
echo Available API endpoints:
echo   - GET  http://localhost:8080/api/analyze
echo   - GET  http://localhost:8080/api/extract-function?path=yourfile.java
echo   - GET  http://localhost:8080/api/extract-function-name?path=yourfile.java
echo   - POST http://localhost:8080/api/parser/fromCode
echo   - POST http://localhost:8080/transform/updateFieldOrder
echo   - POST http://localhost:8080/transform/save-transformation
echo.
echo You can test these endpoints using the httpRequests/*.http files or with curl.
echo.
echo Spring Boot application has stopped. Press any key to exit...
pause >nul 
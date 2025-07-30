@echo off

echo Checking Java installation...
java -version
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting Spring Boot application on port 8081...
start "SpringBoot" java -jar spring-ftl.jar --server.port=8081

echo Waiting 20 seconds for application to start...
timeout /t 20 /nobreak

echo.
echo Spring Boot application should now be running at: http://localhost:8081
echo.
pause
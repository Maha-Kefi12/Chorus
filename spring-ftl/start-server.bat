@echo off
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
echo Spring Boot application has stopped. Press any key to exit...
pause >nul 
@echo off
echo ========================================
echo Spring Boot Server + XML Generator (Separate Process)
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

REM Check if XML generator exists
if not exist "xml-generator.exe" (
    echo ERROR: xml-generator.exe not found in current directory
    echo Please make sure you're running this from the correct directory
    pause
    exit /b 1
)

echo Starting Spring Boot application first...
echo JAR file: %JAR_FILE%
echo This will start a web server on http://localhost:8080
echo.
echo IMPORTANT: When you're ready to generate XML files:
echo 1. Press Ctrl+C to stop the Spring Boot server
echo 2. Wait for the server to fully stop
echo 3. The XML generator will then start automatically
echo.

REM Start the Spring Boot application
java -jar %JAR_FILE%

REM Check if the server stopped properly
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Spring Boot application stopped with error code: %errorlevel%
    echo This might be normal if you pressed Ctrl+C
)

echo.
echo ========================================
echo Spring Boot server has stopped
echo ========================================
echo.
echo Waiting 5 seconds before starting XML generation...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Starting XML Generator in separate process...
echo ========================================
echo.

echo Starting XML Generator application...
echo This will generate XML files in the .idea/demo directory...
echo.

REM Wait a moment to ensure any remaining processes are cleared
timeout /t 3 /nobreak >nul

REM Start the XML generator in a separate process
start /wait xml-generator.exe

REM Check if the application completed successfully
if %errorlevel% equ 0 (
    echo.
    echo ✅ XML generation completed successfully!
    echo 📄 Check the .idea/demo directory for generated XML files
) else (
    echo.
    echo ❌ XML generation failed with error code: %errorlevel%
    echo.
    echo Troubleshooting tips:
    echo - Make sure all Python scripts are in the same directory
    echo - Check that you have write permissions to the .idea/demo directory
    echo - Try running start-debug.bat for more detailed error information
    echo - Try running the XML generator manually to see specific errors
)

echo.
echo Press any key to exit...
pause >nul 
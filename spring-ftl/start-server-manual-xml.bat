@echo off
echo ========================================
echo Spring Boot Server (Manual XML Generation)
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
echo Press Ctrl+C to stop the server when you're done
echo.

REM Start the Spring Boot application
java -jar %JAR_FILE%

echo.
echo ========================================
echo Spring Boot server has stopped
echo ========================================
echo.

REM Check if XML generator exists
if exist "xml-generator.exe" (
    echo XML Generator is available.
    echo.
    set /p run_xml="Do you want to run XML generation now? (y/n): "
    
    if /i "%run_xml%"=="y" (
        echo.
        echo ========================================
        echo Starting XML Generator...
        echo ========================================
        echo.
        
        echo Starting XML Generator application...
        echo This will generate XML files in the .idea/demo directory...
        echo.
        
        REM Wait a moment to ensure any remaining processes are cleared
        timeout /t 3 /nobreak >nul
        
        REM Start the XML generator
        xml-generator.exe
        
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
        )
    ) else (
        echo.
        echo XML generation skipped.
        echo You can run it manually by double-clicking start-xml.bat
    )
) else (
    echo.
    echo XML Generator not found in current directory.
    echo You can run it manually if needed.
)

echo.
echo Press any key to exit...
pause >nul 
@echo off
echo ========================================
echo Real-Time Spring FTL Workflow
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

REM Check if Python is available for HTTP integration
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Python not found, will use curl commands only
    set USE_PYTHON=0
) else (
    echo ✅ Python found, will use HTTP integration script
    set USE_PYTHON=1
)

echo Starting Spring Boot application...
echo JAR file: %JAR_FILE%
echo This will start a web server on http://localhost:8080
echo.

REM Start Spring Boot in background
echo Starting Spring Boot server in background...
start /B java -jar %JAR_FILE%

REM Wait for server to start
echo Waiting for Spring Boot server to start...
timeout /t 15 /nobreak >nul

REM Test if server is running
echo Testing server connection...
curl -s http://localhost:8080/api/analyze >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Server might not be fully started yet, continuing anyway...
) else (
    echo ✅ Server is running and responding
)

echo.
echo ========================================
echo Phase 1: Initial Data Collection
echo ========================================
echo.

REM Create output directories
if not exist "output" mkdir output
if not exist "output\demo" mkdir output\demo
if not exist "output\demo\aini" mkdir output\demo\aini

echo 📁 Created output directories

REM Use Python script if available, otherwise use curl
if %USE_PYTHON% equ 1 (
    echo 🔍 Using Python HTTP integration script...
    python http_data_integration.py
) else (
    echo 🔍 Using curl commands for data collection...
    
    REM Test GET endpoints and save responses
    echo Testing GET endpoints...
    curl -s -o output\analyze_response.json http://localhost:8080/api/analyze
    curl -s -o output\extract_function_response.json "http://localhost:8080/api/extract-function?path=test.java"
    curl -s -o output\extract_function_name_response.json "http://localhost:8080/api/extract-function-name?path=test.java"
    
    REM Test POST endpoints and save responses
    echo Testing POST endpoints...
    curl -s -X POST -H "Content-Type: text/plain" -d "public class Test { }" -o output\parser_fromcode_response.json http://localhost:8080/api/parser/fromCode
    curl -s -X POST -H "Content-Type: application/json" -d "{\"fields\": [\"field1\", \"field2\"]}" -o output\update_field_order_response.json http://localhost:8080/transform/updateFieldOrder
    curl -s -X POST -H "Content-Type: application/json" -d "{\"transformation\": \"test\"}" -o output\save_transformation_response.json http://localhost:8080/transform/save-transformation
    
    echo ✅ Initial data collection completed
)

echo.
echo ========================================
echo Phase 2: Real-Time XML Generation
echo ========================================
echo.

echo 🎯 Starting XML generation while server is running...
echo This will use the collected data to generate XML files
echo.

REM Start XML generation
echo Starting XML generator...
xml-generator.exe

REM Check if XML generation completed
if %errorlevel% equ 0 (
    echo ✅ XML generation completed successfully!
    echo 📄 Check the .idea/demo directory for generated XML files
) else (
    echo ❌ XML generation failed with error code: %errorlevel%
)

echo.
echo ========================================
echo Phase 3: Continuous Data Monitoring
echo ========================================
echo.

echo 🔄 Setting up continuous data monitoring...
echo The server will continue running and collecting data
echo.

REM Create a monitoring script
echo @echo off > monitor_data.bat
echo echo Monitoring Spring Boot server data... >> monitor_data.bat
echo :loop >> monitor_data.bat
echo curl -s -o output\latest_analyze.json http://localhost:8080/api/analyze >> monitor_data.bat
echo timeout /t 30 /nobreak ^>nul >> monitor_data.bat
echo goto loop >> monitor_data.bat

echo 📊 Created monitoring script: monitor_data.bat
echo This script will continuously collect data every 30 seconds
echo.

echo ========================================
echo Workflow Summary
echo ========================================
echo.
echo 🚀 Spring Boot server is running on http://localhost:8080
echo 📁 Data files saved in: output\
echo 📄 XML files generated in: .idea/demo\
echo 🔄 Continuous monitoring: monitor_data.bat
echo.
echo 📊 Available endpoints:
echo   - GET /api/analyze
echo   - GET /api/extract-function
echo   - GET /api/extract-function-name
echo   - POST /api/parser/fromCode
echo   - POST /transform/updateFieldOrder
echo   - POST /transform/save-transformation
echo.
echo 💡 Tips:
echo   - The server will continue running in the background
echo   - Use monitor_data.bat to continuously collect data
echo   - Press Ctrl+C in the server window to stop it when done
echo   - All data is saved in the output directory
echo.

echo Press any key to exit this workflow (server will continue running)...
pause >nul 
@echo off
echo ========================================
echo Complete Spring FTL Workflow
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

echo Starting Spring Boot application...
echo JAR file: %JAR_FILE%
echo This will start a web server on http://localhost:8080
echo.

REM Start Spring Boot in background
echo Starting Spring Boot server in background...
start /B java -jar %JAR_FILE%

REM Wait for server to start
echo Waiting for Spring Boot server to start...
timeout /t 10 /nobreak >nul

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
echo Phase 1: Getting Data via HTTP Endpoints
echo ========================================
echo.

REM Create output directories
if not exist "output" mkdir output
if not exist "output\demo" mkdir output\demo
if not exist "output\demo\aini" mkdir output\demo\aini

echo 📁 Created output directories

REM Step 1: Test GET endpoints and save responses
echo.
echo 🔍 Testing GET endpoints and saving responses...

REM Test /api/analyze endpoint
echo Testing /api/analyze endpoint...
curl -s -o output\analyze_response.json http://localhost:8080/api/analyze
if %errorlevel% equ 0 (
    echo ✅ Saved analyze response to output\analyze_response.json
) else (
    echo ❌ Failed to get analyze response
)

REM Test /api/extract-function endpoint
echo Testing /api/extract-function endpoint...
curl -s -o output\extract_function_response.json "http://localhost:8080/api/extract-function?path=test.java"
if %errorlevel% equ 0 (
    echo ✅ Saved extract-function response to output\extract_function_response.json
) else (
    echo ❌ Failed to get extract-function response
)

REM Test /api/extract-function-name endpoint
echo Testing /api/extract-function-name endpoint...
curl -s -o output\extract_function_name_response.json "http://localhost:8080/api/extract-function-name?path=test.java"
if %errorlevel% equ 0 (
    echo ✅ Saved extract-function-name response to output\extract_function_name_response.json
) else (
    echo ❌ Failed to get extract-function-name response
)

REM Step 2: Test POST endpoints and save responses
echo.
echo 📤 Testing POST endpoints and saving responses...

REM Test /api/parser/fromCode endpoint
echo Testing /api/parser/fromCode endpoint...
curl -s -X POST -H "Content-Type: text/plain" -d "public class Test { }" -o output\parser_fromcode_response.json http://localhost:8080/api/parser/fromCode
if %errorlevel% equ 0 (
    echo ✅ Saved parser fromCode response to output\parser_fromcode_response.json
) else (
    echo ❌ Failed to get parser fromCode response
)

REM Test /transform/updateFieldOrder endpoint
echo Testing /transform/updateFieldOrder endpoint...
curl -s -X POST -H "Content-Type: application/json" -d "{\"fields\": [\"field1\", \"field2\"]}" -o output\update_field_order_response.json http://localhost:8080/transform/updateFieldOrder
if %errorlevel% equ 0 (
    echo ✅ Saved updateFieldOrder response to output\update_field_order_response.json
) else (
    echo ❌ Failed to get updateFieldOrder response
)

REM Test /transform/save-transformation endpoint
echo Testing /transform/save-transformation endpoint...
curl -s -X POST -H "Content-Type: application/json" -d "{\"transformation\": \"test\"}" -o output\save_transformation_response.json http://localhost:8080/transform/save-transformation
if %errorlevel% equ 0 (
    echo ✅ Saved save-transformation response to output\save_transformation_response.json
) else (
    echo ❌ Failed to get save-transformation response
)

echo.
echo ========================================
echo Phase 2: Generating XML Files
echo ========================================
echo.

echo 🎯 Starting XML generation while server is running...
echo This will use the data from HTTP endpoints to generate XML files
echo.

REM Start XML generation in background
echo Starting XML generator in background...
start /wait xml-generator.exe

REM Check if XML generation completed
if %errorlevel% equ 0 (
    echo ✅ XML generation completed successfully!
    echo 📄 Check the .idea/demo directory for generated XML files
) else (
    echo ❌ XML generation failed with error code: %errorlevel%
)

echo.
echo ========================================
echo Phase 3: Final Data Collection
echo ========================================
echo.

REM Get final data from server
echo Getting final data from server...

REM Test all endpoints one more time to ensure we have latest data
curl -s -o output\final_analyze_response.json http://localhost:8080/api/analyze
curl -s -o output\final_extract_function_response.json "http://localhost:8080/api/extract-function?path=test.java"
curl -s -X POST -H "Content-Type: text/plain" -d "public class FinalTest { }" -o output\final_parser_response.json http://localhost:8080/api/parser/fromCode

echo ✅ Final data collection completed

echo.
echo ========================================
echo Workflow Summary
echo ========================================
echo.
echo 📊 HTTP Endpoints tested:
echo   - GET /api/analyze
echo   - GET /api/extract-function
echo   - GET /api/extract-function-name
echo   - POST /api/parser/fromCode
echo   - POST /transform/updateFieldOrder
echo   - POST /transform/save-transformation
echo.
echo 📁 Output files created:
echo   - output\analyze_response.json
echo   - output\extract_function_response.json
echo   - output\extract_function_name_response.json
echo   - output\parser_fromcode_response.json
echo   - output\update_field_order_response.json
echo   - output\save_transformation_response.json
echo   - output\final_*.json (latest data)
echo.
echo 📄 XML files generated in .idea/demo directory
echo.
echo 🚀 Spring Boot server is still running on http://localhost:8080
echo Press Ctrl+C in the server window to stop it when done
echo.

echo Press any key to exit this workflow (server will continue running)...
pause >nul 
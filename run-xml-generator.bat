@echo off
REM XML Generator Workflow Script for Windows
REM Combines Java Spring Boot application with Python XML generation scripts
REM Author: AI Assistant
REM Version: 1.0

setlocal enabledelayedexpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "SPRING_JAR=%SCRIPT_DIR%spring-ftl\target\spring-ftl-0.0.1-SNAPSHOT.jar"
set "SPRING_PORT=8080"
set "SPRING_PID_FILE=%SCRIPT_DIR%spring.pid"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "SPRING_LOG=%LOG_DIR%\spring.log"
set "PYTHON_LOG=%LOG_DIR%\python.log"
set "OUTPUT_DIR=%SCRIPT_DIR%output"
set "PYTHON_SCRIPTS_DIR=%SCRIPT_DIR%spring-ftl\src\main\resources\scripts"

REM Create necessary directories
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo [%date% %time%] Starting XML Generator Workflow...
echo Script directory: %SCRIPT_DIR%

REM Check Java
java -version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Java is not installed or not in PATH
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH
        exit /b 1
    ) else (
        set "PYTHON_CMD=python3"
    )
) else (
    set "PYTHON_CMD=python"
)

REM Check Spring JAR
if not exist "%SPRING_JAR%" (
    echo [ERROR] Spring Boot JAR not found at: %SPRING_JAR%
    echo Building Spring Boot application...
    cd /d "%SCRIPT_DIR%spring-ftl"
    call mvnw.cmd clean package -DskipTests
    cd /d "%SCRIPT_DIR%"
    
    if not exist "%SPRING_JAR%" (
        echo [ERROR] Failed to build Spring Boot JAR
        exit /b 1
    )
)

REM Check Python scripts directory
if not exist "%PYTHON_SCRIPTS_DIR%" (
    echo [ERROR] Python scripts directory not found: %PYTHON_SCRIPTS_DIR%
    exit /b 1
)

echo [SUCCESS] All prerequisites checked successfully

REM Kill any existing Spring Boot processes
taskkill /f /im java.exe /fi "WINDOWTITLE eq spring-ftl*" >nul 2>&1

REM Start Spring Boot application
echo Starting Spring Boot application...
start /b java -jar "%SPRING_JAR%" > "%SPRING_LOG%" 2>&1

REM Wait for Spring Boot to start
echo Waiting for Spring Boot to be ready...
set /a counter=0
:wait_loop
set /a counter+=1
if %counter% gtr 30 (
    echo [ERROR] Spring Boot application failed to start within 60 seconds
    exit /b 1
)

REM Try to connect to Spring Boot
curl -f -s "http://localhost:%SPRING_PORT%" >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_loop
)

echo [SUCCESS] Spring Boot application is ready!

REM Run Python scripts
echo Running Python XML generation scripts...
cd /d "%PYTHON_SCRIPTS_DIR%"

if exist "main.py" (
    echo Running main.py orchestrator...
    %PYTHON_CMD% main.py >> "%PYTHON_LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] Python scripts execution failed. Check logs: %PYTHON_LOG%
        goto cleanup
    )
    echo [SUCCESS] Python scripts executed successfully
) else (
    echo Running individual Python scripts...
    for %%s in (combined.py mapping.py lov_impl_.py screenfinal.py) do (
        if exist "%%s" (
            echo Running %%s...
            %PYTHON_CMD% "%%s" >> "%PYTHON_LOG%" 2>&1
            if errorlevel 1 (
                echo [ERROR] Failed to run %%s
                goto cleanup
            )
        ) else (
            echo [WARNING] Script %%s not found, skipping...
        )
    )
    echo [SUCCESS] All available Python scripts executed
)

cd /d "%SCRIPT_DIR%"

REM Generate HTTP test files
echo Generating HTTP test files...
if exist "%SCRIPT_DIR%spring-ftl\generate_http_tests.py" (
    cd /d "%SCRIPT_DIR%spring-ftl"
    %PYTHON_CMD% generate_http_tests.py >> "%PYTHON_LOG%" 2>&1
    cd /d "%SCRIPT_DIR%"
    echo [SUCCESS] HTTP test files generated
) else (
    echo [WARNING] HTTP test generator not found, skipping...
)

REM Collect output files
echo Collecting generated files...

REM Copy XML files from .idea/demo
if exist ".idea\demo" (
    for /r ".idea\demo" %%f in (*.xml) do copy "%%f" "%OUTPUT_DIR%\" >nul 2>&1
)

REM Copy HTTP test files
if exist "httpRequests" (
    xcopy "httpRequests" "%OUTPUT_DIR%\httpRequests\" /e /i /y >nul 2>&1
)

REM Copy JSON output files
for /r . %%f in (*.json) do (
    echo %%f | findstr /c:"output" >nul && copy "%%f" "%OUTPUT_DIR%\" >nul 2>&1
)

REM List generated files
dir "%OUTPUT_DIR%" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] No output files found
) else (
    echo [SUCCESS] Generated files collected in: %OUTPUT_DIR%
    echo Generated files:
    dir "%OUTPUT_DIR%"
)

REM Git operations if requested
if "%1"=="--git" (
    echo Performing Git operations...
    git rev-parse --git-dir >nul 2>&1
    if not errorlevel 1 (
        echo Pulling latest changes...
        git pull origin main || git pull origin master
        
        git add "%OUTPUT_DIR%" >nul 2>&1
        git add "httpRequests" >nul 2>&1
        git add ".idea\demo" >nul 2>&1
        
        git diff --cached --quiet >nul 2>&1
        if errorlevel 1 (
            echo Committing generated files...
            git commit -m "Auto-generated XML files and HTTP tests - %date% %time%"
            
            echo Pushing changes...
            git push origin main || git push origin master
            echo [SUCCESS] Git operations completed
        ) else (
            echo No changes to commit
        )
    ) else (
        echo [WARNING] Not a git repository, skipping git operations
    )
)

echo [SUCCESS] XML Generator Workflow completed successfully!
goto end

:cleanup
echo Cleaning up...
taskkill /f /im java.exe /fi "WINDOWTITLE eq spring-ftl*" >nul 2>&1
if exist "%SPRING_PID_FILE%" del "%SPRING_PID_FILE%"

:end
REM Cleanup Spring Boot process
taskkill /f /im java.exe /fi "WINDOWTITLE eq spring-ftl*" >nul 2>&1

endlocal
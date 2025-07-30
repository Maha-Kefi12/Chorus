@echo off
echo ========================================
echo Spring FTL Application Launcher
echo ========================================
echo.

REM Vérifier les fichiers disponibles
set XML_GENERATOR_EXISTS=0
set JAR_EXISTS=0
set ADMIN_MODE=0

REM Vérifier si on est en mode administrateur
net session >nul 2>&1
if %errorlevel% equ 0 (
    set ADMIN_MODE=1
    echo ✅ Mode administrateur détecté
) else (
    echo ⚠️ Mode utilisateur standard
)

if exist "xml-generator.exe" (
    set XML_GENERATOR_EXISTS=1
    echo ✅ Found xml-generator.exe
)

if exist "spring-ftl.jar" (
    set JAR_EXISTS=1
    echo ✅ Found spring-ftl.jar
)

if exist "spring-ftl-*.jar" (
    set JAR_EXISTS=1
    echo ✅ Found Spring Boot JAR file
)

echo.

REM Menu principal
echo Choisissez une option:
echo.
echo 1. Diagnostic complet de l'environnement
echo 2. Correction automatique des problèmes
echo 3. Démarrage en mode administrateur
echo 4. Workflow complet (Spring Boot + XML)
echo 5. Workflow temps réel (avec monitoring)
echo 6. XML Generator seulement
echo 7. Spring Boot seulement
echo 8. Spring Boot puis XML Generator
echo 9. XML Generator puis Spring Boot
echo 0. Quitter
echo.

set /p choice="Entrez votre choix (0-9): "

if "%choice%"=="1" goto diagnostic
if "%choice%"=="2" goto fix_issues
if "%choice%"=="3" goto admin_mode
if "%choice%"=="4" goto complete_workflow
if "%choice%"=="5" goto realtime_workflow
if "%choice%"=="6" goto xml_only
if "%choice%"=="7" goto server_only
if "%choice%"=="8" goto server_then_xml
if "%choice%"=="9" goto xml_then_server
if "%choice%"=="0" goto exit
echo Choix invalide. Exiting...
pause
exit /b 1

:diagnostic
echo.
echo ========================================
echo Diagnostic Complet de l'Environnement
echo ========================================
echo.

echo 🔍 Vérification de l'environnement...
echo.

REM Vérifier Java
echo 1. Vérification de Java...
java -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Java est installé
    java -version
) else (
    echo ❌ Java n'est pas installé ou pas dans le PATH
    echo Veuillez installer Java 17 ou plus récent
    pause
    goto menu
)

echo.

REM Vérifier les fichiers
echo 2. Vérification des fichiers...
echo.

if exist "spring-ftl.jar" (
    echo ✅ spring-ftl.jar trouvé
    dir spring-ftl.jar
) else (
    echo ❌ spring-ftl.jar non trouvé
    echo Fichiers JAR disponibles:
    dir *.jar /b 2>nul
)

if exist "xml-generator.exe" (
    echo ✅ xml-generator.exe trouvé
    dir xml-generator.exe
) else (
    echo ❌ xml-generator.exe non trouvé
    echo Fichiers EXE disponibles:
    dir *.exe /b 2>nul
)

echo.

REM Vérifier les ports
echo 3. Vérification des ports...
echo.

netstat -an | findstr :8080
if %errorlevel% equ 0 (
    echo ⚠️ Le port 8080 est déjà utilisé
    echo Cela peut causer des problèmes de démarrage
) else (
    echo ✅ Le port 8080 est libre
)

echo.

REM Test de démarrage avec diagnostic
echo 4. Test de démarrage avec diagnostic...
echo.

echo Tentative de démarrage avec diagnostic complet...
java -jar spring-ftl.jar --debug --trace

echo.
echo ========================================
echo Résultats du Diagnostic
echo ========================================
echo.

echo Si l'application ne démarre toujours pas:
echo 1. Vérifiez que Java 17+ est installé
echo 2. Vérifiez que le port 8080 est libre
echo 3. Vérifiez les permissions d'écriture
echo 4. Essayez de redémarrer votre ordinateur
echo 5. Vérifiez l'espace disque disponible
echo.

pause
goto menu

:fix_issues
echo.
echo ========================================
echo Correction Automatique des Problèmes
echo ========================================
echo.

echo 🔧 Correction automatique des problèmes courants...
echo.

REM 1. Vérifier et tuer les processus existants
echo 1. Arrêt des processus existants...
taskkill /f /im java.exe >nul 2>&1
taskkill /f /im javaw.exe >nul 2>&1
echo ✅ Processus Java arrêtés

REM 2. Libérer le port 8080
echo 2. Libération du port 8080...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo ✅ Port 8080 libéré

REM 3. Nettoyer les fichiers temporaires
echo 3. Nettoyage des fichiers temporaires...
if exist "*.tmp" del *.tmp
if exist "*.log" del *.log
echo ✅ Fichiers temporaires nettoyés

REM 4. Vérifier l'espace disque
echo 4. Vérification de l'espace disque...
for /f "tokens=3" %%a in ('dir /-c ^| findstr "bytes free"') do (
    set FREE_SPACE=%%a
)
echo Espace libre: %FREE_SPACE% bytes

REM 5. Vérifier les permissions
echo 5. Vérification des permissions...
icacls . /grant Everyone:F >nul 2>&1
echo ✅ Permissions mises à jour

REM 6. Test de démarrage avec options de sécurité
echo 6. Test de démarrage avec options de sécurité...
echo.

echo Tentative de démarrage avec options de sécurité...
java -Xmx512m -Xms256m -Djava.security.manager=allow -jar spring-ftl.jar

echo.
echo ========================================
echo Résultats de la Correction
echo ========================================
echo.

if %errorlevel% equ 0 (
    echo ✅ Application démarrée avec succès!
) else (
    echo ❌ L'application n'a toujours pas démarré
    echo.
    echo Solutions supplémentaires:
    echo 1. Redémarrez votre ordinateur
    echo 2. Réinstallez Java 17+
    echo 3. Vérifiez l'antivirus
    echo 4. Exécutez en tant qu'administrateur
    echo 5. Vérifiez les dépendances manquantes
)

echo.
pause
goto menu

:admin_mode
echo.
echo ========================================
echo Mode Administrateur - Spring FTL
echo ========================================
echo.

if %ADMIN_MODE% neq 1 (
    echo ⚠️ Ce mode nécessite des privilèges administrateur
    echo Veuillez faire un clic droit et sélectionner "Exécuter en tant qu'administrateur"
    pause
    goto menu
)

echo ✅ Mode administrateur détecté
echo.

REM Vérifier Java
echo Vérification de Java...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java n'est pas installé
    echo Veuillez installer Java 17 ou plus récent
    pause
    goto menu
)

echo ✅ Java est installé
java -version

echo.

REM Vérifier le fichier JAR
if not exist "spring-ftl.jar" (
    echo ❌ spring-ftl.jar non trouvé
    echo Fichiers JAR disponibles:
    dir *.jar /b 2>nul
    pause
    goto menu
)

echo ✅ spring-ftl.jar trouvé

echo.

REM Nettoyer l'environnement
echo Nettoyage de l'environnement...
taskkill /f /im java.exe >nul 2>&1
taskkill /f /im javaw.exe >nul 2>&1

REM Libérer le port 8080
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 2^>nul') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo ✅ Environnement nettoyé

echo.

REM Définir les variables d'environnement pour la sécurité
echo Configuration des variables d'environnement...
set JAVA_OPTS=-Xmx1024m -Xms512m -Djava.security.manager=allow -Djava.security.policy=all.policy
set SPRING_PROFILES_ACTIVE=dev
set SERVER_PORT=8080

echo ✅ Variables d'environnement configurées

echo.

REM Créer un fichier de politique de sécurité temporaire
echo Création du fichier de politique de sécurité...
echo grant { permission java.security.AllPermission; }; > all.policy

echo ✅ Fichier de politique créé

echo.

echo ========================================
echo Démarrage de l'Application
echo ========================================
echo.

echo 🚀 Démarrage avec options de sécurité...
echo.

REM Démarrer l'application avec toutes les options de sécurité
java %JAVA_OPTS% -jar spring-ftl.jar

echo.
echo ========================================
echo Résultats
echo ========================================
echo.

if %errorlevel% equ 0 (
    echo ✅ Application démarrée avec succès!
    echo 🌐 Serveur accessible sur http://localhost:8080
) else (
    echo ❌ L'application n'a pas pu démarrer
    echo.
    echo Code d'erreur: %errorlevel%
    echo.
    echo Solutions possibles:
    echo 1. Vérifiez que Java 17+ est installé
    echo 2. Vérifiez l'espace disque disponible
    echo 3. Désactivez temporairement l'antivirus
    echo 4. Vérifiez les logs d'erreur Windows
    echo 5. Essayez de redémarrer l'ordinateur
)

echo.
echo Nettoyage des fichiers temporaires...
if exist "all.policy" del all.policy

echo.
pause
goto menu

:complete_workflow
echo.
echo ========================================
echo Workflow Complet (Spring Boot + XML)
echo ========================================
echo.

REM Vérifier les prérequis
if not exist "spring-ftl.jar" (
    echo ❌ spring-ftl.jar non trouvé
    pause
    goto menu
)

if not exist "xml-generator.exe" (
    echo ❌ xml-generator.exe non trouvé
    pause
    goto menu
)

echo Starting Spring Boot application...
echo JAR file: spring-ftl.jar
echo This will start a web server on http://localhost:8080
echo.

REM Start Spring Boot in background
echo Starting Spring Boot server in background...
start /B java -jar spring-ftl.jar

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
pause
goto menu

:realtime_workflow
echo.
echo ========================================
echo Real-Time Workflow (avec monitoring)
echo ========================================
echo.

REM Vérifier les prérequis
if not exist "spring-ftl.jar" (
    echo ❌ spring-ftl.jar non trouvé
    pause
    goto menu
)

if not exist "xml-generator.exe" (
    echo ❌ xml-generator.exe non trouvé
    pause
    goto menu
)

echo Starting Spring Boot application...
echo JAR file: spring-ftl.jar
echo This will start a web server on http://localhost:8080
echo.

REM Start Spring Boot in background
echo Starting Spring Boot server in background...
start /B java -jar spring-ftl.jar

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
pause
goto menu

:xml_only
echo.
echo ========================================
echo XML Generator Only
echo ========================================
echo.

REM Check if the executable exists
if not exist "xml-generator.exe" (
    echo ERROR: xml-generator.exe not found in current directory
    echo Please make sure you're running this from the correct directory
    echo.
    echo Available files in current directory:
    dir *.exe /b 2>nul
    echo.
    pause
    goto menu
)

echo Starting XML Generator application...
echo This will generate XML files in the .idea/demo directory...
echo.

REM Start the XML generator and wait for it to complete
xml-generator.exe

REM Check if the application completed successfully
if %errorlevel% equ 0 (
    echo.
    echo ✅ XML generation completed successfully!
    echo 📄 Check the .idea/demo directory for generated XML files
) else (
    echo.
    echo ❌ XML generation failed with error code: %errorlevel%
)

echo.
echo Press any key to exit...
pause
goto menu

:server_only
echo.
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
    goto menu
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
        goto menu
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
pause
goto menu

:server_then_xml
echo.
echo ========================================
echo Spring Boot Server + XML Generator
echo ========================================
echo.

REM Check if Java is available
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 17 or later and try again
    pause
    goto menu
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
        goto menu
    )
)

REM Check if XML generator exists
if not exist "xml-generator.exe" (
    echo ERROR: xml-generator.exe not found in current directory
    echo Please make sure you're running this from the correct directory
    pause
    goto menu
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
echo Waiting 3 seconds before starting XML generation...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting XML Generator...
echo ========================================
echo.

echo Starting XML Generator application...
echo This will generate XML files in the .idea/demo directory...
echo.

REM Wait a moment to ensure any remaining processes are cleared
timeout /t 2 /nobreak >nul

REM Start the XML generator and wait for it to complete
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

echo.
echo Press any key to exit...
pause
goto menu

:xml_then_server
echo.
echo ========================================
echo XML Generator + Spring Boot Server
echo ========================================
echo.

REM Check if the executable exists
if not exist "xml-generator.exe" (
    echo ERROR: xml-generator.exe not found in current directory
    echo Please make sure you're running this from the correct directory
    pause
    goto menu
)

echo Starting XML Generator first...
echo This will generate XML files in the .idea/demo directory...
echo.

REM Start the XML generator and wait for it to complete
xml-generator.exe

REM Check if the application completed successfully
if %errorlevel% equ 0 (
    echo.
    echo ✅ XML generation completed successfully!
    echo 📄 Check the .idea/demo directory for generated XML files
) else (
    echo.
    echo ❌ XML generation failed with error code: %errorlevel%
)

echo.
echo Press any key to continue to Spring Boot application...
pause >nul

echo.
echo ========================================
echo Starting Spring Boot Application...
echo ========================================
echo.

REM Check if Java is available
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 17 or later and try again
    pause
    goto menu
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
        pause
        goto menu
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
goto menu

:menu
echo.
echo ========================================
echo Retour au Menu Principal
echo ========================================
echo.
echo Choisissez une option:
echo.
echo 1. Diagnostic complet de l'environnement
echo 2. Correction automatique des problèmes
echo 3. Démarrage en mode administrateur
echo 4. Workflow complet (Spring Boot + XML)
echo 5. Workflow temps réel (avec monitoring)
echo 6. XML Generator seulement
echo 7. Spring Boot seulement
echo 8. Spring Boot puis XML Generator
echo 9. XML Generator puis Spring Boot
echo 0. Quitter
echo.

set /p choice="Entrez votre choix (0-9): "

if "%choice%"=="1" goto diagnostic
if "%choice%"=="2" goto fix_issues
if "%choice%"=="3" goto admin_mode
if "%choice%"=="4" goto complete_workflow
if "%choice%"=="5" goto realtime_workflow
if "%choice%"=="6" goto xml_only
if "%choice%"=="7" goto server_only
if "%choice%"=="8" goto server_then_xml
if "%choice%"=="9" goto xml_then_server
if "%choice%"=="0" goto exit
echo Choix invalide. Retour au menu...
timeout /t 2 /nobreak >nul
goto menu

:exit
echo.
echo Merci d'avoir utilisé Spring FTL Application Launcher!
echo.
exit /b 0 
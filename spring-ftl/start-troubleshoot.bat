@echo off
echo ========================================
echo Diagnostic de l'Application Spring FTL
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
    exit /b 1
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

echo Press any key to exit...
pause >nul 
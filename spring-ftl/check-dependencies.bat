@echo off
echo ========================================
echo Vérification des Dépendances
echo ========================================
echo.

echo 🔍 Vérification complète des dépendances...
echo.

REM 1. Vérifier Java
echo 1. Vérification de Java...
java -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Java est installé
    java -version
) else (
    echo ❌ Java n'est pas installé
    echo Veuillez installer Java 17 ou plus récent
    echo Téléchargez depuis: https://adoptium.net/
)

echo.

REM 2. Vérifier la version de Java
echo 2. Vérification de la version de Java...
for /f "tokens=3" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do (
    set JAVA_VERSION=%%i
)
echo Version Java détectée: %JAVA_VERSION%
if "%JAVA_VERSION:~1,2%" geq "17" (
    echo ✅ Version Java compatible (17+)
) else (
    echo ❌ Version Java trop ancienne
    echo Veuillez installer Java 17 ou plus récent
)

echo.

REM 3. Vérifier les variables d'environnement
echo 3. Vérification des variables d'environnement...
echo JAVA_HOME: %JAVA_HOME%
echo PATH contient Java: 
echo %PATH% | findstr /i java >nul && echo ✅ Java dans PATH || echo ❌ Java pas dans PATH

echo.

REM 4. Vérifier l'espace disque
echo 4. Vérification de l'espace disque...
for /f "tokens=3" %%a in ('dir /-c ^| findstr "bytes free"') do (
    set FREE_SPACE=%%a
)
echo Espace libre: %FREE_SPACE% bytes
if %FREE_SPACE% gtr 1000000000 (
    echo ✅ Espace disque suffisant
) else (
    echo ❌ Espace disque insuffisant
    echo Libérez de l'espace disque
)

echo.

REM 5. Vérifier les fichiers nécessaires
echo 5. Vérification des fichiers...
if exist "spring-ftl.jar" (
    echo ✅ spring-ftl.jar trouvé
    dir spring-ftl.jar
) else (
    echo ❌ spring-ftl.jar manquant
    echo Fichiers JAR disponibles:
    dir *.jar /b 2>nul
)

if exist "xml-generator.exe" (
    echo ✅ xml-generator.exe trouvé
    dir xml-generator.exe
) else (
    echo ❌ xml-generator.exe manquant
    echo Fichiers EXE disponibles:
    dir *.exe /b 2>nul
)

echo.

REM 6. Vérifier les ports
echo 6. Vérification des ports...
netstat -an | findstr :8080 >nul
if %errorlevel% equ 0 (
    echo ⚠️ Le port 8080 est utilisé
    echo Cela peut causer des problèmes
) else (
    echo ✅ Le port 8080 est libre
)

echo.

REM 7. Vérifier les permissions
echo 7. Vérification des permissions...
icacls . /q | findstr "Everyone" >nul
if %errorlevel% equ 0 (
    echo ✅ Permissions correctes
) else (
    echo ⚠️ Permissions limitées
    echo Essayez d'exécuter en tant qu'administrateur
)

echo.

REM 8. Test de connectivité réseau
echo 8. Test de connectivité réseau...
ping -n 1 127.0.0.1 >nul
if %errorlevel% equ 0 (
    echo ✅ Connectivité locale OK
) else (
    echo ❌ Problème de connectivité locale
)

echo.

echo ========================================
echo Résumé des Vérifications
echo ========================================
echo.

echo Si des problèmes sont détectés:
echo 1. Installez Java 17+ si manquant
echo 2. Libérez de l'espace disque si nécessaire
echo 3. Exécutez en tant qu'administrateur
echo 4. Désactivez temporairement l'antivirus
echo 5. Redémarrez l'ordinateur
echo.

echo Press any key to exit...
pause >nul 
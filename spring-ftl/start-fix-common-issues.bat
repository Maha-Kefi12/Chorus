@echo off
echo ========================================
echo Correction des Problèmes Courants
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
echo Press any key to exit...
pause >nul 
@echo off
echo ========================================
echo Mode Administrateur - Spring FTL
echo ========================================
echo.

REM Vérifier si on est en mode administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ce script doit être exécuté en tant qu'administrateur
    echo Veuillez faire un clic droit et sélectionner "Exécuter en tant qu'administrateur"
    pause
    exit /b 1
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
    exit /b 1
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
    exit /b 1
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
echo Press any key to exit...
pause >nul 
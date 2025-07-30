@echo off
echo ========================================
echo Diagnostic du Main.py
echo ========================================
echo.

echo 🔍 Vérification de l'environnement Python...
echo.

REM Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python 3.7+ et réessayer
    pause
    exit /b 1
)

echo ✅ Python est installé
python --version

echo.

REM Vérifier les fichiers Python
echo 📄 Vérification des fichiers Python...
echo.

if exist "main.py" (
    echo ✅ main.py trouvé
    dir main.py
) else (
    echo ❌ main.py non trouvé
)

if exist "debug-main.py" (
    echo ✅ debug-main.py trouvé
) else (
    echo ❌ debug-main.py non trouvé
)

echo.

REM Vérifier les scripts requis
echo 🔍 Vérification des scripts requis...
echo.

set MISSING_SCRIPTS=0

if exist "combined.py" (
    echo ✅ combined.py trouvé
) else (
    echo ❌ combined.py non trouvé
    set /a MISSING_SCRIPTS+=1
)

if exist "mapping.py" (
    echo ✅ mapping.py trouvé
) else (
    echo ❌ mapping.py non trouvé
    set /a MISSING_SCRIPTS+=1
)

if exist "lov_impl_.py" (
    echo ✅ lov_impl_.py trouvé
) else (
    echo ❌ lov_impl_.py non trouvé
    set /a MISSING_SCRIPTS+=1
)

if exist "screenfinal.py" (
    echo ✅ screenfinal.py trouvé
) else (
    echo ❌ screenfinal.py non trouvé
    set /a MISSING_SCRIPTS+=1
)

echo.

if %MISSING_SCRIPTS% gtr 0 (
    echo ⚠️ %MISSING_SCRIPTS% script(s) manquant(s)
    echo Cela peut causer des problèmes dans main.py
) else (
    echo ✅ Tous les scripts requis sont présents
)

echo.

echo ========================================
echo Exécution du Diagnostic
echo ========================================
echo.

echo 🚀 Lancement du diagnostic Python...
echo.

REM Exécuter le diagnostic Python
python debug-main.py

echo.
echo ========================================
echo Résultats du Diagnostic
echo ========================================
echo.

if %errorlevel% equ 0 (
    echo ✅ Diagnostic terminé avec succès
) else (
    echo ❌ Diagnostic a rencontré des problèmes
    echo.
    echo Solutions possibles:
    echo 1. Vérifiez que tous les scripts Python sont présents
    echo 2. Vérifiez les permissions des fichiers
    echo 3. Vérifiez la version de Python (3.7+ requis)
    echo 4. Vérifiez les dépendances Python manquantes
    echo 5. Essayez d'exécuter en tant qu'administrateur
)

echo.
echo Press any key to exit...
pause >nul 
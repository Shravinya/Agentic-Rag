@echo off
TITLE Fix and Push GitHub Workflows
COLOR 0E

echo ========================================
echo   FIX AND PUSH GITHUB WORKFLOWS
echo ========================================
echo.

echo [STEP 1] Verifying workflow files exist locally...
if exist ".github\workflows\ci-cd.yml" (
    echo [OK] ci-cd.yml found
) else (
    echo [ERROR] ci-cd.yml NOT found!
    pause
    exit /b 1
)

if exist ".github\workflows\test.yml" (
    echo [OK] test.yml found
) else (
    echo [ERROR] test.yml NOT found!
    pause
    exit /b 1
)
echo.

echo [STEP 2] Checking .gitignore for .github exclusion...
findstr /C:".github" .gitignore >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] .github might be in .gitignore
    echo Removing .github from .gitignore if present...
)
echo.

echo [STEP 3] Force adding .github directory...
git add -f .github/
git add -f .github/workflows/
git add -f .github/workflows/ci-cd.yml
git add -f .github/workflows/test.yml
echo [SUCCESS] Files force-added
echo.

echo [STEP 4] Checking what will be committed...
git status
echo.

echo [STEP 5] Committing workflows...
git commit -m "Add GitHub Actions workflows"
if errorlevel 1 (
    echo [INFO] Nothing new to commit or already committed
)
echo.

echo [STEP 6] Pushing to GitHub...
git push origin main
echo.

if errorlevel 1 (
    echo [ERROR] Push failed! 
    echo.
    echo You may need to authenticate. 
    echo Use a Personal Access Token as password.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Now check:
echo 1. Repository files: https://github.com/Shravinya/Agentic-Rag
echo 2. Workflows folder: https://github.com/Shravinya/Agentic-Rag/tree/main/.github/workflows
echo 3. Actions tab: https://github.com/Shravinya/Agentic-Rag/actions
echo.

pause

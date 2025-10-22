@echo off
TITLE Push to GitHub
COLOR 0A

echo ========================================
echo   PUSH TO GITHUB
echo ========================================
echo.

echo [STEP 1] Adding all files...
git add .
git add .github/workflows/ci.yml -f
echo [OK] Files added
echo.

echo [STEP 2] Committing changes...
git commit -m "Add simple CI/CD workflow"
if errorlevel 1 (
    echo [INFO] No new changes to commit
)
echo.

echo [STEP 3] Pushing to GitHub...
git push origin main
echo.

if errorlevel 1 (
    echo [ERROR] Push failed!
    echo Please check your authentication.
    pause
    exit /b 1
)

echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Check your repository:
echo https://github.com/Shravinya/Agentic-Rag
echo.
echo Check CI/CD pipeline:
echo https://github.com/Shravinya/Agentic-Rag/actions
echo.

pause

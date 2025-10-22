@echo off
TITLE Final Push to GitHub
COLOR 0A

echo ========================================
echo   FINAL PUSH TO GITHUB
echo ========================================
echo.

echo [STEP 1] Aborting any ongoing rebase...
git rebase --abort 2>nul
echo [OK] Clean state
echo.

echo [STEP 2] Adding all files including .github...
git add -A
git add .github/ -f
echo [OK] Files added
echo.

echo [STEP 3] Committing all changes...
git commit -m "Complete MLOps implementation with CI/CD workflows"
if errorlevel 1 (
    echo [INFO] No new changes to commit
)
echo.

echo [STEP 4] Force pushing to GitHub...
git push origin main --force
echo.

if errorlevel 1 (
    echo [ERROR] Push failed!
    echo.
    echo Please check:
    echo 1. Your internet connection
    echo 2. GitHub authentication (use Personal Access Token)
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   SUCCESS! EVERYTHING PUSHED!
echo ========================================
echo.
echo Now verify:
echo.
echo 1. Main repository:
echo    https://github.com/Shravinya/Agentic-Rag
echo.
echo 2. Check for .github folder in the file list
echo.
echo 3. Workflows folder:
echo    https://github.com/Shravinya/Agentic-Rag/tree/main/.github/workflows
echo.
echo 4. Actions tab (CI/CD):
echo    https://github.com/Shravinya/Agentic-Rag/actions
echo.
echo 5. Add GROQ_API_KEY secret:
echo    https://github.com/Shravinya/Agentic-Rag/settings/secrets/actions
echo.

pause

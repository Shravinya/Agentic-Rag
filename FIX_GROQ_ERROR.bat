@echo off
TITLE Fix Groq API Error
COLOR 0E

echo ========================================
echo   FIXING GROQ API COMPATIBILITY ERROR
echo ========================================
echo.

echo [STEP 1] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Activated
echo.

echo [STEP 2] Upgrading Groq and httpx libraries...
pip install --upgrade groq httpx
echo.

echo [STEP 3] Verifying installation...
python -c "import groq; print(f'Groq version: {groq.__version__}')"
python -c "import httpx; print(f'httpx version: {httpx.__version__}')"
echo.

echo ========================================
echo   FIX COMPLETE!
echo ========================================
echo.
echo Now run your application:
echo   run.bat
echo.

pause

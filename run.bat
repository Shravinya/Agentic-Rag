@echo off
echo ========================================
echo  AI Bank Form Validator
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run Streamlit app
echo Starting Streamlit application...
streamlit run streamlit_app.py

pause

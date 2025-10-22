@echo off
echo Cleaning up unnecessary files...
echo.

timeout /t 2 /nobreak >nul

REM Delete batch files
if exist "FINAL_PUSH.bat" del /F /Q "FINAL_PUSH.bat" && echo Deleted: FINAL_PUSH.bat
if exist "FIX_AND_PUSH_WORKFLOWS.bat" del /F /Q "FIX_AND_PUSH_WORKFLOWS.bat" && echo Deleted: FIX_AND_PUSH_WORKFLOWS.bat
if exist "systemd_service.txt" del /F /Q "systemd_service.txt" && echo Deleted: systemd_service.txt

echo.
echo Cleanup complete!
echo.
echo Remaining essential files:
echo - streamlit_app.py (Main application)
echo - config.py (Configuration)
echo - requirements.txt (Dependencies)
echo - run.bat (Application launcher)
echo - README.md (Documentation)
echo - Dockerfile (Docker configuration)
echo - docker-compose.yml (Docker compose)
echo - agents/ (AI agents)
echo - rag/ (RAG system)
echo - utils/ (Utilities)
echo - scrapers/ (Policy scrapers)
echo - data/ (Data storage)
echo.

timeout /t 3 /nobreak >nul
del /F /Q "%~f0" 2>nul

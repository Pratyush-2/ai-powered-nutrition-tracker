@echo off
echo Starting FastAPI backend and Flutter frontend...
echo Windows will open showing the service logs.
echo.

REM Start FastAPI backend - make window visible and bring to front
start "FastAPI Backend - API Logs" /MAX cmd /k "cd /d %~dp0 && title FastAPI Backend && echo Activating virtual environment... && .venv\Scripts\activate && echo. && echo Starting FastAPI server on http://127.0.0.1:8000 && echo API logs will appear below: && echo ================================ && uvicorn app.main:app --reload"

REM Small delay before starting Flutter
timeout /t 2 /nobreak > nul

REM Start Flutter frontend - make window visible  
start "Flutter Frontend" /MAX cmd /k "cd /d %~dp0\nutrition_app && title Flutter Frontend && echo Starting Flutter app... && flutter run --hot --fast-start"

echo.
echo Both services started!
echo Look for the new command windows that just opened.
echo - FastAPI window: Shows all API request/response logs
echo - Flutter window: Shows app startup and hot reload logs
echo.
echo Press any key to close this launcher window...
pause > nul

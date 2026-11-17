@echo off
rem Level 1: recompute every table from the saved answers. No models and no GPU needed.
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer is required: https://www.python.org/downloads/
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo [1/5] Checking frozen inputs and coverage...
".venv\Scripts\python.exe" -X utf8 validate_package.py
if errorlevel 1 goto failed
echo [2/5] Recomputing statistics...
".venv\Scripts\python.exe" -X utf8 analyse_main.py
if errorlevel 1 goto failed
echo [3/5] Redrawing figures...
".venv\Scripts\python.exe" -X utf8 make_figures.py
if errorlevel 1 goto failed
echo [4/5] Recomputing manuscript extra table...
".venv\Scripts\python.exe" -X utf8 manuscript_extra_analysis.py
if errorlevel 1 goto failed
echo [5/5] Comparing with recorded hashes...
".venv\Scripts\python.exe" -X utf8 verify_reproduction.py
if errorlevel 1 goto failed
echo.
echo DONE. Fill in REPRODUCTION_REPORT_TEMPLATE.md with what you saw.
pause
exit /b 0
:failed
echo.
echo FAILED: read the message above.
pause
exit /b 1

@echo off
setlocal
cd /d "%~dp0"
set "RMT_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%RMT_PY%" goto run
where py >nul 2>nul
if not errorlevel 1 (set "RMT_PY=py"&goto run)
where python >nul 2>nul
if not errorlevel 1 (set "RMT_PY=python"&goto run)
echo Python 3 is required. Install Python or open this package in the original Codex environment.
pause
exit /b 1
:run
if exist ".venv\Scripts\python.exe" goto dependencies
"%RMT_PY%" -m venv .venv
if errorlevel 1 goto failed
:dependencies
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
:analyse
".venv\Scripts\python.exe" -X utf8 analyse_main.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -X utf8 make_figures.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -X utf8 validate_package.py
if errorlevel 1 goto failed
echo.
echo SUCCESS: saved-data tables, figures and coverage checks completed.
echo This recomputes existing results; it does not generate new model answers.
pause
exit /b 0
:failed
echo.
echo FAILED: read the error above. No successful reproduction is claimed.
pause
exit /b 1

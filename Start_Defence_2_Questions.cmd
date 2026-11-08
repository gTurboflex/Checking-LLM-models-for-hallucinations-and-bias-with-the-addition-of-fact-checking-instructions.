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
"%RMT_PY%" -X utf8 run_experiment.py --mode demo --questions 2
if errorlevel 1 goto end
"%RMT_PY%" -X utf8 analyse_demo.py --latest
:end
echo.
pause

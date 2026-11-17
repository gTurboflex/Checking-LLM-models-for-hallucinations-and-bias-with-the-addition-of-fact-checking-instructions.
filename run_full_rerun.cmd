@echo off
rem Level 3: repeat all 2400 requests into a NEW folder, then compare with the saved run.
rem Takes about 2 hours on an RTX 4070 Laptop GPU. The saved run is never overwritten.
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
echo This sends 2400 requests (4 local + 2 cloud models). Press Ctrl+C to cancel.
pause
%PY% -X utf8 run_experiment.py --mode main
%PY% -X utf8 compare_rerun.py --latest
pause

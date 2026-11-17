@echo off
rem Level 2: one live question x 4 conditions on the local models (a few minutes).
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
%PY% -X utf8 run_experiment.py --mode demo --questions 1 --models qwen3:1.7b qwen3:4b-q4_K_M qwen3:8b gemma4:e2b
if errorlevel 1 goto end
%PY% -X utf8 analyse_demo.py --latest
:end
pause

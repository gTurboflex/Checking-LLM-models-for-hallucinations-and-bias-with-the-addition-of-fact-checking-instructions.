@echo off
rem Level 2 preparation: download the study models with Ollama.
setlocal
cd /d "%~dp0"
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama is not installed. Download it from https://ollama.com/download , start it, then run this again.
  pause
  exit /b 1
)
ollama --version
echo.
echo Downloading the four local models (about 14 GB in total)...
for %%M in (qwen3:1.7b qwen3:4b-q4_K_M qwen3:8b gemma4:e2b) do (
  echo --- %%M
  ollama pull %%M
)
echo.
set /p "CLOUD=Also set up the two cloud models (needs a free ollama.com account)? [y/N] "
if /i not "%CLOUD%"=="y" goto check
ollama signin
ollama pull beam:cloud
ollama pull gemma4:31b-cloud
:check
echo.
where py >nul 2>nul
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer is required: https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% -X utf8 check_ollama_models.py
pause

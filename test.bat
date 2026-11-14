@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once kur.bat calistirilmali.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -q %*
pause

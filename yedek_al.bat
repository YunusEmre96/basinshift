@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once kur.bat calistirilmali.
  pause
  exit /b 1
)
echo Testler calistiriliyor, ardindan cevrimdisi calisan yedek zip hazirlaniyor...
".venv\Scripts\python.exe" scripts\freeze.py %*
pause

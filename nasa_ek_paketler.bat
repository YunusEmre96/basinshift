@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once kur.bat calistirilmali.
  pause
  exit /b 1
)
echo GRACE ve CMIP6 dosyalarini okumak icin ek paketler kuruluyor...
".venv\Scripts\python.exe" -m pip install -r requirements-nasa.txt
pause

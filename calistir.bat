@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once kur.bat calistirilmali.
  pause
  exit /b 1
)
echo Uygulama aciliyor: http://localhost:8501   (kapatmak icin bu pencerede Ctrl+C)
".venv\Scripts\python.exe" -m streamlit run app.py %*
pause

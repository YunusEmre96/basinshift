@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set "PY="
where py >nul 2>nul && py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo [HATA] Python 3.11 veya ustu bulunamadi.
  echo        https://www.python.org/downloads/ adresinden kurun.
  echo        Kurulumda "Add python.exe to PATH" kutusunu isaretleyin, sonra bu dosyayi yeniden calistirin.
  echo.
  pause
  exit /b 1
)
echo === 1/3 Sanal ortam ===
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
if errorlevel 1 goto :fail
echo === 2/3 Paketler (internet gerekir, birkac dakika surebilir) ===
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail
echo === 3/3 Testler ===
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 (
  echo.
  echo [UYARI] Bazi testler gecmedi. Yukaridaki ciktiyi kaydedin.
  pause
  exit /b 1
)
echo.
echo Kurulum tamam. Uygulamayi acmak icin: calistir.bat
echo Gercek NASA verisi icin:           veri_indir.bat
pause
exit /b 0
:fail
echo.
echo [HATA] Kurulum tamamlanamadi. Internet baglantisini kontrol edin ve yeniden deneyin.
pause
exit /b 1

@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once kur.bat calistirilmali.
  pause
  exit /b 1
)
echo Gercek NASA verisi indiriliyor (POWER + SoilGrids; anahtar gerekmez).
echo Earthdata gerektirenler icin: veri_indir.bat --earthdata   (once .env dosyasini doldurun)
echo CMIP6 icin:                   veri_indir.bat --datasets climate_deltas
echo.
".venv\Scripts\python.exe" scripts\setup_real_data.py %*
echo.
echo Rapor: data\veri_raporu.txt
pause

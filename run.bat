@echo off
chcp 65001 >nul
title Kaplumbaga Tanim Sistemi

echo.
echo  ================================================
echo   Kaplumbaga Fotograf Tanim Sistemi baslatiliyor
echo  ================================================
echo.

cd /d "%~dp0"
python -c "import sys; sys.path.insert(0,'src'); from turtle_id.app import main; main()"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [HATA] Uygulama beklenmedik sekilde kapandi.
    echo  Hata kodu: %ERRORLEVEL%
    pause
)

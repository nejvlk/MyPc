@echo off
title MyPC Explorer Monitor
color 2E
cls

:loop
echo 🔍 Kontrola, zda běží explorer.exe...
tasklist | find "explorer.exe" >nul || (
    echo ⚠️ Explorer.exe spadl! Restartuji...
    start explorer.exe
)

timeout /t 5 >nul
goto loop
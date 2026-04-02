@echo off
title MyPC Explorer Protection
color 2E
cls

:loop
echo 🔍 Kontrola, zda běží explorer.exe...
tasklist | find "explorer.exe" >nul || (
    echo ⚠️ Možná hrozba! Explorer.exe byl vypnut – Obnovuji...
    start explorer.exe
)

echo 🛑 Blokování vypnutí systému...
shutdown -a >nul 2>&1

@echo off
title Antivirová kontrola
color 4E
cls

echo 🔍 Hledám škodlivé procesy...

set processes=noescape.exe memz.exe trojan.exe ransomware.exe wannacry.exe conficker.exe mydoom.exe sobig.exe iloveyou.exe stuxnet.exe cryptolocker.exe tinba.exe nimda.exe sqlslammer.exe shlayer.exe welchia.exe morrisworm.exe

for %%p in (%processes%) do (
    tasklist | find /I "%%p" >nul
    if not errorlevel 1 (
        echo ❌ Detekován %%p! Ukončuji...
        taskkill /IM %%p /F
    )
)

echo ✅ Hotovo! Všechny detekované procesy byly ukončeny.

echo 🗑 Mazání nebezpečných souborů na ploše...
set desktop=%USERPROFILE%\Desktop
set badfiles=noescape.exe memz.exe trojan.exe ransomware.exe wannacry.exe conficker.exe mydoom.exe sobig.exe iloveyou.exe stuxnet.exe cryptolocker.exe tinba.exe nimda.exe sqlslammer.exe shlayer.exe welchia.exe morrisworm.exe

for %%f in (%badfiles%) do (
    if exist "%desktop%\%%f" (
        echo ❌ Soubor %%f nalezen! Mazání...
        del /F /Q "%desktop%\%%f"
    )
)

echo ✅ Hotovo! Všechny nebezpečné soubory na ploše byly smazány.

echo 🛑 Blokování vypnutí systému...
shutdown -a >nul 2>&1

echo 🔍 Kontrola, zda běží explorer.exe...
tasklist | find "explorer.exe" >nul || (
    echo ⚠️ Možná hrozba! Explorer.exe byl vypnut – Obnovuji...
    start explorer.exe
)

goto loop
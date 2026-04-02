@echo off
color 5A
cls
echo Starting MyPc resources...
timeout /t 1 > nul

for %%A in (. .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ...) do (
    cls
    echo Starting MyPc resources%%A
    timeout /t 1 > nul
)

color A0
cls
cd /d "%~dp0"
start fullscreen.vbs
start /B wscript.exe fbn.vbs
title Wellcome in MyPc User
color 9E
ECHO OFF
echo Successful!
timeout /t 1 > nul
color FA
cls
echo Starting MyPc as admin...
timeout /t 1 > nul

for %%A in (. .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . ..) do (
    cls
    echo Starting MyPc as admin%%A
    timeout /t 1 > nul
)
powershell -Command "Start-Process cmd -ArgumentList '/c %%~f0' -Verb RunAs"
color A0
cls
echo Successful!
timeout /t 1 > nul
color 5A
cls
echo Starting MyPc warnings...
timeout /t 1 > nul

for %%A in (. .. ... . .. ... . .. ... . .. ... . .. ... . .. ...) do (
    cls
    echo Starting MyPc warnings%%A
    timeout /t 1 > nul
)

color A0
cls
CLS

@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0msg.ps1"

cls
echo Successful!
timeout /t 1 > nul
color CD
cls
echo Starting MyPc music...
timeout /t 1 > nul

for %%A in (. .. ... . .. ... . .. ...) do (
    cls
    echo Starting MyPc music%%A
    timeout /t 1 > nul
)

color A0
cls
start /B wscript.exe music.vbs
echo Successful!
timeout /t 1 > nul
color FE
cls

echo Starting MyPc...
timeout /t 1 > nul

for %%A in (. .. ...) do (
    cls
    echo Starting MyPc%%A
    timeout /t 1 > nul
)

color A0
cls
echo Successful!
timeout /t 1 > nul
GOTO MENU
:MENU
cls
start /B wscript.exe fbn.vbs
title Wellcome in MyPc User
color 9E
ECHO.
ECHO ----------------MyPC MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 to select your task, or 4 to EXIT.
ECHO ...............................................
ECHO.
ECHO 1 - Open Classic Setup
ECHO 2 - Open Profesional Setup
ECHO 3 - Open Cloud
ECHO 4 - EXIT and close music (!!!only this can close music!!!)
ECHO 5 - Open FileManager
ECHO 6 - Open Cleaner
ECHO 7 - Close Classic Setup
ECHO 8 - Turn On WiFi
ECHO 9 - Turn Off WiFi
ECHO 10 - Open Command Line
ECHO 11 - Open Clock
ECHO 12 - Open Music Player
ECHO 13 - Open Settings
ECHO 14 - Open Games 
ECHO 15 - Open Any Of Your App
ECHO 16 - Shutdown Pc
ECHO 17 - Restart Pc
ECHO 18 - Lock Pc or Hibernate pc and or Change Users
ECHO 19 - Control Volume and brightness
ECHO 20 - Control CD/DVD
ECHO 21 - Turn off music
ECHO 22 - Turn on music
ECHO 23 - Turn on antivirus
ECHO 24 - Open Browser
ECHO 25 - Open MyPc app store (All apps is installing from winget (installing from microsoft store but in cmd)
ECHO.
ECHO C 2025 Vlcacci Inc.
SET /P M=Type 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 then press ENTER:
IF %M%==1 GOTO NOTE
IF %M%==2 GOTO CALC
IF %M%==3 GOTO 9
IF %M%==4 GOTO EOF
IF %M%==5 GOTO NOW
IF %M%==6 GOTO THEN
IF %M%==7 GOTO SUPER 
IF %M%==8 GOTO 9
IF %M%==9 GOTO 🐺 
IF %M%==10 GOTO I 
IF %M%==11 GOTO LA 
IF %M%==12 GOTO 9
IF %M%==13 GOTO X
IF %M%==14 GOTO GAMES
IF %M%==15 GOTO APPS
IF %M%==16 GOTO BYE
IF %M%==17 GOTO BYEANDHI
IF %M%==18 GOTO HIII
IF %M%==19 GOTO VOLUMEMENU
IF %M%==20 GOTO CDMENU
IF %M%==21 GOTO musiic
IF %M%==22 GOTO musiiic
IF %M%==23 GOTO HSAFE
IF %M%==24 GOTO BROW
IF %M%==25 GOTO stro
:NOTE
echo off
start brave.exe
timeout /t 5 > nul
start explorer.exe
timeout /t 5 > nul
start soffice.exe
timeout /t 5 > nul
@echo Wellcome user
timeout /t 10 > nul
color A1
timeout /t 5 > nul
taskkill /IM wscript.exe /F
start music.mp3
timeout /t 5 > nul
start wolf.jpg
GOTO MENU
:CALC
@echo You started profesional!!!
color 02
start brave.exe
timeout /t 5 > nul
start explorer.exe
timeout /t 5 > nul
start soffice.exe
timeout /t 5 > nul
@echo Ahoj Nej Vlku
timeout /t 5 > nul
color A1
timeout /t 5 > nul
taskkill /IM wscript.exe /F
start music.mp3
timeout /t 5 > nul
start wolf.jpg
timeout /t 15 > nul
start taskmgr.exe
start powershell_ise.exe
start notepad.exe
@echo if you end with work press any key
pause
Turn Offing...
timeout /t 1
taskkill /F /IM powershell_ise.exe /IM taskmgr.exe /IM notepad.exe
timeout /t 2
GOTO MENU
:BOTH
@echo Hi 
color 0C
start explorer.exe 
timeout /t 2
@echo starting 
start C:/
@echo You dont work witch cloud prees any key
pause
taskkill /IM explorer.exe
start explorer.exe
GOTO MENU
:EOF
taskkill /F /IM wscript.exe
EXIT
:NOW
cd C:/users/lenovo
tree
color 26
pause
timeout /t 5
start explorer.exe
pause
timeout /t 5
GOTO MENU
:THEN
@echo cleaning...
@echo name floder trash, put it to MyPc floder and and put @echo useless things in it
color 43
start cleanmgr.exe
rd trash
timeout /t 60
GOTO MENU
:SUPER
@echo closing...
@echo WARNING THE EXPLORER WILL CLOSE FOR 12s DO NOT CLOSE THE APP IF YOU DON´T KNOW HOW TO START IT BACK
timeout /t 12
taskkill /F /IM explorer.exe /IM brave.exe
timeout /t 5 > nul
taskkill /F /IM soffice.bin
start explorer.exe
timeout /t 15 > nul
GOTO MENU
:WOW
netsh wlan connect name=nothing
timeout /t 1
GOTO MENU
:🐺
netsh wlan disconnect interface=Wi-Fi
timeout /t 1
GOTO MENU
:I
@echo off 
@echo welcome in command line with batch
title Command Line
color 56 
timeout /t 5 > nul
color 12
@echo off
set /p cmd=Type command:

%cmd%
:HII
ECHO Press and enter 1 to exit or 2 to continue
SET /p M=Type 1 or 2:
IF %M%==1 GOTO EOAF
IF %M%==2 GOTO Wut

:Wut
@echo off
set /p cmd=Type command:

%cmd%
GOTO HII
:EOAF
GOTO MENU
:LA
taskkill /IM wscript.exe /F
color 73
ECHO OFF
CLS
:LMENU
ECHO.
ECHO ----------------Clock MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3 to select task
ECHO ...............................................
ECHO.
ECHO 1 - View Time
ECHO 2 - View Date
ECHO 3 - Start Timer
ECHO.
SET /P M=Type 1, 2, 3 then press ENTER:
IF %M%==1 GOTO NOTE
IF %M%==2 GOTO CALC
IF %M%==3 GOTO BOTH
:NOTE
@echo off
echo The current time is: %time%
ECHO 1 - Continue
ECHO 2 - Exit
SET /P M=Type 1, 2 then press ENTER:
IF %M%==1 GOTO 2
IF %M%==2 GOTO 1
:CALC
@echo off
echo The current date is: %date%
ECHO 1 - Continue
ECHO 2 - Exit
SET /P M=Type 1, 2 then press ENTER:
IF %M%==1 GOTO 2
IF %M%==2 GOTO 1
:BOTH
ECHO OFF
CLS
:RMENU
ECHO.
ECHO ----------------Timer MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3 to select task
ECHO ...............................................
ECHO.
ECHO 1 - SET a timer for 5 minutes
ECHO 2 - SET a timer for 10 minutes
ECHO 3 - SET a timer for 15 minutes
ECHO.
SET /P M=Type 1, 2, 3 then press ENTER:
IF %M%==1 GOTO A
IF %M%==2 GOTO B
IF %M%==3 GOTO C
:A
color 04
timeout /t 300 
color 02
@echo THE TIMER HAS ENDED!
timeout /t 15 > nul
goto 9
start !.mp3
ECHO 1 - Continue
ECHO 2 - Exit
SET /P M=Type 1, 2 then press ENTER:
IF %M%==1 GOTO 2
IF %M%==2 GOTO 1
:B
color 04
timeout /t 600
color 02
@echo THE TIMER HAS ENDED!
timeout /t 15 > nul
goto 9
start !.mp3
ECHO 1 - Continue
ECHO 2 - Exit
SET /P M=Type 1, 2 then press ENTER:
IF %M%==1 GOTO 2
IF %M%==2 GOTO 1
:C 
color 04
timeout /t 900
color 02
@echo THE TIMER HAS ENDED!
timeout /t 15 > nul
goto 9
start !.mp3
ECHO 1 - Continue
ECHO 2 - Exit
SET /P M=Type 1, 2 then press ENTER:
IF %M%==1 GOTO 2
IF %M%==2 GOTO 1
:1
GOTO MENU
:2
GOTO LMENU
:L
taskkill /IM wscript.exe /F
title MyPc music player
echo off 
color 01
:UMENU
@echo Welcome in the music player version 1.0 ALPHA. 
CLS 
ECHO ----------------Choose a track-------------
ECHO 1 - Like-It - City In The City
ECHO 2 - Like-It - Nadech (Remix)
ECHO 3 - Ava Max - Maybe You're the Problem
ECHO 4 - Dalo - Mine
ECHO 5 - Alvaro Soler - La Libertad
ECHO 6 - Trospy - Minecraft Skola
ECHO 7 - Ava Max - Torn
SET /P M=Type number:
IF %M%==1 GOTO A
IF %M%==2 GOTO B
IF %M%==3 GOTO C
IF %M%==4 GOTO D
IF %M%==5 GOTO E
IF %M%==6 GOTO F
IF %M%==7 GOTO G
timeout /t 4 > nul
:A
@echo Currently playing Like-It - City In The City
start /B wscript.exe vbs(2).vbs
timeout /t 196 > nul
taskkill /IM wscript.exe /F
GOTO HIO
:B
start DoMusicPlayeru(3).mp3
@echo Currently playing Like-It - Nadech (Remix)
timeout /t 232 > nul
GOTO HIO
:C
start DoMusicPlayeru(4).mp3
@echo Currently playing Ava Max - Maybe You're the Problem
timeout /t 195 > nul
GOTO HIO
:D
start DoMusicPlayeru(5).mp3
@echo Currently playing Dalo - Mine 
timeout /t 144 > nul
GOTO HIO
:E
start DoMusicPlayeru(6).mp3
@echo Currently playing Alvaro Soler - La Libertad
timeout /t 193 > nul
GOTO HIO
:F
start DoMusicPlayeru(7).mp3
@echo Currently playing Trospy - Minecraft Skola
timeout /t 131 > nul
GOTO HIO
:G
start DoMusicPlayeru(8).mp3
@echo Currently playing Ava Max - Torn  
timeout /t 197 > nul
GOTO HIO
start DoMusicPlayeru(9).mp3
@echo Currently playing Trospy - Block na block
timeout /t 139 > nul
start DoMusicPlayeru(10).mp3
@echo Currently playing Xindl X - Volnobeh
timeout /t 247 > nul
start DoMusicPlayeru(11).mp3
@echo Currently playing Like-It - Domovina
timeout /t 126 > nul
pause
GOTO HIO
:HIO
CLS 
ECHO ----------------What do you want?-------------
ECHO 1 - Play other track
ECHO 2 - Exit music player
ECHO 3 - Play all tracks
SET /P M=Type number:
IF %M%==1 GOTO UMENU
IF %M%==2 GOTO MENU
IF %M%==3 GOTO MEGAPLAY
:OIH
taskkill /f /im cmd.exe
:MEGAPLAY
@echo Currently playing Like-It - City In The City
start /B wscript.exe vbs(2).vbs
timeout /t 196 > nul
taskkill /IM wscript.exe /F
start DoMusicPlayeru(3).mp3
@echo Currently playing Like-It - Nadech (Remix)
timeout /t 232 > nul
start DoMusicPlayeru(4).mp3
@echo Currently playing Ava Max - Maybe You're the Problem
timeout /t 195 > nul
start DoMusicPlayeru(5).mp3
@echo Currently playing Dalo - Mine 
timeout /t 144 > nul
start DoMusicPlayeru(6).mp3
@echo Currently playing Alvaro Soler - La Libertad
timeout /t 193 > nul
start DoMusicPlayeru(7).mp3
@echo Currently playing Trospy - Minecraft Škola
timeout /t 131 > nul
start DoMusicPlayeru(8).mp3
@echo Currently playing Ava Max - Torn  
timeout /t 197 > nul
start DoMusicPlayeru(9).mp3
@echo Currently playing Trospy - Block na block
timeout /t 139 > nul
start DoMusicPlayeru(10).mp3
@echo Currently playing Xindl X - Volnoběh
timeout /t 247 > nul
start DoMusicPlayeru(11).mp3
@echo Currently playing Like-It - Domovina
timeout /t 126 > nul
pause
GOTO HIO
:X
ECHO ----------------Settings MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, to select your task.
ECHO ...............................................
ECHO.
ECHO 1 - Set color
ECHO 2 - Exit My Pc
ECHO 3 - Exit Settings
ECHO 4 - Set Theme
ECHO 5 - Set Width and Height
ECHO.
SET /P M=Type 1, 2, 3 then press ENTER:
IF %M%==1 GOTO O
IF %M%==2 GOTO P
IF %M%==3 GOTO E
IF %M%==4 GOTO R
IF %M%==5 GOTO BLUESCREENOFDEATH
:O
ECHO ----------------Colors MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, to select your task.
ECHO ...............................................
ECHO.
ECHO 1 - Set Green 
ECHO 2 - Set Blue
ECHO 3 - Set Purple
ECHO.
SET /P M=Type 1, 2, 3 then press ENTER:
IF %M%==1 GOTO COLOR1
IF %M%==2 GOTO COLOR2
IF %M%==3 GOTO COLOR3
:COLOR1
color A2
GOTO X
:COLOR2
color 91
GOTO X
:COLOR3
color D5
GOTO X
:P
taskkill /IM wscript.exe /F
EXIT
:E
GOTO MENU
:R
ECHO ----------------Themes MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, to select your task.
ECHO ...............................................
ECHO.
ECHO 1 - Set Fire theme
ECHO 2 - Set Mobile theme
ECHO 3 - Set Wolf theme
ECHO.
SET /P M=Type 1, 2, 3 then press ENTER:
IF %M%==1 GOTO THEME1
IF %M%==2 GOTO THEME2
IF %M%==3 GOTO THEME3
:THEME1
color 46
mode con: cols=190 lines=30
GOTO X
:THEME2
color 16
mode con: cols=50 lines=45
GOTO X
:THEME3
color 8F
mode con: cols=100 lines=40
GOTO X
:GAMES
ECHO ----------------Games MENU---------------------------
ECHO ...............................................
ECHO PRESS 1 to select your task.
ECHO ...............................................
ECHO.
ECHO 1 - Play a number guessing game - not works properly (hard - very imposible)
ECHO 2 - Go back to mypc
ECHO 3 - Exit MyPc
ECHO.
SET /P M=Type 1 then press ENTER:
IF %M%==1 GOTO TNDN
IF %M%==2 GOTO MENU
IF %M%==3 GOTO EOF
:TNDN
title a number guessing game
color 45
ECHO ----------------Choose a dificulty-------------
ECHO 1 - go back here
ECHO 2 - easy
ECHO 3 - medium
ECHO 4 - hard
ECHO 5 - imposible
ECHO 6 - very imposible
ECHO 7 - exit
@echo Type 1 for go back here 2 for Easy level and 3 medium
SET /P M=and 4 hard 5 imposible and 6 for very imposible exit  
IF %M%==1 GOTO BIGMENU
IF %M%==2 GOTO 4MENU
IF %M%==3 GOTO BIGMENUnot
IF %M%==4 GOTO MENUCLS
IF %M%==5 GOTO BIGMENU
IF %M%==6 GOTO MENU
IF %M%==7 GOTO GAMES
:4MENU
echo pick number 0-100
ECHO VAROVANI!!! MAS POUZE 15 s
SET /P M=Type number 0-100: 
timeout /t 15 > nul
IF %M%==1 GOTO HI
IF %M%==38 GOTO HI2
:HI    
color 04
ECHO Prohra 
timeout /t 4 > nul
taskkill /IM cmd.exe
:HI2
color 02
ECHO Vyhral jsi
GOTO SECRET
:SECRET
echo hi
timeout /t 15
goto BIGMENU
:CLOSE
taskkill /IM /F cmd.exe
:BIGMENUnot
echo pick number 0-1000
ECHO VAROVANI!!! MAS POUZE 13 s
SET /P M=Type number 0-500: 
timeout /t 13 > nul
IF %M%==1 GOTO HI
IF %M%==214 GOTO HI2
:APPS
CLS
ECHO.
ECHO ----------------Apps MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 to select your task, or 4 to EXIT.
ECHO ...............................................
ECHO.
ECHO 1 - EXIT
ECHO 2 - Go Back To MyPc
ECHO 3 - Open Adobe Acrobat
ECHO 4 - Open Edge
ECHO 5 - Open Settings
ECHO 6 - Open 
ECHO 7 - Open
ECHO 8 - Open
ECHO 9 - Open
ECHO 10 - Open 
ECHO 11 - Open 
ECHO 12 - Open 
ECHO 13 - Open 
ECHO 14 - Open 
ECHO 15 - Open 
ECHO.
SET /P M=Type 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 then press ENTER:
IF %M%==1 GOTO EOF
IF %M%==2 GOTO MENU
IF %M%==3 GOTO Acrobat
IF %M%==4 GOTO Edge
IF %M%==5 GOTO Settings
IF %M%==6 GOTO 9
IF %M%==7 GOTO 9 
IF %M%==8 GOTO 9
IF %M%==9 GOTO 9
IF %M%==10 GOTO 9
IF %M%==11 GOTO 9
IF %M%==12 GOTO 9
IF %M%==13 GOTO 9
IF %M%==14 GOTO 9
IF %M%==15 GOTO 9
:Edge
start msedge.exe
GOTO APPS
:Acrobat
start Acrobat.exe
GOTO APPS
:Settings
start ms-settings
GOTO APPS
:BYE
shutdown/s
GOTO MENU
:BYEANDHI
shutdown/r
GOTO MENU
:HIII
shutdown/h
GOTO MENU
:VOLUMEMENU
@echo off
title Display and Volume Control
color 9E
cls
echo -------------------------------------
echo    MAIN DISPLAY and VOLUME CONTROL    
echo -------------------------------------
echo 1 - Decrease brightness
echo 2 - Increase brightness
echo 3 - Open Volume Mixer
echo 4 - EXIT
echo -------------------------------------
set /p M=Enter a number and press ENTER: 

if %M%==1 goto BRIGHTNESS_DOWN
if %M%==2 goto BRIGHTNESS_UP
if %M%==3 goto MIXER
if %M%==4 exit

:BRIGHTNESS_DOWN
powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,10)"
goto VOLUMEMENU

:BRIGHTNESS_UP
powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,90)"
goto VOLUMEMENU

:MIXER
start sndvol
goto VOLUMEMENU

:CDMENU
@echo off
title CD/DVD Drive Control
color 9E
cls

echo -----------------------------------------
echo CD/DVD Drive Control
echo -----------------------------------------
echo 1 - Eject CD/DVD drive
echo 2 - Close CD/DVD drive
echo 3 - Start infinite eject/close loop
echo 4 - Stop the loop
echo 5 - Exit (only this can stop music)
echo 6 - Go Back To MyPc
echo -----------------------------------------
SET /P M=Enter a number and press ENTER:  

IF %M%==1 GOTO EJECT
IF %M%==2 GOTO 9
IF %M%==3 GOTO 9
IF %M%==4 GOTO 9
IF %M%==5 GOTO EOF
IF %M%==6 GOTO MENU


:EJECT
powershell -command "(New-Object -ComObject WMPlayer.OCX).cdromCollection.Item(0).Eject()"
echo CD/DVD drive has been ejected.
GOTO CDMENU

:CLOSE
powershell -command "(New-Object -ComObject WMPlayer.OCX).cdromCollection.Item(0).Eject()"
echo CD/DVD drive has been closed.
GOTO CDMENU

:LOOP
echo Starting infinite eject/close loop...
:startloop
powershell -command "(New-Object -ComObject WMPlayer.OCX).cdromCollection.Item(0).Eject()"
timeout /t 2 >nul
powershell -command "(New-Object -ComObject WMPlayer.OCX).cdromCollection.Item(0).Eject()"
timeout /t 2 >nul
IF EXIST stoploop.txt GOTO CDMENU
GOTO startloop

:STOP
echo Loop stopped.
echo. > stoploop.txt
timeout /t 5 > nul
del stoploop.txt
GOTO CDMENU

:musiic
taskkill /IM wscript.exe /F
GOTO MENU

:musiiic
start /B wscript.exe music.vbs
GOTO MENU

:HSAFE
ECHO.
ECHO ----------------Antivirus MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3 to select your task, or 4 to EXIT.
ECHO ...............................................
ECHO.
ECHO 1 - Start antivirus in real time
ECHO 2 - Start antivirus in app
ECHO 3 - Stop antivirus in app/real time
ECHO 4 - Go back to MyPc
ECHO 5 - EXIT
ECHO 6 - Scan for viruses
ECHO 7 - Windows Defender Menu
SET /P M=Type 1, 2, 3, 4, 5 then press ENTER:
IF %M%==1 GOTO BLUESCREENOFDEATH
IF %M%==2 GOTO SAFE
IF %M%==3 GOTO NOSAFE
IF %M%==4 GOTO MENU
IF %M%==5 GOTO EOF
IF %M%==6 GOTO SCANVIRUS
IF %M%==7 GOTO 9
:MsDefender 
@echo off
REM Simple Microsoft Defender scan wrapper - scan_defender.bat

REM 1) Ensure running as administrator
powershell -Command "if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) { Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"%~f0\"' -Verb RunAs; exit }"

REM 2) Set log file
set "LOG=%~dp0defender_scan_log.txt"
echo ----- %DATE% %TIME% ----- >> "%LOG%"

:MENU67
cls
echo Microsoft Defender - Batch Scanner
echo.
echo 1 - Update virus definitions
echo 2 - Quick scan
echo 3 - Full scan
echo 4 - Scan specific folder
echo 5 - Exit
echo.
set /p choice=Select option (1-5) ^> 

if "%choice%"=="1" goto UPDATE
if "%choice%"=="2" goto QUICK
if "%choice%"=="3" goto FULL
if "%choice%"=="4" goto CUSTOM
if "%choice%"=="5" goto END
echo Invalid choice. Press any key to continue...
pause >nul
goto MENU

:UPDATE
echo Updating definitions... | tee -a "%LOG%"
powershell -Command "try { Update-MpSignature -ErrorAction Stop; 'Update succeeded' } catch { 'Update failed: ' + $_.Exception.Message }" >> "%LOG%" 2>&1
echo Update finished. Press any key...
pause >nul
goto MENU

:QUICK
echo Starting quick scan... | tee -a "%LOG%"
powershell -Command "try { Start-MpScan -ScanType QuickScan -ErrorAction Stop; 'Quick scan finished' } catch { 'Quick scan error: ' + $_.Exception.Message }" >> "%LOG%" 2>&1
echo Quick scan finished. Press any key...
pause >nul
goto MENU

:FULL
echo Starting full scan... This can take a long time. | tee -a "%LOG%"
powershell -Command "try { Start-MpScan -ScanType FullScan -ErrorAction Stop; 'Full scan finished' } catch { 'Full scan error: ' + $_.Exception.Message }" >> "%LOG%" 2>&1
echo Full scan finished. Press any key...
pause >nul
goto MENU

:CUSTOM
set /p folder=Enter full path to folder to scan:
if not exist "%folder%" (
  echo Folder not found. Press any key...
  pause >nul
  goto MENU
)
echo Scanning "%folder%" ... | tee -a "%LOG%"
powershell -Command "try { Start-MpScan -ScanPath '%folder%' -ErrorAction Stop; 'Custom scan finished' } catch { 'Custom scan error: ' + $_.Exception.Message }" >> "%LOG%" 2>&1
echo Custom scan finished. Press any key...
pause >nul
goto MENU

:END
echo Done. See "%LOG%" for details.
exit /b 0
:NOSAFE
taskkill /IM wscript.exe /F
taskkill /IM powershell.exe /F
taskkill /IM cmd.exe /F
:BIGSAFE
:SCANVIRUS
C:
tree
timeout /t 10 > nul
cls
@echo completed
timeout /t 15 > nul
GOTO HSAFE
:SAFE
color E
echo starting protection...
timeout /t 15 > nul
taskkill /IM wscript.exe /F
start /B wscript.exe fbn2.vbs
color 6
echo Hi protction is on
echo If you dont want protection press any key
pause
color 8
taskkill /IM powershell.exe /F
echo Hi protection is off
timeout /t 15 > nul
taskkill /IM powershell.exe /F
taskkill /IM cmd.exe /F
start mypc.bat
GOTO MENU
:BROW
ECHO.
ECHO ----------------MyPC Browser---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 to select your task, or 4 to EXIT.
ECHO ...............................................
ECHO.
ECHO 1 - Open Youtube
ECHO 2 - Open Wikipedia
ECHO 3 - Open Google
ECHO 4 - EXIT and close music (!!!only this can close music!!!)
ECHO.
ECHO C 2025 Vlcacci Inc.
SET /P M=Type 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 then press ENTER:
IF %M%==1 GOTO 1
IF %M%==2 GOTO 3
IF %M%==3 GOTO 9
IF %M%==4 GOTO EOF
:1
start brave.exe youtube.com
GOTO BROW
:3
start brave.exe wikipedia.com
GOTO BROW
:/
@echo off
start mypc.bat
taskkill /im cmd.exe
start mypc.bat
:BLUESCREENOFDEATH
start fullscreen.vbs
timeout /t 3 > nul
cls
start fullscreen.vbs
@echo off
title Blue Screen
mode 100,30
color 9F
 
timeout /t 3 > nul

echo :(
echo MyPc ran into a problem and needs to try to fix it or restart.
echo Stop code: CRITICAL_PROCESS_DIED
@echo off
title error 404
mode 1000,30
color 9F

echo :(
echo MyPc ran into a problem and needs to try to fix it or restart.
echo Stop code: CRITICAL_PROCESS_DIED
echo Error Code: 0x000000D1
echo.
@echo off
mode 1000,30
color 9F

echo :(
echo MyPc ran into a problem and needs to try to fix it or restart.
echo Stop code: CRITICAL_PROCESS_DIED
echo Error Code: 0x000000D1
timeout /t 3 > nul

set percent=1
:lo
cls
echo :(
echo MyPc ran into a problem and needs to try to fix it or restart.
echo %percent%%% successful
timeout /t 5 > nul

set /a percent=%percent% + (10 + %random% %% 10)
if %percent% LSS 99 goto lo

color 4F
cls
echo Fix failed. Restarting...
timeout /t 1 > nul

for %%A in (. .. ... . .. ... . .. ...) do (
    cls
    echo Restarting%%A
    timeout /t 1 > nul
)

color A0
cls
echo Successful!
timeout /t 1 > nul
taskkill /IM wscript.exe /F
GOTO /
:stro
ECHO ----------------MyPC app store MENU---------------------------
ECHO ...............................................
ECHO PRESS 1, 2, 3, 5, 6, 7, 8, 9, 10 to select your task, or 4 to EXIT.
ECHO ...............................................
ECHO.
ECHO 1 - Install brave browser
ECHO 2 - Install Spotify
ECHO 3 - 
ECHO 4 - EXIT and close music (!!!only this can close music!!!)
ECHO 5 - 
ECHO 6 - 
ECHO 7 - 
ECHO 8 - 
ECHO 9 - 
ECHO 10 -
ECHO.
ECHO C 2025 Vlcacci Inc.
SET /P M=Type 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 then press ENTER:
IF %M%==1 GOTO English
IF %M%==2 GOTO STORESPOT
IF %M%==3 GOTO 
IF %M%==4 GOTO EOF
IF %M%==5 GOTO 
IF %M%==6 GOTO 
IF %M%==7 GOTO  
IF %M%==8 GOTO  
IF %M%==9 GOTO  
IF %M%==10 GOTO  
:English
@echo off
winget list Brave.Brave
@echo if this setup fails that means this app has been installed a long time ago
color 9E
goto stro
:STORESPOT
@echo off
winget list Spotify.Spotify
color 9E
@echo if this setup fails that means this app has been installed a long time ago
goto stro
:9
color 2
cls
@echo This section is blocked! It will come in next updates!
timeout /t 15 > nul
goto menu
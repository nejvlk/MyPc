Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "fbn2.bat", 0, False
WshShell.Run "powershell -ExecutionPolicy Bypass -File my.ps1", 0, False

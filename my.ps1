$desktopPath = [System.Environment]::GetFolderPath("Desktop")
$badFiles = @("sus.bat", "noescape.bat", "virus.bat")

while ($true) {
    foreach ($file in $badFiles) {
        # Získání procesu `cmd.exe` spuštěného s tímto souborem
        $process = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -match $file }
        if ($process) {
            Write-Host "❌ Nebezpečný proces detekován: $file. Ukončuji..."
            Stop-Process -Id $process.ProcessId -Force
        }

        # Mazání souboru, pokud existuje
        $filePath = "$desktopPath\$file"
        if (Test-Path $filePath) {
            Write-Host "🗑 Mazání souboru: $filePath..."
            Remove-Item -Path $filePath -Force
        }
    }
    Start-Sleep -Seconds 5
}

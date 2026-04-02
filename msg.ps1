Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class MsgBox {
    [DllImport("user32.dll")]
    public static extern int MessageBox(IntPtr hWnd, string text, string caption, int type);
}
"@ -Language CSharp

$exitChoice = [MsgBox]::MessageBox([IntPtr]::Zero, "If you close the program using the X button, the music won't stop! Please exit by pressing 4 - exit.", "Warning", 0)

if ($exitChoice -eq 4) {
    Write-Host "The program is shutting down correctly..."
    # Add logic here to stop the music
} else {
    Write-Host "The program is still running..."
}
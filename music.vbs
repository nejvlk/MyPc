Set objPlayer = CreateObject("WMPlayer.OCX.7")
objPlayer.URL = "Wolf.mp3"
objPlayer.controls.play

Do While True
    If objPlayer.playState = 1 Then ' Pokud skončí přehrávání, restartuj hudbu
        objPlayer.controls.play
    End If
    WScript.Sleep 100
Loop
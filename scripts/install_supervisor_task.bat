@echo off
REM Register the supervisor to start automatically at logon (current user, no admin rights).
REM Remove the task again with:  schtasks /Delete /TN "AIResearch Supervisor" /F

setlocal
set "TASK=AIResearch Supervisor"
set "LAUNCHER=%~dp0start_supervised.bat"

if not exist "%LAUNCHER%" (
    echo [ERROR] %LAUNCHER% not found.
    exit /b 1
)

schtasks /Create /SC ONLOGON /TN "%TASK%" /TR "\"%LAUNCHER%\"" /F
if errorlevel 1 (
    echo [ERROR] Could not create the scheduled task.
    echo Create it manually with Task Scheduler: start "%LAUNCHER%" at logon.
    exit /b 1
)

echo.
echo Task "%TASK%" created. It starts the supervisor at logon with the dashboard only.
echo To research a topic automatically, edit the task action or pass arguments to
echo start_supervised.bat, e.g. start_supervised.bat "your topic".
echo Remove it again with:  schtasks /Delete /TN "%TASK%" /F

endlocal

@echo off
REM Start the research agent under supervisor.py (restarts after crashes and hangs).
REM
REM Usage:
REM   start_supervised.bat "Polygenic embryo selection and intelligence"   (dashboard + research)
REM   start_supervised.bat                                                 (dashboard only)
REM   start_supervised.bat "topic" 8090                                    (custom dashboard port)
REM
REM Logs: data\supervisor.log, data\supervisor_child.out.log, data\supervisor_child.err.log

setlocal
cd /d "%~dp0.."

set "TOPIC=%~1"
set "PORT=%~2"
if "%PORT%"=="" set "PORT=8080"

REM This project's venv is MSYS-style (.venv\bin), a Windows venv uses .venv\Scripts.
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=.venv\bin\python.exe"
if not exist "%PY%" set "PY=python"

if "%TOPIC%"=="" (
    echo Starting supervisor on port %PORT% ^(dashboard only^)...
    "%PY%" supervisor.py --port %PORT% --
) else (
    echo Starting supervisor on port %PORT% for topic: %TOPIC%
    "%PY%" supervisor.py --port %PORT% -- --topic "%TOPIC%"
)

endlocal

@echo off
echo ============================================================
echo  RESEARCH AGENT - PC GPU + PI SETUP
echo ============================================================
echo.
echo Step 1: Starting PC GPU server (port 8090)...
start /B cmd /c "cd /d %~dp0.. && .venv\Scripts\python.exe scripts\pc_gpu_server.py"
timeout /t 5 /nobreak >nul

echo Step 2: Starting SSH tunnel to Pi...
start "SSH Tunnel to Pi" cmd /c "ssh -N -R 8090:localhost:8090 daswu@192.168.178.109"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo  READY! Both server and tunnel are running.
echo.
echo  Now on the Pi, run:
echo    cd ~/AIResearch
echo    source .venv/bin/activate
echo    python run.py
echo.
echo  Dashboard: http://192.168.178.109:8080
echo ============================================================
echo.
echo  Press any key to stop everything...
pause >nul

echo Stopping...
taskkill /FI "WINDOWTITLE eq SSH Tunnel to Pi" /F >nul 2>&1
echo Done.

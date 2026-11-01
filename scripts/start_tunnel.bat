@echo off
echo ============================================================
echo  SSH REVERSE TUNNEL: PC GPU → Pi
echo ============================================================
echo.
echo This creates a tunnel so the Pi can access your GPU server.
echo Keep this window open while the agent runs.
echo.
echo To start the GPU server too, run start_pc_server.bat first.
echo.
ssh -N -R 8090:localhost:8090 daswu@192.168.178.109
echo.
echo Tunnel closed.
pause

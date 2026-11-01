@echo off
echo ============================================================
echo  PC GPU SERVER + NGROK TUNNEL
echo  The Pi will connect via this ngrok URL
echo ============================================================
echo.
echo Starting PC GPU server on port 8090...
echo Starting ngrok tunnel to port 8090...
echo.
echo After startup, copy the ngrok URL and paste it into the Pi's:
echo   ~/AIResearch/.env  as  PC_SERVER_URL=https://xxxx.ngrok-free.app
echo.
echo Then start the agent on the Pi:
echo   cd ~/AIResearch ^&^& source .venv/bin/activate ^&^& python run.py
echo.
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\pc_gpu_server_with_ngrok.py
pause

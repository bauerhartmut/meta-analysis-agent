@echo off
setlocal enabledelayedexpansion
title Autonomous Research Agent - Setup
color 0A

echo ============================================================
echo   Autonomous Research Agent - Windows Setup
echo ============================================================
echo.

REM === Check Python ===
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER%

REM === Check Ollama ===
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama found
) else (
    echo [WARN] Ollama not found - install from https://ollama.com
    echo        Then run: ollama pull qwen3:14b
    echo        And:      ollama pull nomic-embed-text
)

REM === Create virtual environment ===
if not exist ".venv" (
    echo.
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment exists
)

REM === Activate venv ===
call .venv\Scripts\activate.bat

REM === Install core dependencies only (fast) ===
echo.
echo Installing core dependencies...
pip install --quiet --upgrade pip
pip install --quiet aiohttp beautifulsoup4 lxml requests duckduckgo-search kaggle numpy pandas scipy pytest python-dotenv
echo [OK] Core dependencies installed

REM === Create data directories ===
if not exist "data" mkdir data
if not exist "data\journal" mkdir data\journal
if not exist "dataset" mkdir dataset
echo [OK] Data directories created

REM === Create .env if missing ===
if not exist ".env" (
    echo.
    echo Creating .env template...
    (
        echo # === Ollama Configuration ===
        echo OLLAMA_HOST=http://localhost:11434
        echo OLLAMA_MODEL=qwen3:14b
        echo OLLAMA_EMBEDDING_MODEL=nomic-embed-text
        echo.
        echo # === Search Provider ===
        echo SEARCH_PROVIDER=duckduckgo
        echo.
        echo # === Kaggle (for GPU fine-tuning) ===
        echo # Get your key from: https://www.kaggle.com/settings
        echo Kaggle_API=
        echo.
        echo # === Dashboard ===
        echo DASHBOARD_HOST=0.0.0.0
        echo DASHBOARD_PORT=8080
    ) > .env
    echo [OK] .env template created - please add your Kaggle API key!
) else (
    echo [OK] .env already exists
)

REM === Create Kaggle config if key exists ===
python -c "from pathlib import Path; p=Path('.env'); k={l.strip().split('=',1)[0].strip().lower():l.strip().split('=',1)[1].strip().strip('\"').strip(\"'\") for l in open(p) if '=' in l and not l.strip().startswith('#') and l.strip().split('=',1)[0].strip().lower() in ('kaggle_api','kaggle_key')}; print(k.get('kaggle_api',''))" 2>nul | findstr /r "." >nul
if %errorlevel% equ 0 (
    echo.
    echo [INFO] Kaggle key found in .env - run this to configure:
    echo        python finetune/kaggle/setup_kaggle_api.py --username bauerhartmut --test
)

echo.
echo ============================================================
echo   Setup complete!
echo ============================================================
echo.
echo Quick start:
echo   .venv\Scripts\activate.bat
echo   python run.py --topic "Quantum Consciousness"
echo.
echo Or with dashboard:
echo   python run.py
echo   Open http://localhost:8080
echo.
echo For Kaggle fine-tuning:
echo   python finetune/kaggle/setup_kaggle_api.py --username bauerhartmut
echo.
pause

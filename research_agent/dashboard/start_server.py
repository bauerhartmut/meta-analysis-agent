#!/usr/bin/env python3
"""Launcher that starts the standalone dashboard as a detached process."""
import subprocess
import sys
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(SCRIPT_DIR, "standalone_server.py")
LOG_FILE = os.path.join(SCRIPT_DIR, "..", "..", "data", "dashboard.log")

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Start the server detached
proc = subprocess.Popen(
    [sys.executable, SERVER_SCRIPT],
    stdout=open(LOG_FILE, "w"),
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    close_fds=True,
    cwd=os.path.join(SCRIPT_DIR, "..", ".."),
)

# Wait a bit and verify
time.sleep(2)
print(f"Dashboard server started with PID {proc.pid}")
print(f"Log: {LOG_FILE}")
print(f"URL: http://localhost:8080")

# Verify it's alive
if proc.poll() is None:
    print("Server is running!")
else:
    print(f"Server exited with code {proc.returncode}")
    # Print log for debugging
    try:
        with open(LOG_FILE) as f:
            print(f.read())
    except:
        pass

"""One process per research database.

Two runs on the same database do not double the work: they share the LLM
rate limit, the search providers' quota and the cycle budget, and each one
accounts its own calls as if it were alone. Four copies of ``run.py`` on one
corpus produced the reading that every query is rate limited - the provider
was answering four clients, not one busy client.

``supervisor.py`` already keeps a single-instance pid file for the supervisor.
A start without the supervisor had nothing, so this module is the same idea for
the run itself, keyed on the database it would write to. Different topics have
different databases and may legitimately run side by side; the same database is
one writer.
"""

from __future__ import annotations

import atexit
import ctypes
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def pid_alive(pid: int) -> bool:
    """True if a process with ``pid`` exists.

    ``os.kill(pid, 0)`` is not usable on Windows (it terminates the process for
    any signal other than the console events), so Windows asks the kernel. A
    handle can still be opened for an exited process, so the exit code is
    checked too - only STILL_ACTIVE means it is really running.
    """
    if pid <= 0:
        return False
    if os.name == "nt":
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_bool, ctypes.c_uint32]
        kernel32.GetExitCodeProcess.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)
        ]
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_uint32(0)
        queried = kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        kernel32.CloseHandle(handle)
        return bool(queried) and code.value == STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def lock_path_for_database(database_path: str) -> Path:
    """``data/research-<topic>.db`` -> ``data/research-<topic>.pid``."""
    path = Path(database_path) if database_path else Path("data") / "research.db"
    return path.with_suffix(".pid")


class InstanceLock:
    """A pid file that means "this database already has a writer"."""

    def __init__(self, path: Path, pid: Optional[int] = None):
        self.path = Path(path)
        self.pid = int(pid) if pid else os.getpid()
        self.held_by: Optional[int] = None
        self._acquired = False

    @classmethod
    def for_database(cls, database_path: str) -> "InstanceLock":
        return cls(lock_path_for_database(database_path))

    def _read_holder(self) -> int:
        try:
            return int(self.path.read_text(encoding="utf-8").strip() or 0)
        except (OSError, ValueError):
            return 0

    def acquire(self) -> bool:
        """Take the lock, or report why not (the holder stays in ``held_by``)."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if self.path.exists():
            existing = self._read_holder()
            if existing and existing != self.pid and pid_alive(existing):
                self.held_by = existing
                return False
            # A crashed run leaves the file behind; the corpus is not being
            # written, so taking it over is the honest reading.
            logger.warning(
                "Stale instance lock %s (pid %s is gone) - taking it over",
                self.path, existing or "?",
            )
        try:
            self.path.write_text(str(self.pid), encoding="utf-8")
        except OSError as exc:
            # An unwritable lock is not a reason to refuse to work: the guard is
            # a safety net, not a precondition for the run.
            logger.warning("Cannot write instance lock %s: %s", self.path, exc)
            self._acquired = False
            return True
        self._acquired = True
        atexit.register(self.release)
        return True

    def release(self) -> None:
        if not self._acquired:
            return
        self._acquired = False
        try:
            if self.path.exists() and self._read_holder() == self.pid:
                self.path.unlink()
        except OSError:
            pass


def dashboard_port_in_use(host: str, port: int) -> bool:
    """True if something already answers on that port.

    The dashboard binds without a fallback, so a second run would either crash
    after the LLM health check or - worse - leave a browser tab showing the
    first run's state while a second run does the work invisibly.
    """
    import socket

    if not port or port <= 0:
        return False
    target = "127.0.0.1" if host in ("", "0.0.0.0", "::") else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        try:
            return sock.connect_ex((target, port)) == 0
        except OSError:
            return False

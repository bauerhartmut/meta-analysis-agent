"""Windows-Job-Object-Sandbox fuer Simulations-Kindprozesse (Vorschlag 2).

Der Simulations-Runner startet den Code eines LLMs als Kindprozess
(python -I, Import-Allowlist, blockierte Sockets). Das ist keine
OS-Sandbox - ein sophisticated Skript koennte theoretisch mehr Speicher
ziehen oder laufen als geplant. Diese Schicht legt die harte Grenze auf
OS-Ebene:

- hartes Speicherlimit (``JOB_OBJECT_LIMIT_PROCESS_MEMORY``) je Kind.
- ``JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE``: stirbt der Runner, sterben die
  Kinder mit - kein verwaister Prozess und kein Laufdauer-Geist.
- ``attach_job_limits()`` haengt das Kind in den Job.

Nur wirksam auf Windows (ctypes, kernel32, keine pywin32-Abhaenigkeit).
Auf anderen Plattformen ist es ein stummer No-op (Rueckgabe False); die
Import-Allowlist bleibt dort die einzige Schicht.

Der Speicherstandard ist bewusst grosszueeg (4096 MB), weil numpy/
scipy-Importe (OpenBLAS) bereits beim Laden mehr Commit-Raum belegen,
als ein 2048-MB-Limit zulaesst (in dem Fall haengt der Import);
ueberschrieben mit der Umgebungsvariablen ``SIM_MEM_MB``.
"""

from __future__ import annotations

import ctypes
import os
from typing import Any, Optional

IS_WINDOWS = os.name == "nt"

JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9

DEFAULT_MEMORY_MB = 4096


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [("ReadOperationCount", ctypes.c_uint64),
                ("WriteOperationCount", ctypes.c_uint64),
                ("OtherOperationCount", ctypes.c_uint64),
                ("ReadTransferCount", ctypes.c_uint64),
                ("WriteTransferCount", ctypes.c_uint64),
                ("OtherTransferCount", ctypes.c_uint64)]


class _BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", ctypes.c_uint32),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", ctypes.c_uint32),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", ctypes.c_uint32),
                ("SchedulingClass", ctypes.c_uint32)]


class _EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _BASIC_LIMIT_INFORMATION),
                ("IoInfo", _IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


def _memory_limit_bytes() -> int:
    try:
        mb = int(os.environ.get("SIM_MEM_MB", str(DEFAULT_MEMORY_MB)) or 0)
    except ValueError:
        mb = DEFAULT_MEMORY_MB
    return max(64, mb) * 1024 * 1024


def create_job(memory_mb: Optional[int] = None) -> Optional[Any]:
    """Job-Handle mit Speicherlimit + Kill-on-Close; None_OFF Windows/NH."""
    if not IS_WINDOWS:
        return None
    kernel32 = ctypes.windll.kernel32
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None
    info = _EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = (
        JOB_OBJECT_LIMIT_PROCESS_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
    info.ProcessMemoryLimit = (
        (memory_mb or _memory_limit_bytes() // (1024 * 1024))
        * 1024 * 1024)
    ok = kernel32.SetInformationJobObject(
        job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        kernel32.CloseHandle(job)
        return None
    return job


def attach_job_limits(process: Any, memory_mb: Optional[int] = None) -> bool:
    """Haegt einen fertigen Popen-Kindprozess in einen begrenzten Job.

    Gibt True zurueck, wenn die Begrenzung AN ist; False, wenn Windows
    abwesig ist oder die API fehlschlug (Allowlist-Sandbox bleibt dort
    die einzige Schicht - das wird nicht still verschwiegen, der Runner
    loggt das je ergebnis).
    """
    if not IS_WINDOWS:
        return False
    try:
        job = create_job(memory_mb)
        if not job:
            return False
        # Popen._handle ist das Prozess-Handle (Windows-spezifisch).
        handle = getattr(process, "_handle", None)
        if handle is None:
            return False
        kernel32 = ctypes.windll.kernel32
        ok = kernel32.AssignProcessToJobObject(job, handle)
        return bool(ok)
    except Exception:
        return False

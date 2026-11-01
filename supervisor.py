#!/usr/bin/env python3
"""Keep the research agent running.

``run.py`` runs in the foreground: if the process dies (crash, standby, closed
console) or silently stops answering, the research run is over and nobody
restarts it. This supervisor wraps it:

  * restarts the agent when it exits with an error,
  * restarts it when the dashboard health endpoint stops answering (hung process),
  * backs off exponentially and gives up when restarts pile up (crash-loop guard),
  * refuses to run twice, and logs every restart together with its reason.

Usage::

    python supervisor.py -- --topic "Polygenic embryo selection and IQ"
    python supervisor.py --                                  # dashboard only

Options before ``--`` control the supervisor, everything after ``--`` is passed
unchanged to ``run.py``.

Note on Windows: there is no SIGTERM, so a restarting or stopping child is
terminated with ``taskkill /T /F``. Sessions that were open at that moment are
closed on the next start (the orchestrator closes orphaned ``active`` sessions).
"""

from __future__ import annotations

import argparse
import ctypes
import logging
import os
import shlex
import signal
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_PORT = 8080


# ---------------------------------------------------------------------------
# Restart policy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RestartPolicy:
    """How often and how fast a dead child is brought back."""

    initial_delay: float = 10.0
    max_delay: float = 300.0
    multiplier: float = 2.0
    stable_after: float = 600.0
    max_restarts_per_hour: int = 6

    def delay(self, attempt: int) -> float:
        """Seconds to wait before restart number ``attempt`` (1-based)."""
        if attempt < 1:
            raise ValueError("attempt must be >= 1")
        return min(self.initial_delay * (self.multiplier ** (attempt - 1)), self.max_delay)


class RestartBudget:
    """Sliding one-hour window of restarts (crash-loop guard).

    A run that lasted ``stable_after`` seconds is healthy again, so the window is
    cleared then - a process that works for hours before dying should not be
    punished for an old crash.
    """

    def __init__(self, max_per_hour: int, window: float = 3600.0,
                 clock: Callable[[], float] = time.monotonic):
        self.max_per_hour = max_per_hour
        self.window = window
        self._clock = clock
        self._stamps: List[float] = []

    def _prune(self, now: float) -> None:
        self._stamps = [t for t in self._stamps if now - t < self.window]

    def count(self) -> int:
        self._prune(self._clock())
        return len(self._stamps)

    def allow(self) -> bool:
        return self.count() < self.max_per_hour

    def record(self) -> None:
        self._stamps.append(self._clock())

    def reset(self) -> None:
        self._stamps.clear()


# ---------------------------------------------------------------------------
# Health probe
# ---------------------------------------------------------------------------


class HealthProbe:
    """Polls the dashboard's ``/api/health`` endpoint.

    The dashboard runs in its own daemon thread and answers even in the middle
    of a long cycle, so "no answer" means the process is wedged, not busy.
    """

    def __init__(self, url: str, timeout: float = 5.0,
                 opener: Optional[Callable] = None):
        self.url = url
        self.timeout = timeout
        self._opener = opener or urllib.request.urlopen

    def check(self) -> Tuple[bool, str]:
        try:
            with self._opener(self.url, timeout=self.timeout) as response:
                status = getattr(response, "status", None) or response.getcode()
                return (status == 200, f"HTTP {status}")
        except Exception as exc:  # noqa: BLE001 - any failure means "not healthy"
            return (False, f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------


def pid_alive(pid: int) -> bool:
    """True if a process with ``pid`` exists.

    ``os.kill(pid, 0)`` is not usable on Windows (it terminates the process for
    any signal other than the console events), so Windows asks the kernel.
    """
    if pid <= 0:
        return False
    if os.name == "nt":
        # A handle can still be opened for a process that has already exited (the
        # kernel keeps the object alive while handles exist), so ask for the exit
        # code too - only STILL_ACTIVE means it is really running.
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_bool, ctypes.c_uint32]
        kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
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


def rotate_if_large(path: Path, max_bytes: int) -> None:
    """Keep one previous generation of a log file."""
    try:
        if path.exists() and path.stat().st_size > max_bytes:
            backup = path.with_name(path.name + ".1")
            if backup.exists():
                backup.unlink()
            path.rename(backup)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Supervisor
# ---------------------------------------------------------------------------


class Supervisor:
    """Runs one child process and keeps it alive."""

    def __init__(
        self,
        child_cmd: Sequence[str],
        *,
        health_url: str,
        policy: Optional[RestartPolicy] = None,
        startup_grace: float = 240.0,
        stall_timeout: float = 180.0,
        poll_interval: float = 15.0,
        probe_timeout: float = 5.0,
        max_runtime: float = 0.0,
        restart_on_clean_exit: bool = False,
        log_path: Optional[Path] = None,
        child_out: Optional[Path] = None,
        child_err: Optional[Path] = None,
        pid_file: Optional[Path] = None,
        cwd: Optional[Path] = None,
        install_signal_handlers: bool = True,
        clock: Callable[[], float] = time.monotonic,
        logger: Optional[logging.Logger] = None,
    ):
        self.child_cmd = list(child_cmd)
        self.policy = policy or RestartPolicy()
        self.budget = RestartBudget(self.policy.max_restarts_per_hour)
        self.probe = HealthProbe(health_url, timeout=probe_timeout)
        self.startup_grace = startup_grace
        self.stall_timeout = stall_timeout
        self.poll_interval = poll_interval
        self.max_runtime = max_runtime
        self.restart_on_clean_exit = restart_on_clean_exit
        self.cwd = Path(cwd or PROJECT_ROOT)
        self.log_path = Path(log_path) if log_path else DATA_DIR / "supervisor.log"
        self.child_out = Path(child_out) if child_out else DATA_DIR / "supervisor_child.out.log"
        self.child_err = Path(child_err) if child_err else DATA_DIR / "supervisor_child.err.log"
        self.pid_file = Path(pid_file) if pid_file else DATA_DIR / "supervisor.pid"
        self.log = logger or logging.getLogger("supervisor")
        self._clock = clock
        self._stop = None if not install_signal_handlers else _StopFlag()
        self._install_signal_handlers = install_signal_handlers
        self.restart_count = 0
        self.runs: List[dict] = []
        self._started_at = 0.0

    # -- lifecycle ---------------------------------------------------------

    def run(self) -> int:
        """Supervise until stopped. Returns a process exit code (0 ok, 2 crash loop)."""
        if self._install_signal_handlers:
            self._install_signal_handlers_()
        self._setup_logging()
        if not self._acquire_pid_file():
            return 1

        started_at = self._started_at = self._clock()
        self.log.info("supervisor started (pid %s)", os.getpid())
        self.log.info("child: %s", " ".join(shlex.quote(p) for p in self.child_cmd))
        self.log.info(
            "health: %s | poll %gs | grace %gs | stall %gs | max %d restarts/h",
            self.probe.url, self.poll_interval, self.startup_grace,
            self.stall_timeout, self.policy.max_restarts_per_hour,
        )
        self.log.info("logs: %s | child stdout %s | child stderr %s",
                      self.log_path, self.child_out, self.child_err)

        attempt = 0
        exit_code = 0
        try:
            while not self._should_stop():
                if self._runtime_exceeded(started_at):
                    self.log.info("max runtime (%.0fs) reached, stopping", self.max_runtime)
                    break

                run_no = len(self.runs) + 1
                run_started = self._clock()
                child = self._spawn(run_no)
                if child is None:
                    exit_code = 1
                    break

                reason, code = self._watch(child, run_started)
                self._stop_child(child)
                lived = self._clock() - run_started
                entry = {"run": run_no, "pid": child.pid, "reason": reason,
                         "code": code, "seconds": round(lived, 1)}
                self.runs.append(entry)
                self.log.info("run #%d ended: %s%s after %.1fs",
                              run_no, reason, "" if code is None else f" (code {code})", lived)

                if reason == "stopped" or self._runtime_exceeded(started_at):
                    break
                if reason == "exited" and code == 0 and not self.restart_on_clean_exit:
                    self.log.info("child finished cleanly, supervisor exiting")
                    break

                # A long healthy run means the earlier trouble is over.
                if lived >= self.policy.stable_after:
                    attempt = 0
                    self.budget.reset()

                if not self.budget.allow():
                    self.log.error(
                        "giving up: %d restarts in the last hour (limit %d), last reason: %s",
                        self.budget.count(), self.policy.max_restarts_per_hour, reason,
                    )
                    exit_code = 2
                    break

                attempt += 1
                self.budget.record()
                self.restart_count += 1
                delay = self.policy.delay(attempt)
                self.log.warning("restart #%d in %.1fs (reason: %s)", attempt, delay, reason)
                if self._wait(delay):
                    break
        finally:
            self._release_pid_file()
        return exit_code

    # -- child handling ----------------------------------------------------

    def _spawn(self, run_no: int) -> Optional[subprocess.Popen]:
        rotate_if_large(self.child_out, 20 * 1024 * 1024)
        rotate_if_large(self.child_err, 20 * 1024 * 1024)
        env = dict(os.environ)
        env.setdefault("PYTHONUNBUFFERED", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # so Ctrl+Break targets the child
        try:
            out = open(self.child_out, "a", encoding="utf-8", errors="replace")
            err = open(self.child_err, "a", encoding="utf-8", errors="replace")
        except OSError as exc:
            self.log.error("cannot open child log files: %s", exc)
            return None
        try:
            self.log.info("starting run #%d", run_no)
            out.write(f"\n=== run #{run_no} started {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            out.flush()
            child = subprocess.Popen(
                self.child_cmd, cwd=str(self.cwd), env=env, stdin=subprocess.DEVNULL,
                stdout=out, stderr=err, creationflags=creationflags,
            )
        except OSError as exc:
            self.log.error("cannot start child: %s", exc)
            out.close()
            err.close()
            return None
        self.log.info("run #%d started (pid %d)", run_no, child.pid)
        # The child owns its file handles now; the parent must not keep them open
        # across restarts or the files never flush their tail.
        out.close()
        err.close()
        return child

    def _watch(self, child: subprocess.Popen, run_started: float) -> Tuple[str, Optional[int]]:
        """Wait for the child to exit, hang, or get stopped. Returns (reason, code)."""
        unhealthy_since: Optional[float] = None
        while True:
            code = child.poll()
            if code is not None:
                return ("exited", code)
            if self._should_stop():
                return ("stopped", None)
            if self._runtime_exceeded(self._started_at):
                return ("max_runtime", None)

            if self._clock() - run_started >= self.startup_grace:
                healthy, detail = self.probe.check()
                if healthy:
                    if unhealthy_since is not None:
                        self.log.info("health endpoint answered again")
                    unhealthy_since = None
                else:
                    now = self._clock()
                    if unhealthy_since is None:
                        unhealthy_since = now
                        self.log.warning("health endpoint not answering: %s", detail)
                    elif now - unhealthy_since >= self.stall_timeout:
                        self.log.error(
                            "health endpoint silent for %.0fs, restarting the agent",
                            now - unhealthy_since,
                        )
                        return ("unhealthy", None)

            if self._wait(self.poll_interval):
                return ("stopped", None)

    def _stop_child(self, child: subprocess.Popen, graceful_wait: float = 20.0) -> None:
        if child.poll() is not None:
            return
        if os.name == "nt":
            try:
                child.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:  # noqa: BLE001 - the hard kill below is the real one
                pass
            try:
                child.wait(timeout=3)
                return
            except subprocess.TimeoutExpired:
                pass
            self.log.info("terminating pid %d (taskkill /T /F)", child.pid)
            subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"],
                           capture_output=True)
        else:
            # SIGTERM is handled by run.py's shutdown handler -> sessions close cleanly.
            child.terminate()
        try:
            child.wait(timeout=graceful_wait if os.name != "nt" else 10)
            return
        except subprocess.TimeoutExpired:
            pass
        self.log.warning("pid %d ignored the graceful stop, killing it", child.pid)
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"],
                           capture_output=True)
        else:
            child.kill()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.log.error("pid %d could not be killed", child.pid)

    # -- helpers -----------------------------------------------------------

    def _should_stop(self) -> bool:
        return bool(self._stop is not None and self._stop.is_set())

    def _wait(self, seconds: float) -> bool:
        """Sleep, waking early on stop. Returns True if a stop was requested."""
        if seconds <= 0:
            return self._should_stop()
        if self._stop is not None:
            return self._stop.wait(seconds)
        time.sleep(seconds)
        return False

    def _runtime_exceeded(self, started_at: float) -> bool:
        return self.max_runtime > 0 and (self._clock() - started_at) >= self.max_runtime

    def _setup_logging(self) -> None:
        self.log.setLevel(logging.INFO)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        rotate_if_large(self.log_path, 5 * 1024 * 1024)
        formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        if not any(isinstance(h, logging.FileHandler) for h in self.log.handlers):
            file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)
        if not any(getattr(h, "_supervisor_console", False) for h in self.log.handlers):
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            stream_handler._supervisor_console = True
            self.log.addHandler(stream_handler)
        self.log.propagate = False

    def _install_signal_handlers_(self) -> None:
        def handler(signum, frame):  # noqa: ARG001
            self.log.info("signal %s received, shutting down", signum)
            if self._stop:
                self._stop.set()

        for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
            sig = getattr(signal, name, None)
            if sig is not None:
                try:
                    signal.signal(sig, handler)
                except (ValueError, OSError):
                    pass

    def _acquire_pid_file(self) -> bool:
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            existing = int(self.pid_file.read_text(encoding="utf-8").strip() or 0)
        except (OSError, ValueError):
            existing = 0
        if existing and existing != os.getpid() and pid_alive(existing):
            self.log.error(
                "another supervisor is already running (pid %d, %s) - stop it first",
                existing, self.pid_file,
            )
            return False
        try:
            self.pid_file.write_text(str(os.getpid()), encoding="utf-8")
        except OSError as exc:
            self.log.warning("cannot write pid file %s: %s", self.pid_file, exc)
        return True

    def _release_pid_file(self) -> None:
        try:
            if self.pid_file.exists() and self.pid_file.read_text(encoding="utf-8").strip() == str(os.getpid()):
                self.pid_file.unlink()
        except OSError:
            pass


class _StopFlag:
    """Minimal stand-in for a stop event so tests need no signal machinery."""

    def __init__(self) -> None:
        import threading

        self._event = threading.Event()

    def set(self) -> None:
        self._event.set()

    def is_set(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._event.wait(timeout)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _port_from_args(child_args: Sequence[str]) -> Optional[int]:
    for i, token in enumerate(child_args):
        if token in ("--port", "-p") and i + 1 < len(child_args):
            try:
                return int(child_args[i + 1])
            except ValueError:
                return None
        if token.startswith("--port="):
            try:
                return int(token.split("=", 1)[1])
            except ValueError:
                return None
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keep the autonomous research agent alive.",
        epilog="Unknown arguments (best after '--') are passed unchanged to run.py, "
               "e.g. 'python supervisor.py -- --topic \"my topic\"'.",
    )
    parser.add_argument("--port", type=int, help="Dashboard port (default: DASHBOARD_PORT or 8080)")
    parser.add_argument("--model", "-m", help="Chat model override, forwarded to run.py")
    parser.add_argument("--health-url", help="Health endpoint (default: http://127.0.0.1:<port>/api/health)")
    parser.add_argument("--poll-interval", type=float, default=15.0, help="Health poll interval in seconds")
    parser.add_argument("--startup-grace", type=float, default=240.0,
                        help="Seconds a fresh child gets before health checks apply")
    parser.add_argument("--stall-timeout", type=float, default=180.0,
                        help="Seconds the health endpoint may stay silent before a restart")
    parser.add_argument("--initial-backoff", type=float, default=10.0, help="First restart delay in seconds")
    parser.add_argument("--max-backoff", type=float, default=300.0, help="Restart delay cap in seconds")
    parser.add_argument("--stable-after", type=float, default=600.0,
                        help="A run this long resets the backoff and the crash-loop window")
    parser.add_argument("--max-restarts-per-hour", type=int, default=6,
                        help="Give up after this many restarts within an hour (0 = never give up)")
    parser.add_argument("--max-runtime", type=float, default=0.0,
                        help="Stop after this many seconds (0 = run until stopped)")
    parser.add_argument("--restart-on-clean-exit", action="store_true",
                        help="Also restart when the child exits with code 0")
    parser.add_argument("--child-python", default=sys.executable, help="Python used for run.py")
    parser.add_argument("--log-file", type=Path, help="Supervisor log (default: data/supervisor.log)")
    parser.add_argument("--child-out", type=Path, help="Child stdout log")
    parser.add_argument("--child-err", type=Path, help="Child stderr log")
    parser.add_argument("--pid-file", type=Path, help="Single-instance lock (default: data/supervisor.pid)")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args, child_args = build_parser().parse_known_args(argv)
    # Unknown arguments belong to run.py (argparse keeps their original order),
    # so 'supervisor.py --topic X' works as well as 'supervisor.py -- --topic X'.
    child_args = list(child_args)
    if child_args and child_args[0] == "--":
        child_args = child_args[1:]

    port = args.port or _port_from_args(child_args) or int(os.environ.get("DASHBOARD_PORT", DEFAULT_PORT))
    if args.port and _port_from_args(child_args) is None:
        child_args += ["--port", str(port)]
    if args.model and "--model" not in child_args and "-m" not in child_args:
        child_args += ["--model", args.model]

    health_url = args.health_url or f"http://127.0.0.1:{port}/api/health"
    max_per_hour = args.max_restarts_per_hour
    policy = RestartPolicy(
        initial_delay=args.initial_backoff,
        max_delay=args.max_backoff,
        stable_after=args.stable_after,
        max_restarts_per_hour=max_per_hour,
    )
    if max_per_hour <= 0:
        policy = RestartPolicy(max_restarts_per_hour=10 ** 9,
                               initial_delay=args.initial_backoff,
                               max_delay=args.max_backoff,
                               stable_after=args.stable_after)

    supervisor = Supervisor(
        [args.child_python, str(PROJECT_ROOT / "run.py"), *child_args],
        health_url=health_url,
        policy=policy,
        startup_grace=args.startup_grace,
        stall_timeout=args.stall_timeout,
        poll_interval=args.poll_interval,
        max_runtime=args.max_runtime,
        restart_on_clean_exit=args.restart_on_clean_exit,
        log_path=args.log_file,
        child_out=args.child_out,
        child_err=args.child_err,
        pid_file=args.pid_file,
    )
    return supervisor.run()


if __name__ == "__main__":
    sys.exit(main())

"""Tests for the process supervisor (supervisor.py).

The unit tests cover the restart policy, the crash-loop window and the health
probe. The behaviour tests start a real child process and a real HTTP server on
an ephemeral port, so restart, hang detection and clean shutdown are exercised
the way the supervisor uses them.
"""

import logging
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from supervisor import (  # noqa: E402
    HealthProbe,
    RestartBudget,
    RestartPolicy,
    Supervisor,
    pid_alive,
)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


FAKE_CHILD = textwrap.dedent(
    '''
    """Stand-in for run.py: can crash, exit cleanly, serve /api/health or hang."""
    import sys
    import threading
    import time
    from http.server import BaseHTTPRequestHandler, HTTPServer

    mode, port = sys.argv[1], int(sys.argv[2])


    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b'{"status": "ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass


    if mode == "crash":
        sys.exit(1)
    if mode == "clean":
        sys.exit(0)

    server = HTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    if mode == "hang":
        # Answers for a moment, then goes silent while staying alive.
        time.sleep(0.5)
        server.shutdown()
        server.server_close()

    while True:
        time.sleep(0.5)
    '''
)


class TestRestartPolicy(unittest.TestCase):
    def test_delay_doubles_and_is_capped(self):
        policy = RestartPolicy(initial_delay=10, max_delay=300, multiplier=2)
        self.assertEqual([policy.delay(n) for n in range(1, 8)],
                         [10, 20, 40, 80, 160, 300, 300])

    def test_delay_rejects_zero_attempt(self):
        with self.assertRaises(ValueError):
            RestartPolicy().delay(0)


class TestRestartBudget(unittest.TestCase):
    def test_allows_up_to_limit_then_blocks(self):
        now = [0.0]
        budget = RestartBudget(max_per_hour=2, clock=lambda: now[0])
        self.assertTrue(budget.allow())
        budget.record()
        self.assertTrue(budget.allow())
        budget.record()
        self.assertFalse(budget.allow())
        self.assertEqual(budget.count(), 2)

    def test_old_restarts_leave_the_window(self):
        now = [0.0]
        budget = RestartBudget(max_per_hour=2, window=3600, clock=lambda: now[0])
        budget.record()
        budget.record()
        self.assertFalse(budget.allow())
        now[0] = 3601.0
        self.assertTrue(budget.allow())

    def test_reset_clears_the_window(self):
        budget = RestartBudget(max_per_hour=1, clock=lambda: 0.0)
        budget.record()
        self.assertFalse(budget.allow())
        budget.reset()
        self.assertTrue(budget.allow())


class TestHealthProbe(unittest.TestCase):
    def test_reports_healthy_endpoint(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import threading

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, *args):
                pass

        port = _free_port()
        server = HTTPServer(("127.0.0.1", port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            ok, detail = HealthProbe(f"http://127.0.0.1:{port}/api/health", timeout=2).check()
            self.assertTrue(ok, detail)
            self.assertIn("200", detail)
        finally:
            server.shutdown()
            server.server_close()

    def test_reports_dead_endpoint(self):
        ok, detail = HealthProbe(f"http://127.0.0.1:{_free_port()}/api/health", timeout=1).check()
        self.assertFalse(ok)
        self.assertTrue(detail)


class TestPidAlive(unittest.TestCase):
    def test_own_process_is_alive(self):
        import os

        self.assertTrue(pid_alive(os.getpid()))

    def test_finished_process_is_not_alive(self):
        finished = subprocess.Popen([sys.executable, "-c", "pass"])
        pid = finished.pid
        finished.wait(timeout=30)
        self.assertFalse(pid_alive(pid))


class SupervisorBehaviourTest(unittest.TestCase):
    """Drives Supervisor.run() with a real child process."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.child = self.dir / "fake_child.py"
        self.child.write_text(FAKE_CHILD, encoding="utf-8")
        self.port = _free_port()
        self.logger = logging.getLogger(f"supervisor-test-{id(self)}")
        self.logger.handlers = [logging.NullHandler()]
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.log_file = self.dir / "supervisor.log"

    def tearDown(self):
        # The supervisor keeps its log file open; Windows refuses to delete an
        # open file, so close the handlers before the temp dir goes away.
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)
        logging.Logger.manager.loggerDict.pop(self.logger.name, None)
        self._tmp.cleanup()

    def _make(self, mode, **overrides):
        options = dict(
            health_url=f"http://127.0.0.1:{self.port}/api/health",
            policy=RestartPolicy(initial_delay=0.05, max_delay=0.1, stable_after=60,
                                 max_restarts_per_hour=2),
            startup_grace=0.3,
            stall_timeout=0.8,
            poll_interval=0.15,
            probe_timeout=1.0,
            log_path=self.log_file,
            child_out=self.dir / "child.out.log",
            child_err=self.dir / "child.err.log",
            pid_file=self.dir / "supervisor.pid",
            install_signal_handlers=False,
            logger=self.logger,
        )
        options.update(overrides)
        return Supervisor([sys.executable, str(self.child), mode, str(self.port)], **options)

    def _logged(self) -> str:
        return self.log_file.read_text(encoding="utf-8") if self.log_file.exists() else ""

    def test_crashes_are_restarted_until_the_budget_is_spent(self):
        supervisor = self._make("crash")
        code = supervisor.run()

        self.assertEqual(code, 2, "supervisor should report the crash loop")
        self.assertEqual(supervisor.restart_count, 2)
        self.assertEqual(len(supervisor.runs), 3, "initial start plus two restarts")
        self.assertTrue(all(run["reason"] == "exited" and run["code"] != 0
                            for run in supervisor.runs))
        log = self._logged()
        self.assertIn("giving up", log)
        self.assertIn("restart #1", log)

    def test_clean_exit_ends_the_supervision(self):
        supervisor = self._make("clean")
        code = supervisor.run()

        self.assertEqual(code, 0)
        self.assertEqual(supervisor.restart_count, 0)
        self.assertEqual(len(supervisor.runs), 1)
        self.assertIn("child finished cleanly", self._logged())

    def test_clean_exit_can_be_restarted_on_request(self):
        supervisor = self._make("clean", restart_on_clean_exit=True,
                                policy=RestartPolicy(initial_delay=0.05, max_delay=0.1,
                                                     stable_after=60, max_restarts_per_hour=1))
        code = supervisor.run()

        self.assertEqual(code, 2)
        self.assertEqual(supervisor.restart_count, 1)

    def test_silent_process_is_restarted(self):
        supervisor = self._make("hang", policy=RestartPolicy(initial_delay=0.05, max_delay=0.1,
                                                             stable_after=60,
                                                             max_restarts_per_hour=1))
        started = time.monotonic()
        code = supervisor.run()
        elapsed = time.monotonic() - started

        self.assertEqual(code, 2)
        self.assertEqual(supervisor.restart_count, 1)
        self.assertEqual(supervisor.runs[0]["reason"], "unhealthy")
        self.assertLess(elapsed, 20.0)
        self.assertIn("health endpoint silent", self._logged())

    def test_healthy_child_is_stopped_after_max_runtime(self):
        supervisor = self._make("serve", max_runtime=1.2)
        started = time.monotonic()
        code = supervisor.run()
        elapsed = time.monotonic() - started

        self.assertEqual(code, 0)
        self.assertEqual(len(supervisor.runs), 1)
        self.assertEqual(supervisor.runs[0]["reason"], "max_runtime")
        self.assertLess(elapsed, 15.0)
        pid = supervisor.runs[0]["pid"]
        self.assertFalse(pid_alive(pid), "the child must not survive the supervisor")

    def test_second_instance_refuses_to_start(self):
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(other.kill)
        (self.dir / "supervisor.pid").write_text(str(other.pid), encoding="utf-8")
        supervisor = self._make("serve")
        code = supervisor.run()

        self.assertEqual(code, 1)
        self.assertEqual(supervisor.runs, [], "no child may be started")
        self.assertIn("already running", self._logged())
        self.assertEqual((self.dir / "supervisor.pid").read_text(encoding="utf-8").strip(),
                         str(other.pid), "a foreign pid file must be left alone")


if __name__ == "__main__":
    unittest.main()

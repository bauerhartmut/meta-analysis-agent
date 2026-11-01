"""One writer per corpus, and a dashboard port that is really ours.

Four run.py processes on one database looked like one busy client to every
search provider, so every query came back 429 while the run blamed its own
queries. These tests pin the two guards that make that impossible: a pid lock
keyed on the database, and a refused start when the port already answers.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.instance_guard import (
    InstanceLock, dashboard_port_in_use, lock_path_for_database,
)


class TestLockPath(unittest.TestCase):
    def test_lock_sits_next_to_the_database(self):
        path = lock_path_for_database("data/research-topic-abc.db")
        self.assertEqual(path.name, "research-topic-abc.pid")
        self.assertEqual(path.parent.name, "data")

    def test_a_plain_database_name_works_too(self):
        self.assertEqual(lock_path_for_database("").name, "research.pid")


class TestInstanceLock(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="instance_guard_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.path = Path(self.tmp) / "research.pid"

    def test_a_second_writer_is_refused(self):
        first = InstanceLock(self.path, pid=1111)
        self.assertTrue(first.acquire())
        self.addCleanup(first.release)

        second = InstanceLock(self.path, pid=2222)
        with mock.patch("research_agent.instance_guard.pid_alive", return_value=True):
            self.assertFalse(second.acquire())

        self.assertEqual(second.held_by, 1111)
        self.assertEqual(self.path.read_text(encoding="utf-8").strip(), "1111")

    def test_a_stale_lock_is_taken_over(self):
        self.path.write_text("999999", encoding="utf-8")
        lock = InstanceLock(self.path, pid=os.getpid())

        with mock.patch("research_agent.instance_guard.pid_alive", return_value=False):
            self.assertTrue(lock.acquire())

        self.assertTrue(lock.acquire())
        self.assertEqual(self.path.read_text(encoding="utf-8").strip(), str(os.getpid()))

    def test_release_removes_only_our_own_lock(self):
        lock = InstanceLock(self.path, pid=os.getpid())
        lock.acquire()
        lock.release()
        self.assertFalse(self.path.exists())

        self.path.write_text("1234", encoding="utf-8")
        other = InstanceLock(self.path, pid=os.getpid())
        other._acquired = True  # pretend, but the file names someone else
        other.release()
        self.assertTrue(self.path.exists(), "a foreign lock must survive")

    def test_an_unwritable_lock_does_not_stop_the_run(self):
        # A guard is a safety net, not a precondition: a read-only data dir must
        # not prevent research from happening at all.
        blocked = Path(self.tmp) / "missing" / "x" / "research.pid"
        lock = InstanceLock(blocked, pid=os.getpid())
        with mock.patch.object(Path, "write_text", side_effect=OSError("denied")):
            self.assertTrue(lock.acquire())


class TestPortCheck(unittest.TestCase):
    def test_a_free_port_is_reported_free(self):
        self.assertFalse(dashboard_port_in_use("127.0.0.1", 0))

    def test_a_taken_port_is_reported_taken(self):
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            port = server.getsockname()[1]
            self.assertTrue(dashboard_port_in_use("0.0.0.0", port))


if __name__ == "__main__":
    unittest.main()

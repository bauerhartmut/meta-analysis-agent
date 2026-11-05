"""Windows-Job-Object-Sandbox (Claude-Vorschlag 2): echte Grenzen am
Simulations-Kindprozess.

Geprueft wird am ECHTEN Kindprozess (nicht gemockt), denn der Wert dieser
Schicht liegt gerade in der OS-EBENE:
1. Ein normaler Kindprozess laeuft mit angehaengtem Job unbeschaedigt durch.
2. Ein Speicherfresser wird vom Job-LIMIT (SIM_MEM_MB) beendet, bevor er
   den Host belastet.
3. Auf Nicht-Windows bleibt die Schicht ein ehrlicher No-op (Rueckgabe
   False), damit die Tests dort nicht fake-gruen laufen.
"""

import os
import subprocess
import sys
import unittest

from research_agent.experiments.win_job import (
    IS_WINDOWS, attach_job_limits, create_job,
)

_PY = sys.executable


@unittest.skipUnless(not IS_WINDOWS, "nur auf Nicht-Windows relevant")
class TestNoopAusserhalbWindows(unittest.TestCase):
    def test_create_job_ist_none(self):
        self.assertIsNone(create_job())

    def test_attach_ist_false(self):
        child = subprocess.Popen([_PY, "-c", "print('x')"],
                                 stdout=subprocess.DEVNULL)
        try:
            self.assertFalse(attach_job_limits(child))
        finally:
            child.kill()
            child.wait()


@unittest.skipUnless(IS_WINDOWS, "nur auf Windows ausfuehrbar")
class TestJobGrenzen(unittest.TestCase):
    def test_normaler_prozess_laeuft_durch(self):
        child = subprocess.Popen(
            [_PY, "-c", "print('ok')"], stdout=subprocess.PIPE, text=True)
        attached = attach_job_limits(child, memory_mb=256)
        self.assertTrue(attached)
        out, _ = child.communicate(timeout=20)
        self.assertEqual((out or "").strip(), "ok")
        self.assertEqual(child.returncode, 0)

    def test_speicherfresser_wird_vom_limit_gestoppt(self):
        child = subprocess.Popen(
            [_PY, "-c", "x = bytearray(400 * 1024 * 1024);"
                        " import time; time.sleep(30)"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        attach_job_limits(child, memory_mb=128)
        # Das Limit kuendigt das Kind, bevor die 400 MB voll saugen:
        # returncode != 0 und deutlich unter den 30 s Schlaf.
        out, err = child.communicate(timeout=45)
        self.assertNotEqual(child.returncode, 0,
                            "Kind lief gegen das Speicherlimit durch")


if __name__ == "__main__":
    unittest.main()

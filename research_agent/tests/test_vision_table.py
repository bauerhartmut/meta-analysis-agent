"""Vision-Tabellenlesung (Sprint 29): Der gerasterte Seitenbild wird vom
TUDaGPT-Vision-Modell gelesen; Doppelleitung makes disagreements disputed
instead of averaged. Tests use the table fixture only - no API calls."""

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.research.vision_table import (
    crop_bounds,
    png_bytes,
    parse_vision_rows,
    rows_equal,
    compare_double_read,
    VisionTableReader,
)

FIXTURE_PDF = Path(__file__).parent / "assets" / "table_fixture.pdf"


class TestRender(unittest.TestCase):
    def test_fixture_renders_to_png(self):
        pages = None
        try:
            from research_agent.research.vision_table import render_pdf_pages
            pages = render_pdf_pages(str(FIXTURE_PDF))
        except ImportError:
            self.skipTest("pypdfium2 nicht installiert")
        self.assertTrue(pages)
        idx, data = pages[0]
        self.assertEqual(idx, 0)
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertGreater(len(data), 10_000)


class TestPngEncoder(unittest.TestCase):
    def test_png_bytes_shape(self):
        import numpy as np
        arr = np.zeros((4, 6, 3), dtype=np.uint8)
        data = png_bytes(arr)
        # PNG-Aufbau: 8 Signatur + 4 Laenge + 4 'IHDR' + 13 Daten;
        # Breite/Hoehe liegen deshalb bei Byte 16..24.
        w = int.from_bytes(data[16:20], "big")
        h = int.from_bytes(data[20:24], "big")
        self.assertEqual((w, h), (6, 4))


class TestParse(unittest.TestCase):
    def test_probe_output_with_duplicated_keys_keeps_both_rows(self):
        # Ausschnitt aus dem echten Probeaufruf: BEIDE Zeilen hängen in EINEM
        # Objekt; ein naiver json.loads verlöre die erste still.
        text = ('{"rows": [{"label": "Simple RT", "effect": -22.3, "se": 6.2,'
                ' "ci_low": -34.4, "ci_high": -10.2, "bbox_row": [110, 300, 888, 340],'
                ' "label": "Choice RT", "effect": -14.1, "se": 5.0,'
                ' "ci_low": -23.9, "ci_high": -4.3, "bbox_row": [110, 340, 888, 380]}]}')
        rows = parse_vision_rows(text)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["label"], "Simple RT")
        self.assertEqual(rows[0]["effect"], -22.3)
        self.assertEqual(rows[0]["se"], 6.2)
        self.assertEqual(rows[1]["label"], "Choice RT")
        self.assertEqual(rows[1]["effect"], -14.1)
        self.assertEqual(rows[1]["bbox_row"], [110, 340, 888, 380])

    def test_null_fields_stay_none(self):
        text = ('{"rows": [{"label": "Noisy", "effect": -1.0, "se": null,'
                '"ci_low": null, "ci_high": null, "bbox_row": [1,2,3,4]}]}')
        rows = parse_vision_rows(text)
        self.assertEqual(rows[0]["se"], None)
        self.assertEqual(rows[0]["ci_low"], None)

    def test_gibberish_yields_no_rows(self):
        self.assertEqual(parse_vision_rows("Kein JSON hier."), [])


class TestDoubleRead(unittest.TestCase):
    def test_agreeing_rows_are_not_disputed(self):
        rows = [{"label": "S", "effect": -22.3, "se": 6.2,
                 "ci_low": -34.4, "ci_high": -10.2}]
        confirmed, counts = compare_double_read(rows, [{"label": "S", "effect": -22.3,
                                                        "se": 6.2, "ci_low": -34.4,
                                                        "ci_high": -10.2}])
        self.assertEqual(len(confirmed), 1)
        self.assertFalse(confirmed[0]["_disputed"])
        self.assertFalse(any(counts))

    def test_off_by_one_digit_is_disputed_never_averaged(self):
        rows = [{"label": "S", "effect": -22.3, "se": 6.2,
                 "ci_low": -34.4, "ci_high": -10.2}]
        other = [{"label": "S", "effect": -22.8, "se": 6.2,
                  "ci_low": -34.4, "ci_high": -10.2}]
        confirmed, counts = compare_double_read(rows, other)
        self.assertTrue(confirmed[0]["_disputed"])
        self.assertTrue(any(counts))

    def test_different_row_counts_kill_the_page(self):
        # Zeilen MIT Zahlen: ungleiche Anzahl zwischen den beiden Lesungen
        # killt die ganze Seite (nichts wird paarenweise gemittelt).
        a = [{"label": "a", "effect": 1.0, "se": 0.1, "ci_low": 0.8, "ci_high": 1.2}]
        confirmed, counts = compare_double_read(a, [])
        self.assertEqual(confirmed, [])
        self.assertEqual(counts, [1])

    def test_header_rows_without_numbers_are_dropped(self):
        # Aus dem Probe: Kopfwörter wie 'Caffeine'/'Placebo' landen als leere
        # Zeilen ohne jegliche Zahl - sie fallen weg, werden nicht disputed.
        a = [{"label": "Caffeine"}, {"label": "Simple RT", "effect": -22.3,
                                     "se": 6.2, "ci_low": -34.4, "ci_high": -10.2}]
        b = [{"label": "Caffeine"}, {"label": "Simple RT", "effect": -22.3,
                                     "se": 6.2, "ci_low": -34.4, "ci_high": -10.2}]
        confirmed, counts = compare_double_read(a, b)
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0]["label"], "Simple RT")
        self.assertFalse(confirmed[0]["_disputed"])


class TestBounds(unittest.TestCase):
    def test_full_image_bbox_maps_to_full_frame(self):
        self.assertEqual(crop_bounds([0, 0, 1000, 1000], 200, 100), (0, 0, 200, 100))

    def test_partial_bbox_with_pad(self):
        x1, y1, x2, y2 = crop_bounds([100, 200, 300, 400], 1000, 1000)
        self.assertLessEqual(x1, 100)
        self.assertGreaterEqual(x2, 300)
        self.assertTrue(0 <= x1 <= x2 <= 1000)


class FakeResponse:
    def __init__(self, status=200, payload=None, text=""):
        self.status = status
        self._payload = payload
        self._text = text

    async def json(self):
        return self._payload

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    def __init__(self, responses):
        self._responses = responses
        self.calls = 0

    def post(self, *a, **kw):
        r = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return r

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class TestClientFallback(unittest.TestCase):
    def _reader(self, responses):
        class CfgReader(VisionTableReader):
            def __init__(self):
                self._session = None
                self._base = "http://fake"
                self._key = "x"  # Testsnutzung: nicht öffentlich
                self._model = "fake-model"
                self._max_tokens = 100
        r = CfgReader()
        r._session = FakeSession(responses)
        return r

    def _patch_client_session(self, reader, responses):
        import research_agent.research.vision_table as vt
        orig = vt.aiohttp.ClientSession
        vt.aiohttp.ClientSession = lambda *a, **kw: FakeSession(responses)
        self.addCleanup(setattr, vt.aiohttp, "ClientSession", orig)

    def test_http_error_gives_no_rows_not_crash(self):
        reader = self._reader([FakeResponse(status=401, text="unauthorized")])
        self._patch_client_session(reader, [FakeResponse(status=401, text="unauthorized")])
        rows = asyncio.run(reader.read_once(b"png"))
        self.assertEqual(rows, [])

    def test_http_200_with_rows(self):
        content = ('{"rows": [{"label": "S", "effect": -22.3, "se": 6.2, '
                   '"ci_low": -34.4, "ci_high": -10.2, "bbox_row": [1,2,3,4]}]}')
        resp = FakeResponse(
            payload={"choices": [{"message": {"content": content}}]})
        reader = self._reader([resp])
        self._patch_client_session(reader, [resp])
        rows = asyncio.run(reader.read_once(b"png"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["effect"], -22.3)


if __name__ == "__main__":
    unittest.main()

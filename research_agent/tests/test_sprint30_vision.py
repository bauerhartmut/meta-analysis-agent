"""Sprint 30: Verbatim-Vertrag fuer Bild-Evidenz (vision_read).

Die Bildlesung wird nicht textverifiziert (kein Textzitat-Span) - sie hat
eigene deterministische Regeln:

1. Der Zeilenvergleich zwischen den beiden Lesungen laeuft ueber die
   DEFINIERTE Normalisierung (Unicode-Minus, Dezimalkomma, Whitespace/±)
   und NIE mit numerischer Toleranz: 0,58 vs 0,53 bleibt disputed.
2. Pooling nimmt eine vision_read-Zeile nur bei vision_status == "verified"
   an (dieselbe Regel wie im Pooling - Verteidigung in der Tiefe).
3. Die Validierungsschicht behandelt vision-Zeilen NICHT als sinnlos
   "unbelegt", sondern prueft die Statusregeln; jede poolbare Zeile ohne
   verified ist ein Blocker.

Nie mittels, nie still korrigiert - weder im Vergleich noch beim Pooling.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.research.vision_table import (
    PROMPT_VERSION,
    compare_double_read,
    normalise_number_text,
    rows_equal,
    VisionTableReader,
)
from research_agent.meta.pooling import standardize
from research_agent.meta import validation as _validation
from research_agent.orchestrator import ResearchOrchestrator


def _row(effect=None, se=None, ci_low=-0.2, ci_high=0.8, label="row"):
    """Handgebaute Zeile OHNE raw_*-Felder (Rueckzugs-Pfad: strikter
    numerischer Vergleich). Jede Zahl ist LESEN belegt - unlesbare Felder
    (None) machen die Zeile disputed, auch wenn beide Passes None
    lesen."""
    return {"label": label, "effect": effect, "se": se,
            "ci_low": ci_low, "ci_high": ci_high}


def _row_raw(raw_effect, raw_match, effect=0.53, se=0.1, label="row"):
    """Zeile MIT Rohlesung (Modell-Pfad: stringvergleich nach Regel).
    Die CI-Felder bleiben beides gleich gelesen (hier konstant), damit der
    Fall den Zeilenvergleich testet und nicht die Halblesung."""
    d = {"label": label, "effect": effect, "se": se, "ci_low": -0.2,
         "ci_high": 0.8, "raw_effect": raw_effect, "raw_se": raw_match,
         "raw_ci_low": "-0,2", "raw_ci_high": "0,8"}
    return d


class TestNormalisierung(unittest.TestCase):
    def test_unicode_minus_wird_ascii_minus(self):
        self.assertEqual(normalise_number_text("\u22120.53"), "-0.53")

    def test_dezimalkomma_wird_punkt(self):
        self.assertEqual(normalise_number_text("0,53"), "0.53")

    def test_whitespace_vereinzelt_und_pm_ohne_leerzeichen(self):
        self.assertEqual(normalise_number_text("  0.53  ±  0.1  "), "0.53±0.1")

    def test_nie_numerische_toleranz(self):
        # 0,53 vs 0,58: nach Regel UNGLEICH - eine genuine Ziffern-
        # verwechslung muss disputed bleiben, nicht gunstig runden.
        self.assertNotEqual(normalise_number_text("0,53"),
                            normalise_number_text("0,58"))


class TestStringbasierterVergleich(unittest.TestCase):
    def test_gleiche_zahl_andere_schreibweise_ist_verified(self):
        a = _row_raw("0,53", "0,1")
        b = _row_raw("0.53", "0.1")
        self.assertTrue(rows_equal(a, b))

    def test_unicode_minus_bindestrich_variante_ist_verified(self):
        a = _row_raw("\u22120.53", "0,1")
        b = _row_raw("-0.53", "0.1")
        self.assertTrue(rows_equal(a, b))

    def test_ziffernverwechslung_bleibt_disputed(self):
        a = _row_raw("0,58", "0,1")
        b = _row_raw("0,53", "0,1")
        self.assertFalse(rows_equal(a, b))

    def test_pflichtig_fehlende_zeichenkette_ist_ungleich(self):
        a = _row_raw("-.53", "0,1")
        b = _row_raw("-0.53", "0,1")
        self.assertFalse(rows_equal(a, b))

    def test_halbgelesene_zeile_bleibt_disputed(self):
        # Halbgelesen = der Pass hat das Feld NICHT gelesen (Wert und
        # Rohlesung beide fehlend). Diese Zeile ist disputed, auch wenn
        # der andere Pass die Zahl gelesen hat.
        a = _row_raw("0,53", "0,1")
        a["se"] = None
        a["raw_se"] = None
        b = _row_raw("0,53", "0,1")
        self.assertFalse(rows_equal(a, b))

    def test_beide_passes_delete_dasselbe_feld_ist_disputed(self):
        # Sprint 29-Regel bleibt: halbgelesen bleibt disputed, auch wenn
        # BEIDE dasselbe Feld verloren haben (nichts wird still ausgelassen).
        a = _row_raw("0,53", "0,1")
        b = _row_raw("0,53", "0,1")
        a["ci_low"] = None
        b["ci_low"] = None
        self.assertFalse(rows_equal(a, b))

    def test_handgebaute_zeilen_strikt_numerisch(self):
        # Ohne raw_*-Felder: Rueckzugs-Pfalz, strikte Float-Gleichheit.
        self.assertTrue(rows_equal(_row(0.53, 0.1), _row(0.53, 0.1)))
        self.assertFalse(rows_equal(_row(0.58, 0.1), _row(0.53, 0.1)))


class TestStatusProZeile(unittest.TestCase):
    def test_compare_markiert_verified_und_disputed(self):
        a = [_row_raw("0,53", "0,1", label="a"),
             _row_raw("0,58", "0,1", label="b")]
        b = [_row_raw("0.53", "0.1", label="a"),
             _row_raw("0.53", "0.1", label="b")]
        rows, counts = compare_double_read(a, b)
        self.assertEqual(rows[0].get("_vision_status"), "verified")
        self.assertEqual(rows[1].get("_vision_status"), "disputed")
        self.assertTrue(rows[1].get("_disputed"))


class _FakeReader:
    """Fuer read_table_evidence: liefert vorgegebene Lesungen."""

    def __init__(self, rows, model_name="fake-vision-model"):
        self.model_name = model_name
        self._rows = rows

    async def read_double(self, image_png):
        rows, counts = compare_double_read(
            [dict(r) for r in self._rows[0]],
            [dict(r) for r in self._rows[1]])
        return rows, counts


class TestEvidenzAggregat(unittest.TestCase):
    def _pdf(self, tmp=None):
        # Eine "PDF" braucht nur Bytes; pdf_hash ist ein sha256 aller Bytes.
        return os.path.join(os.path.dirname(__file__), "test_sprint30_vision.py")

    def test_verified_aggregat_traegt_belegkette(self):
        import asyncio
        reader = _FakeReader([[_row_raw("0,53", "0,1")],
                              [_row_raw("0.53", "0.1")]])
        pdf = self._pdf()
        png = b"\x89PNG-fake-crop"
        ev = asyncio.get_event_loop_policy().new_event_loop()
        result = ev.run_until_complete(
            _ev_read(pdf, 2, png, reader))
        ev.close()
        self.assertEqual(result["evidence_kind"], "vision_read")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["model"], reader.model_name)
        self.assertIn("pdf_hash", result)
        self.assertIn("crop_hash", result)
        self.assertEqual(result["prompt_version"], PROMPT_VERSION)

    def test_disputed_aggregat_ist_disputed(self):
        import asyncio
        reader = _FakeReader([[_row_raw("0,58", "0,1")],
                              [_row_raw("0,53", "0,1")]])
        png = b"\x89PNG-fake-crop"
        ev = asyncio.get_event_loop_policy().new_event_loop()
        result = ev.run_until_complete(
            _ev_read(self._pdf(), 0, png, reader))
        ev.close()
        self.assertEqual(result["status"], "disputed")

    def test_leere_lesung_ist_empty_nicht_verified(self):
        import asyncio

        class _Empty:
            model_name = "fake"
            async def read_double(self, image_png):
                return [], []
        png = b"\x89PNG-fake-crop"
        ev = asyncio.get_event_loop_policy().new_event_loop()
        result = ev.run_until_complete(_ev_read(self._pdf(), 0, png, _Empty()))
        ev.close()
        self.assertEqual(result["status"], "empty")


async def _ev_read(pdf, page, png, reader):
    from research_agent.research.vision_table import read_table_evidence
    return await read_table_evidence(pdf, page, png, reader)


from types import SimpleNamespace


def _textlayer_row(disputed=False, rejection="", se=None, ci_low=None,
                   ci_high=None):
    """Text-Layer-Zeile als Attr-Objekt - die Extraktion liefert Objekte
    (StudyEffect), nicht Dicts; SimpleNamespace reicht fuer den Trigger."""
    return SimpleNamespace(
        disputed=disputed, rejection_reason=rejection,
        se=se, ci_low=ci_low, ci_high=ci_high)


class TestVisionFallbackTrigger(unittest.TestCase):
    """Netzlauffund 2026-11-05: der Fallback lief nur bei `not rows`.

    Der Melatonin-Netzlauf 2 produzierte Zeilen ohne Effektwert und ohne
    SE/CI - und die Bildlesung blieb im ganzen Lauf bei 0 Aufrufen, obwohl
    VISION_TABLE_ENABLED an war. Diese Faelle pinnen den erweiterten
    Trigger (_vision_fallback_due).
    """

    def _due(self, rows, pdf="/a/b.pdf", enabled=True):
        return ResearchOrchestrator._vision_fallback_due(rows, pdf, enabled)

    def test_rows_leer_durch_pdf_fallt_fallback(self):
        self.assertTrue(self._due([]))
        self.assertTrue(self._due(None))

    def test_nur_effektlose_zeilen_verlangen_fallback(self):
        rows = [_textlayer_row()] * 3
        self.assertEqual(ResearchOrchestrator._count_poolable(rows), 0)
        self.assertTrue(self._due(rows))

    def test_eine_poolbare_zeile_verhindert_fallback(self):
        rows = [_textlayer_row(), _textlayer_row(se=0.1)]
        self.assertEqual(ResearchOrchestrator._count_poolable(rows), 1)
        self.assertFalse(self._due(rows))

    def test_ci_traegt_als_poolbar_ohne_se(self):
        rows = [_textlayer_row(ci_low=-0.2, ci_high=0.8)]
        self.assertEqual(ResearchOrchestrator._count_poolable(rows), 1)
        self.assertFalse(self._due(rows))

    def test_disputed_und_rejection_zaehlen_nicht_als_poolbar(self):
        rows = [_textlayer_row(disputed=True, se=0.1)]
        self.assertEqual(ResearchOrchestrator._count_poolable(rows), 0)
        rows2 = [_textlayer_row(rejection="kein Effektwert gelesen", se=0.1)]
        self.assertEqual(ResearchOrchestrator._count_poolable(rows2), 0)
        self.assertTrue(self._due(rows))
        self.assertTrue(self._due(rows2))

    def test_ohne_pdf_oder_ohne_enabled_kein_fallback(self):
        self.assertFalse(self._due([], pdf=""))
        self.assertFalse(self._due([], enabled=False))
        self.assertFalse(self._due([_textlayer_row(se=0.1)], pdf=""))


def _vision_row(status, **kw):
    d = {"id": "r1", "label": "x", "effect_type": "smd", "effect": 0.53,
         "se": 0.1, "disputed": 0, "rejection_reason": "",
         "quote_start": -1, "quote_end": -1, "n": 50,
         "evidence_kind": "vision_read", "vision_status": status,
         "vision_meta": "{}", "source_text_id": ""}
    d.update(kw)
    return d


class TestPoolingGate(unittest.TestCase):
    def test_vision_verified_ist_poolbar_ohne_text_span(self):
        est, se, scale, reason = standardize(_vision_row("verified"))
        self.assertIsNotNone(est)
        self.assertEqual(reason, "")

    def test_vision_disputed_ist_nicht_poolbar(self):
        est, se, scale, reason = standardize(_vision_row("disputed"))
        self.assertIsNone(est)
        self.assertIn("nicht verifiziert", reason)

    def test_vision_ohne_status_ist_nicht_poolbar(self):
        est, se, scale, reason = standardize(_vision_row(""))
        self.assertIsNone(est)
        self.assertIn("nicht verifiziert", reason)

    def test_text_zeile_bleibt_unveraendert(self):
        d = {"id": "r1", "label": "x", "effect_type": "smd", "effect": 0.53,
             "se": 0.1, "disputed": 0, "rejection_reason": "",
             "quote_start": 5, "quote_end": 25, "n": 50,
             "evidence_kind": "text_verbatim", "vision_status": "",
             "vision_meta": "{}", "source_text_id": "t"}
        est, se, scale, reason = standardize(d)
        self.assertIsNotNone(est)


class _VisionDb:
    """Mini-Double: liefert die Zeilen, die die Regeln brauchen."""

    def __init__(self, rows):
        self._rows = rows

    def count_study_effects(self):
        return len(self._rows)

    def get_study_effects(self, limit=0):
        return list(self._rows)

    def read_source_text(self, text_id):
        return ""


class TestValidierungsregeln(unittest.TestCase):
    def test_vision_ohne_verified_und_poolbar_ist_blocker(self):
        db = _VisionDb([_vision_row("disputed")])
        result = _validation.run_validation(db)
        rules = [b["rule"] for b in result["blockers"]]
        self.assertIn("vision_poolable_without_verified", rules)

    def test_vision_verified_macht_keinen_blocker(self):
        db = _VisionDb([_vision_row("verified")])
        result = _validation.run_validation(db)
        rules = [b["rule"] for b in result["blockers"]]
        self.assertNotIn("vision_poolable_without_verified", rules)
        self.assertNotIn("poolable_effect_without_verbatim_quote", rules)
        self.assertEqual(int(result["checks"]["effect_quotes"]
                             .get("vision_rows")), 1)

    def test_vision_ohne_status_gibt_warnung(self):
        db = _VisionDb([_vision_row("")])
        result = _validation.run_validation(db)
        wrules = [w["rule"] for w in result["warnings"]]
        self.assertIn("vision_row_without_status", wrules)
        # equals nicht poolbar -> Blocker unrichtig, Warnung da
        brules = [b["rule"] for b in result["blockers"]]
        self.assertIn("vision_poolable_without_verified", brules)

    def test_text_verbatim_bleibt_unveraendert_geprueft(self):
        d = {"id": "r2", "label": "x", "effect_type": "smd", "effect": 0.53,
             "se": 0.1, "disputed": 0, "rejection_reason": "",
             "quote_start": -1, "quote_end": -1, "n": 50,
             "evidence_kind": "text_verbatim", "vision_status": "",
             "vision_meta": "{}", "source_text_id": ""}
        db = _VisionDb([d])
        result = _validation.run_validation(db)
        rules = [b["rule"] for b in result["blockers"]]
        self.assertIn("poolable_effect_without_verbatim_quote", rules)


if __name__ == "__main__":
    unittest.main()

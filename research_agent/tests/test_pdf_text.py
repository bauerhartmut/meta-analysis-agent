"""Tests fuer die PDF-Textnormalisierung (Silbentrennung, Spalten)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "pdf_text",
    Path(__file__).resolve().parents[2] / "research_agent" / "meta" / "pdf_text.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

NL = chr(10)


def test_silbentrennung_wird_aufgeloest():
    text = "sleep onset la-" + NL + "tency was 18.3 min"
    assert _MOD.dehyphenate(text) == "sleep onset latency was 18.3 min"


def test_weicher_bindestrich_verschwindet():
    assert _MOD.dehyphenate("la" + chr(173) + "tency") == "latency"


def test_bindestrich_vor_grossbuchstabe_bleibt():
    text = "Melatonin-" + NL + "RCT"
    assert _MOD.dehyphenate(text) == text


def test_zwei_spalten_in_einer_zeile_werden_getrennt():
    text = ("Sleep onset latency was 18.3 min in the first group.        "
            "Secondary outcomes were similar across both groups.")
    parts = _MOD.split_columns(text).split(NL)
    assert len(parts) == 2
    assert parts[0].startswith("Sleep onset")
    assert parts[1].startswith("Secondary")


def test_tabellenzeile_bleibt_zusammen():
    row = "SOL (min)      18.3        27.9"
    assert _MOD.split_columns(row) == row


def test_normalize_loest_bindestrich_und_glueckt():
    text = "Sleep onset la-" + NL + "tency was" + NL + "18.3 +- 7.2 min."
    assert _MOD.normalize(text) == "Sleep onset latency was 18.3 +- 7.2 min."


def test_normalize_ergibt_lesbaren_kandidaten():
    from research_agent.meta.arm_text import text_arm_candidates

    text = _MOD.normalize(
        "Sleep onset la-" + NL
        + "tency was 18.3 +- 7.2 min in the melatonin group (n = 20) and 27.9 +- 8.1"
        + " min in" + NL + "the placebo group (n = 20).")
    assert len(text_arm_candidates(text)) == 1

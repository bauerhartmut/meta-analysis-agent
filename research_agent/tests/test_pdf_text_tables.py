"""Tests: Zahlenzeilen und Tabellen ueberleben die Normalisierung."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "pdf_text",
    Path(__file__).resolve().parents[2] / "research_agent" / "meta" / "pdf_text.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

NL = chr(10)


def test_zahlenzeilen_werden_nicht_verklebt():
    rows = "0.00 1.00 2.00" + NL + "12.5 13.5 14.5"
    assert _MOD.flatten_prose(rows).count(NL) == 1


def test_prosazeile_wird_weiterhin_verklebt():
    text = "Sleep onset latency was" + NL + "18.3 +- 7.2 min."
    assert _MOD.flatten_prose(text).count(NL) == 0


def test_tabellenbereich_bleibt_verbatim(monkeypatch):
    text = ("Results were similar across groups." + NL
            + "0.00 1.00 2.00" + NL + "12.5 13.5 14.5" + NL
            + "The next paragraph starts here.")
    start, end = text.index("0.00"), text.index("The next")
    monkeypatch.setattr(_MOD, "_table_spans", lambda t: [(start, end)])
    out = _MOD.normalize(text)
    assert "0.00 1.00 2.00" + NL + "12.5 13.5 14.5" in out


def test_zahlen_bleiben_erhalten(monkeypatch):
    text = ("Results were similar across groups." + NL
            + "0.00 1.00 2.00" + NL + "12.5 13.5 14.5" + NL
            + "The next paragraph starts here.")
    start, end = text.index("0.00"), text.index("The next")
    monkeypatch.setattr(_MOD, "_table_spans", lambda t: [(start, end)])

    def numbers(blob):
        return [t for t in blob.replace(",", " ").split()
                if t.strip("().;").replace(".", "").isdigit()]

    assert numbers(text) == numbers(_MOD.normalize(text))


def test_ueberlappende_bereiche_werden_zusammengefasst(monkeypatch):
    import types
    text = "A sentence here." + NL + "1.0 2.0" + NL + "3.0 4.0"
    start, mid, end = text.index("1.0"), text.index("3.0"), len(text)
    fake = [types.SimpleNamespace(start=start, end=mid + 2),
            types.SimpleNamespace(start=mid, end=end)]
    monkeypatch.setattr(
        "research_agent.research.table_extractor.find_table_blocks", lambda t: fake)
    assert _MOD._table_spans(text) == [(start, end)]

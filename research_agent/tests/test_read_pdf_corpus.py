"""Tests fuer die PDF-Kette: Zeilenzerlegung und SOL-Erkennung."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "read_pdf_corpus",
    Path(__file__).resolve().parents[2] / "scripts" / "read_pdf_corpus.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def test_pipe_block_wird_zerlegt():
    header, rows = _MOD.rows_from_block(
        "Outcome | Melatonin | Placebo\nSOL (min) | 18.3 | 27.9")
    assert header == ["Outcome", "Melatonin", "Placebo"]
    assert rows == [["SOL (min)", "18.3", "27.9"]]


def test_spaltenblock_wird_zerlegt():
    header, rows = _MOD.rows_from_block(
        "Outcome    Melatonin    Placebo\nSOL (min)    18.3    27.9")
    assert header == ["Outcome", "Melatonin", "Placebo"]
    assert rows[0][0] == "SOL (min)"


def test_zu_kurzer_block_gibt_nichts():
    assert _MOD.rows_from_block("nur eine Zeile") == ([], [])


def test_sol_wird_erkannt():
    assert _MOD.is_sol("Sleep onset latency (min)")
    assert _MOD.is_sol("SOL, minutes")
    assert not _MOD.is_sol("Total sleep time")


def test_fliesstextsatz_ergibt_speicherbaren_kandidaten():
    """Ende-zu-Ende: PDF-typischer Satz -> Kandidat -> Store."""
    from research_agent.database import Database
    from research_agent.meta.arm_text import store_text_arm_effects, text_arm_candidates

    text = ("Sleep onset latency was 18.3 +- 7.2 min in the melatonin group (n = 20) "
            "and 27.9 +- 8.1 min in the placebo group (n = 20).")
    candidates = text_arm_candidates(text)
    assert candidates and candidates[0]["ok"]

    db = Database(":memory:")
    row = db.save_source_text("pdf:test", text, kind="pdf", origin_url="test.pdf")
    stored, rejected = store_text_arm_effects(
        db, "pdf:test", (row or {}).get("id", ""), text, candidates)
    assert len(stored) == 1
    assert not rejected
    assert stored[0]["effect"] < 0  # Melatonin senkt die Einschaflatenz

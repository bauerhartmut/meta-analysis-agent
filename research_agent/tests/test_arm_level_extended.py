"""Tests fuer die zwei Erweiterungen am Arm-Leser aus dem Q2-Durchgang.

Beide Faelle stammen aus echten Tabellen des Korpus: das Klammer-SD mit
Etikett in der Caption (PMC3489506) und die Fallzahlspalte "No of children"
in derselben Tabelle.
"""

from __future__ import annotations

from research_agent.meta.arm_level import convert_row


def test_klammer_sd_ohne_etikett_wird_abgelehnt():
    """Ohne Etikett bleibt "54.8 (51.9)" mehrdeutig - nicht raten."""
    header = ["", "Melatonin", "Placebo"]
    cells = ["Sleep onset latency (min)", "54.8 (51.9)", "92.4 (63.0)"]

    result = convert_row(header, cells, quote="x", n_per_arm=[54, 59])

    assert result["ok"] is False
    assert "Mittelwert" in result["reason"]


def test_klammer_sd_mit_caption_etikett_wird_gelesen():
    """Nennt die Caption "means (SD)", ist die Klammer die SD."""
    header = ["", "Melatonin", "Placebo"]
    cells = ["Sleep onset latency (min)", "54.8 (51.9)", "92.4 (63.0)"]

    result = convert_row(header, cells, quote="x", n_per_arm=[54, 59],
                         spread_hint="sd")

    assert result["ok"] is True
    assert [arm["sd"] for arm in result["arms"]] == [51.9, 63.0]
    assert result["n"] == 113
    # Melatonin senkt die Einschaflatenz: negativer Effekt.
    assert result["effect"] < 0


def test_fallzahlspalte_no_of_children_wird_erkannt():
    """'Melatonin No of children' ist eine n-Spalte, nicht ein Armwert."""
    header = ["", "Melatonin No of children", "Melatonin Week 12",
              "Placebo No of children", "Placebo Week 12"]
    cells = ["Sleep onset latency (min)", "54", "54.8 (51.9)",
             "59", "92.4 (63.0)"]

    result = convert_row(header, cells, quote="x", spread_hint="sd")

    assert result["ok"] is True
    assert [arm["n"] for arm in result["arms"]] == [54, 59]
    assert [arm["mean"] for arm in result["arms"]] == [54.8, 92.4]

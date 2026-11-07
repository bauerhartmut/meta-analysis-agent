"""Tests fuer ``research_agent.meta.baseline_columns``.

Der Kernfall: Eine Tabelle mit Baseline- und 6-Monats-Spalten und einer
adjustierten Differenz. Die Differenz ist brauchbar, die Baseline-Spalten
nicht - das Gate muss beides unterscheiden.
"""

from __future__ import annotations

from research_agent.meta.baseline_columns import (
    ALL_BASELINE,
    MIXED_TIMEPOINTS,
    baseline_columns,
    baseline_violation,
)

JSR_HEADER = [
    "",
    "Control group N",
    "Control group Baseline Mean (SD)",
    "Control group 6 months Mean (SD)",
    "Intervention group N",
    "Intervention group Baseline Mean (SD)",
    "Intervention group 6 months Mean (SD)",
    "Adjusted mean difference between groups Beta (95% CI)",
]


def test_baseline_spalten_werden_erkannt():
    assert baseline_columns(JSR_HEADER, [2, 5]) == [2, 5]
    assert baseline_violation(JSR_HEADER, [2, 5]) == ALL_BASELINE


def test_adjustierte_differenz_ist_keine_baseline_spalte():
    assert baseline_columns(JSR_HEADER, [7]) == []
    assert baseline_violation(JSR_HEADER, [7]) == ""


def test_gemischte_zeitpunkte_sind_kein_behandlungseffekt():
    assert baseline_violation(JSR_HEADER, [2, 3]) == MIXED_TIMEPOINTS


def test_tagesangaben_zaehlen_als_ausgangswert():
    header = ["Outcome", "Day 0", "Day 30"]
    assert baseline_columns(header, [1]) == [1]
    assert baseline_violation(header, [1, 2]) == MIXED_TIMEPOINTS


def test_zwischenueberschrift_wirkt_nur_bei_leerem_kopf():
    header = ["Outcome", "Mean (SD)", "Mean (SD)"]
    assert baseline_violation(header, [1, 2], row_group="Baseline") == ALL_BASELINE
    assert baseline_violation(header, [1, 2], row_group="6 months") == ""

"""Gate gegen Ausgangslage-Spalten in Tabellenzeilen.

Eine Zeile ist nur dann ein Behandlungseffekt, wenn die verglichenen Spalten
einen Zustand **nach** der Intervention beschreiben. Das Gate prueft deshalb
die Spalten, aus denen der Effekt gebildet wurde - nicht die Tabellen-Caption.

Der Unterschied ist nicht theoretisch: Die Tabelle "Sleep outcomes at baseline
and after 6 months" enthaelt Baseline- und 6-Monats-Spalten nebeneinander und
dazu die adjustierte Differenz zwischen den Gruppen. Eine Caption-Sperre
wuerde die brauchbare Zeile mit verwerfen; eine Spaltenpruefung nicht.

Erkannt wird eine Spalte an ihrem Kopf:
  * "Baseline", "Baseline Mean (SD)", "At baseline"
  * "Pre-treatment", "Pre-dose", "Vor der Intervention"
  * "Day 0", "Week 0", "T0"

Nennt der Kopf keinen Zeitpunkt, zaehlt die Zwischenueberschrift der Zeile
(``row_group``): In Tabellen mit der Ueberschrift "Baseline" tragen die
Spalten oft nur "Mean (SD)".
"""

from __future__ import annotations

import re
from typing import List, Sequence

BASELINE_COLUMN = re.compile(
    r"\bbaseline\b"
    r"|\bpre[-\s]?(?:treatment|intervention|dose|sleep|test|surgery)?\b"
    r"|\bday\s*0\b|\bweek\s*0\b|\bt\s*0\b"
    r"|\bat\s+inclusion\b|\bvor\s+(?:der\s+)?(?:intervention|behandlung)\b",
    re.IGNORECASE)

# Ein Kopf, der selbst einen Zeitpunkt nennt, schlaegt die Zwischenueberschrift.
TIMEPOINT_IN_HEADER = re.compile(
    r"\b(?:baseline|week|month|day|visit|post|follow[\s-]?up|change|end)\b",
    re.IGNORECASE)

ALL_BASELINE = "Baseline-Spalte (vor Intervention) - kein Behandlungseffekt"
MIXED_TIMEPOINTS = ("gemischte Zeitpunkte (Baseline und Follow-up) - "
                    "kein Behandlungseffekt")


def is_baseline_column(text: str) -> bool:
    return bool(BASELINE_COLUMN.search(str(text or "")))


def baseline_columns(header: Sequence[str], columns: Sequence[int],
                     row_group: str = "") -> List[int]:
    """Welche der verwendeten Spalten zeigen den Ausgangszustand?"""
    heads = list(header or [])
    flagged: List[int] = []
    for index in columns:
        head = str(heads[index]) if 0 <= index < len(heads) else ""
        if is_baseline_column(head):
            flagged.append(index)
        elif (row_group and is_baseline_column(row_group)
              and not TIMEPOINT_IN_HEADER.search(head)):
            flagged.append(index)
    return flagged


def baseline_violation(header: Sequence[str], columns: Sequence[int],
                       row_group: str = "") -> str:
    """Grund, warum die Zeile kein Behandlungseffekt ist - oder "".

    Sind alle verwendeten Spalten Ausgangswerte, ist die Zeile ein Vergleich
    vor der Intervention. Ist nur ein Teil davon Ausgangswert, vergleicht die
    Zeile zwei Zeitpunkte - auch das ist kein Behandlungseffekt. Eine Zeile
    ohne Baseline-Spalte wird nie allein wegen ihrer Caption verworfen.
    """
    used = list(columns or [])
    if not used:
        return ""
    flagged = baseline_columns(header, used, row_group)
    if not flagged:
        return ""
    if len(flagged) >= len(used):
        return ALL_BASELINE
    return MIXED_TIMEPOINTS

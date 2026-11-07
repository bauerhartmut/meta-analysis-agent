"""Deterministischer Leser fuer direkt berichtete Effektspalten.

Viele Tabellen enthalten die Schaetzung schon fertig: ``Hedges g (95% CI)``,
``OR (95% CI)``, ``Adjusted OR (95% CI)``, ``RR`` oder ``HR``. Der
Arm-Rechner (``arm_level.py``) ist dort nicht zustaendig - hier wird die
Zelle gelesen, der Standardfehler aus dem berichteten Intervall abgeleitet
(``derive_se``, gleiche z-Tabelle wie im Effekt-Extraktor) und die Zeile
gespeichert, wenn das Zitat woertlich im Dokument steht.

Was NICHT passiert:
  * Keine Umrechnung zwischen Massen (kein OR -> SMD, kein Median -> SMD).
  * Keine Ableitung ohne Intervall: ohne CI gibt es keinen SE und damit
    keine poolbare Zeile.
  * Kein Zeilenabgleich, wenn Kopf und Zeile verschieden viele Spalten
    haben. Zusammengefasste Kopfzellen (colspan) verschieben sonst jede
    Zahl um eine Spalte - genau der Fehler, der aus einem Placebo-Median
    einen Treatment-Effekt macht.
"""

from __future__ import annotations

import datetime as _dt
import json
import logging
import re
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .arm_level import parse_number

logger = logging.getLogger(__name__)

EFFECT_COLUMN_VERSION = "effect-column/1"

MIN_POINT = -1e6
MAX_POINT = 1e6


# --------------------------------------------------------------------------
# Spaltenkopf
# --------------------------------------------------------------------------

_UPPER = {
    "or": re.compile(r"\bOR\b"),
    "rr": re.compile(r"\bRR\b"),
    "hr": re.compile(r"\bHR\b"),
    "irr": re.compile(r"\bIRR\b"),
}
_WORDS = {
    "or": re.compile(r"odds\s+ratio", re.IGNORECASE),
    "rr": re.compile(r"(?:relative|risk)\s+ratio", re.IGNORECASE),
    "hr": re.compile(r"hazard\s+ratio", re.IGNORECASE),
    "irr": re.compile(r"incidence\s+rate\s+ratio", re.IGNORECASE),
}
# "Effect size" allein nennt keine Skala: In Schlafstudien steht darunter die
# Minutendifferenz (45.013 (2.891, 87.136)), in anderen die standardisierte
# Differenz. Nur wenn das Skalenwort dabei steht, ist der Typ belegbar.
_G = re.compile(r"hedges\W{0,3}s?\s*g\b|cohen\W{0,3}s\s*d\b|\bg\s*\(\s*9\d\s*%",
                re.IGNORECASE)
_SMD = re.compile(r"\bsmd\b|standard(?:ized|ised)\s+(?:mean\s+(?:difference|contrast)"
                  r"|effect\s+size)", re.IGNORECASE)
# Gepoolte oder meta-analytische Schaetzungen sind keine Studienzeile. Sie in
# eine Gruppe zu legen, zaehlt dieselben Studien doppelt.
_POOLED = re.compile(
    r"pooled|leave[\s-]?one[\s-]?out|meta[\s-]?analy|random[\s-]?effects"
    r"|overall\s+(?:effect|estimate)|summary\s+(?:effect|estimate)",
    re.IGNORECASE)
# Eine Zeile "(Intercept)" beweist eine Regressions- oder Modelltabelle: die
# uebrigen Zeilen sind dann Praediktoren (Age, Sex, Ethnicity), keine Effekte.
_MODEL_ROW = re.compile(r"^\(?\s*intercept\s*\)?$|^constant$|^_cons$", re.IGNORECASE)


def is_model_table(rows) -> bool:
    """True, wenn eine Tabellenzeile ein Intercept ist (Modelltabelle)."""
    for row in rows:
        cells = getattr(row, "cells", row)
        cells = list(cells or [])
        if cells and _MODEL_ROW.match(str(cells[0] or "").strip()):
            return True
    return False
# Rohskalige Differenz, wie Schlaf- und Schmerzstudien sie berichten:
# "Mean difference (95% CI)", "Difference in means", "MD (95% CI)".
# "Baseline difference" ist keine Behandlungswirkung und bleibt aussen vor.
_MD = re.compile(
    r"mean\s+difference|difference\s+in\s+means?"
    r"|(?<!baseline\s)difference\b|\bMD\b",
    re.IGNORECASE)
_BETA = re.compile(r"\u03b2|\bbeta\b|regression\s+coefficient", re.IGNORECASE)
_CI = re.compile(r"\bCI\b|confidence\s+interval", re.IGNORECASE)
_LEVEL = re.compile(r"(9[059])\s*%\s*(?:CI|confidence)|CI\s*[:=]?\s*(9[059])\s*%",
                    re.IGNORECASE)
_ADJUSTED = re.compile(r"adjust|multivariab|crude\s+and\s+adjust", re.IGNORECASE)

# Spalten, die nie ein Effekt sind, auch wenn "OR" als Wort darin steht.
_NOT_EFFECT = re.compile(
    r"p\s*[- ]?\s*value|no\.?\s+of\s+pairs|median|iqr|interquartile"
    r"|mean\s*\(|weight",
    re.IGNORECASE)


def header_effect_kind(header_cell: str) -> Tuple[str, float, bool]:
    """(Effekttyp, CI-Niveau, adjustiert) aus einem Spaltenkopf.

    Leerer Typ heisst: diese Spalte traegt keinen direkt berichteten Effekt.
    """
    text = str(header_cell or "").strip()
    if not text or _NOT_EFFECT.search(text) or not _CI.search(text):
        return "", 0.0, False
    kind = ""
    for candidate in ("irr", "hr", "rr", "or"):
        if _UPPER[candidate].search(text) or _WORDS[candidate].search(text):
            kind = candidate
            break
    if not kind:
        # Reihenfolge: SMD vor mean_diff ("standardized mean difference"
        # enthaelt beide Woerter), mean_diff vor g ("effect size (mean
        # difference)" ist eine Differenz, kein standardisierter Effekt).
        if _SMD.search(text):
            kind = "smd"
        elif _MD.search(text):
            kind = "mean_diff"
        elif _G.search(text):
            kind = "g"
        elif _BETA.search(text):
            kind = "beta"
    if not kind:
        return "", 0.0, False
    if _POOLED.search(text):
        return "", 0.0, False
    match = _LEVEL.search(text)
    level = 0.95
    if match:
        value = match.group(1) or match.group(2)
        level = int(value) / 100.0
    return kind, level, bool(_ADJUSTED.search(text))


# Ein Label, das nur ein Code ist ("T2", "Model 1", "M3"), benennt kein
# Outcome. Es entsteht, wenn die eigentliche Beschriftung in einer
# rowspan-Zelle der Zeile darueber steht.
_CODE_LABEL = re.compile(r"^(?:[A-Za-z]{0,3}\s?\d+|model\s?\d+|m\d+|t\d+)$",
                         re.IGNORECASE)
_TABLE_PREFIX = re.compile(r"^\s*(?:Table|Tab\.?|Tabelle)\s*\d*\s*[.:]?\s*", re.IGNORECASE)


def _outcome_label(cells: Sequence[str], caption: str = "",
                   row_group: str = "") -> str:
    """Outcome-Name aus der Zeile, nicht aus der Caption.

    Frueher galt "Zelle ohne Ziffer" als Label; damit fielen echte Namen
    wie "Short sleep duration (<6 hours per night)" durch und alle Zeilen
    einer Tabelle hiessen wie ihre Caption. Ein Label ist jetzt jeder
    Zelltext mit Buchstaben, der nicht selbst eine Zahl ist.

    ``row_group`` ist die Beschriftung, die eine rowspan-Zelle der Zeile
    darueber fuer diese Zeile mitgibt ("Sleep parameter"). Sie wird
    vorangestellt, wenn das eigene Label fehlt oder nur ein Code ist - sonst
    hiesse die Zeile "T2" statt "Sleep parameter T2".
    """
    label = ""
    for cell in cells:
        text = str(cell or "").strip()
        if not text or not re.search(r"[A-Za-z]", text):
            continue
        if re.fullmatch(r"[\s\d.,%\-\u2013\u2212+()<>]*", text):
            continue
        label = text[:90]
        break
    group = str(row_group or "").strip()
    code = bool(_CODE_LABEL.match(label))
    if not group:
        if label and not code:
            return label
        # Ohne Gruppenbeschriftung bleibt die Caption: sie nennt bei
        # Modelltabellen das Outcome ("Odds ratios for excessive daytime
        # sleepiness ..."). Besser als "Model 1" ist sie belegt, nicht geraten.
        text = _TABLE_PREFIX.sub("", str(caption or "")).strip()
        if code and text:
            return text[:90]
        return (label or text[:90])
    if not label:
        return group[:90]
    if code:
        return f"{group} {label}"[:90]
    return label


# --------------------------------------------------------------------------
# Zelle
# --------------------------------------------------------------------------

_RANGE = re.compile(
    r"(-?\d+(?:[.,]\d+)?)\s*(?:to|bis|-|\u2013|,)\s*(-?\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)


@dataclass
class DirectEffect:
    """Eine gelesene Effektzelle, bevor sie gespeichert wird."""

    effect_type: str
    effect: float
    ci_low: float
    ci_high: float
    ci_level: float
    adjusted: int
    quote: str
    outcome: str = ""
    comparison: str = ""

    def to_dict(self) -> Dict:
        return {
            "ok": True,
            "effect_type": self.effect_type,
            "effect": self.effect,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "ci_level": self.ci_level,
            "adjusted": self.adjusted,
            "quote": self.quote,
            "outcome": self.outcome,
            "comparison": self.comparison,
        }


def parse_effect_cell(cell: str) -> Optional[Tuple[float, float, float]]:
    """(Punkt, low, high) aus "0.07 (0.05 to 0.09)" - oder None.

    Ohne Intervall gibt es keinen Standardfehler und damit keine poolbare
    Zeile; ein Punktwert allein wird verworfen.
    """
    text = str(cell or "").strip()
    if not text:
        return None
    # Nur fuer das Lesen: Unicode-Minus und Gedankenstrich auf ASCII
    # bringen, damit -0.32 und -0.17 erkannt werden. Das Zitat bleibt die
    # unveraenderte Originalzeile.
    clean = (text.replace("\u2212", "-").replace("\u2013", "-")
                 .replace("\u2014", "-"))
    point = parse_number(text)
    if point is None:
        return None
    span = _RANGE.search(clean)
    if not span:
        return None
    low = parse_number(span.group(1))
    high = parse_number(span.group(2))
    if low is None or high is None or high <= low:
        return None
    if not (min(low, high) <= point <= max(low, high)):
        return None      # der Punktschaetzer liegt nicht im Intervall
    return point, low, high


def effects_from_row(header: Sequence[str], cells: Sequence[str],
                     quote: str, caption: str = "",
                     row_group: str = "") -> Tuple[List[Dict], str]:
    """Alle direkten Effekte einer Tabellenzeile, oder ([], Grund).

    Kopf und Zeile muessen gleich viele Spalten haben; sonst ist die
    Zuordnung nicht belegbar und die Zeile wird verworfen.
    """
    header = list(header or [])
    cells = list(cells or [])
    if not cells:
        return [], "leere Zeile"
    if not header:
        return [], "keine Kopfzeile"
    if len(header) != len(cells):
        return [], (f"Kopfzeile ({len(header)} Spalten) passt nicht zur Zeile "
                    f"({len(cells)} Zellen) - colspan nicht aufloesbar")
    if _MODEL_ROW.match(str(cells[0] or "").strip()):
        return [], "Modelltabelle (Intercept-Zeile), keine Behandlungseffekte"
    outcome = _outcome_label(cells, caption, row_group)
    found: List[Dict] = []
    saw_effect_column = False
    saw_pooled = False
    for index, head in enumerate(header):
        if _POOLED.search(str(head or "")):
            saw_pooled = True
            continue
        kind, level, adjusted = header_effect_kind(head)
        if not kind:
            continue
        saw_effect_column = True
        parsed = parse_effect_cell(cells[index])
        if not parsed:
            continue
        point, low, high = parsed
        if not MIN_POINT <= point <= MAX_POINT:
            continue
        found.append(DirectEffect(
            effect_type=kind, effect=point, ci_low=low, ci_high=high,
            ci_level=level, adjusted=1 if adjusted else 0,
            quote=quote, outcome=outcome,
            comparison=str(head).strip(),
        ).to_dict())
    if not found:
        if saw_pooled:
            return [], "gepoolte Schaetzung (Metaanalyse), keine Studienzeile"
        if saw_effect_column:
            return [], "Effektspalte ohne lesbares Intervall"
        return [], "keine Effektspalte im Kopf"
    return found, ""


# --------------------------------------------------------------------------
# Speichern - nur verifizierte, plausible Zeilen
# --------------------------------------------------------------------------

_UNIT = {
    "g": "Hedges g", "smd": "SMD", "or": "Odds Ratio", "rr": "Risk Ratio",
    "hr": "Hazard Ratio", "irr": "Incidence Rate Ratio", "beta": "beta",
    "mean_diff": "Mitteldifferenz (Rohskala)",
}
_DIRECTION = {
    "g": "hoeheres g bedeutet einen groesseren Gruppenunterschied",
    "smd": "hoeheres SMD bedeutet einen groesseren Gruppenunterschied",
    "or": "hoeheres OR bedeutet hoehere Odds (mehr Ereignisse)",
    "rr": "hoeheres RR bedeutet ein hoeheres Risiko",
    "hr": "hoeheres HR bedeutet ein hoeheres Hazard",
    "irr": "hoeheres IRR bedeutet eine hoehere Inzidenzrate",
    "beta": "hoeheres beta bedeutet einen staerkeren Zusammenhang",
    "mean_diff": ("Vorzeichen folgt der Gruppenreihenfolge der Tabelle; "
                  "der Betrag ist der Unterschied zwischen den Gruppen"),
}


def store_direct_effects(db, source_id: str, source_text_id: str,
                         document_text: str,
                         candidates: Sequence[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Verifizierte Effektzeilen speichern; alles andere zurueckmelden."""
    from ..research.fulltext import locate_quote
    from .extraction import check_plausibility, derive_se

    stored: List[Dict] = []
    rejected: List[Dict] = []
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()

    for candidate in candidates:
        quote = str(candidate.get("quote") or "")
        span = locate_quote(document_text, quote) if (quote and document_text) else None
        if not span:
            rejected.append({"quote": quote, "reason": "Zitat nicht im Dokument"})
            continue
        kind = str(candidate.get("effect_type") or "")
        se = derive_se(candidate.get("ci_low"), candidate.get("ci_high"),
                       float(candidate.get("ci_level") or 0.95))
        if se is None or se <= 0:
            rejected.append({"quote": quote, "reason": "kein Standardfehler aus dem CI"})
            continue
        row = {
            "id": uuid.uuid4().hex,
            "source_id": source_id,
            "outcome": str(candidate.get("outcome") or ""),
            "outcome_key": str(candidate.get("outcome") or ""),
            "comparison": str(candidate.get("comparison") or ""),
            "effect_type": kind,
            "effect": float(candidate["effect"]),
            "se": float(se),
            "ci_low": float(candidate["ci_low"]),
            "ci_high": float(candidate["ci_high"]),
            "ci_level": float(candidate.get("ci_level") or 0.95),
            "n": None,
            "design": "",
            "population": "",
            "direction": _DIRECTION.get(kind, ""),
            "unit": _UNIT.get(kind, kind),
            "quote": quote,
            "quote_start": span.start,
            "quote_end": span.end,
            "source_text_id": source_text_id,
            "extractor": EFFECT_COLUMN_VERSION,
            "extraction_pass": 1,
            "disputed": 0,
            "rejection_reason": "",
            "adjusted": int(candidate.get("adjusted")) if candidate.get("adjusted") is not None else -1,
            "time_point": "",
            "moderators": json.dumps({"column": candidate.get("comparison")},
                                     ensure_ascii=False),
            "created_at": now,
        }
        problem = check_plausibility(row)
        if problem:
            rejected.append({"quote": quote, "reason": problem})
            continue
        db.save_study_effect(row)
        stored.append(row)
    return stored, rejected

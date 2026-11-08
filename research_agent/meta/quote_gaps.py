"""Deterministische Lueckenpruefung fuer Effekt-Quotes.

Befund E3 (MENDS, `data/bench/validierung/`): Der Satz nennt zwei
Konfidenzintervalle, der Extraktor gibt genau eine Zeile zurueck. Die Zeile
ist korrekt, die zweite fehlt - und nichts in der Kette merkt es. Fuer das
Pooling sieht der Fall aus wie k = 1 und geht still ein.

Diese Pruefung zaehlt die Intervalle in einer Quote und vergleicht sie mit den
Zeilen, die aus ihr stammen. Sie ist rein deterministisch: kein Modellaufruf,
keine Aenderung an einer Zeile, keine Persistenz. Sie meldet nur.

Bewusst nicht in `pool()` verdrahtet: Das Pooling rechnet unveraendert, der
Befund steht daneben. Eine Luecke ist ein Lese-Befund, kein Rechenfehler.

Grenzen: Die Zuordnung "welches Intervall fehlt" laeuft ueber die Zahlen
(Werte und Klammern auf zwei Dezimalen gerundet, daher `tol`). Sie ist eine
Diagnose, keine Wahrheit - die harte Aussage ist die Anzahl: mehr Intervalle
in der Quote als Zeilen daraus. Eine Zeile, die zwei Intervalle zu einem
zusammenfasst, wird deshalb ebenfalls als Luecke gemeldet.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

_NUM = r"[-+\u2212]?\d+(?:[.,]\d+)?"
_PAIRS = {"(": ")", "[": "]"}
_CI = re.compile(
    r"(?:95\s*%\s*)?(?:confidence\s+interval|CI)\s*(?:\(\s*CI\s*\))?\s*[:=]?\s*"
    rf"({_NUM})\s*(?:to|bis|[\u2013\u2014])\s*({_NUM})",
    re.IGNORECASE,
)
_RANGE = re.compile(
    rf"({_NUM})\s*(?:to|bis|[\u2013\u2014]|,|;|/)\s*({_NUM})",
    re.IGNORECASE,
)
_NUMBER = re.compile(_NUM)
# "n = 20", "SD = 2.0", "p = 0.01" sind keine Intervalle.
_BLOCKED = re.compile(
    r"\b(?:SD|SE|s\.?d\.?|s\.?e\.?|n|p|df|I2|tau2?|r)\s*[=:]", re.IGNORECASE
)


def _float(value) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("\u2212", "-").replace("\u2013", "-")
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _fmt(value: float) -> str:
    return f"{value:g}"


def _has_decimal(text: str) -> bool:
    return "." in text or "," in text


@dataclass(frozen=True)
class Interval:
    """Ein Intervall, wie es in einer Klammer steht."""

    raw: str
    start: int
    end: int
    low: float
    high: float
    point: Optional[float] = None

    def label(self) -> str:
        prefix = "" if self.point is None else f"{_fmt(self.point)} "
        return f"{prefix}[{_fmt(self.low)}; {_fmt(self.high)}]"


@dataclass(frozen=True)
class GapReport:
    """Befund zu genau einer Quote."""

    quote: str
    intervals: Tuple[Interval, ...] = ()
    rows: int = 0
    rejected: int = 0
    matched: int = 0
    missing: Tuple[Interval, ...] = ()
    status: str = "nicht_pruefbar"
    message: str = ""

    @property
    def is_gap(self) -> bool:
        return self.status in ("luecke", "keine_zeile")

    def to_dict(self) -> Dict:
        return {
            "quote": self.quote,
            "status": self.status,
            "message": self.message,
            "zeilen": self.rows,
            "abgelehnt": self.rejected,
            "intervalle": [i.label() for i in self.intervals],
            "zugeordnet": self.matched,
            "nicht_belegt": [i.label() for i in self.missing],
        }


def _brackets(text: str):
    """Balancierte Klammergruppen, auch verschachtelt.

    Der Korpus schreibt beide Formen::

        (-37.49 minutes, 95% CI -55.27 to -19.71)
        [95% confidence interval (CI) 0.52 to 44.34 minutes; p=0.04]

    Ein Regex auf ``[^()]+`` scheitert an der zweiten; deshalb zaehlt der
    Scanner die Tiefe.
    """

    index = 0
    while index < len(text):
        opener = text[index]
        if opener not in _PAIRS:
            index += 1
            continue
        depth = 0
        end = -1
        for position in range(index, min(len(text), index + 240)):
            if text[position] in _PAIRS:
                depth += 1
            elif text[position] in (")", "]"):
                depth -= 1
                if depth == 0:
                    end = position
                    break
        if end < 0:
            index += 1
            continue
        yield index, end + 1, text[index + 1:end]
        index = end + 1


def _leading_point(content: str, stop: int) -> Optional[float]:
    """Der Punkt-Schaetzer vor dem CI-Marker, ohne die 95 in "95% CI"."""

    for number in _NUMBER.finditer(content):
        if number.start() >= stop:
            return None
        if content[number.end():number.end() + 2].lstrip().startswith("%"):
            continue
        return _float(number.group())
    return None


def find_intervals(text: str) -> List[Interval]:
    """Alle Konfidenzintervalle, die in Klammern von ``text`` stehen.

    Erkannt werden die beiden Formen, die im Korpus vorkommen:

        (-37.49 minutes, 95% CI -55.27 to -19.71 minutes; p<0.0001)
        [-55.27, -19.71]

    Der Punkt-Schaetzer (hier -37.49) wird mitgenommen, wenn eine Zahl vor
    dem CI-Marker steht. Klammern mit ``SD``/``SE``/``n``/``p`` und ohne
    CI-Marker zaehlen nicht: ``10.0 (2.0)`` ist keine Intervallsangabe.
    """

    found: List[Interval] = []
    for start, end, content in _brackets(text or ""):
        m_ci = _CI.search(content)
        if m_ci:
            first = _float(m_ci.group(1))
            second = _float(m_ci.group(2))
            if first is None or second is None:
                continue
            point = _leading_point(content, m_ci.start())
            low, high = sorted((first, second))
            found.append(Interval(raw=(text or "")[start:end], start=start,
                                  end=end, low=low, high=high, point=point))
            continue

        numbers = list(_NUMBER.finditer(content))
        if len(numbers) != 2 or _BLOCKED.search(content):
            continue
        gap = content[numbers[0].end():numbers[1].start()]
        if not re.fullmatch(r"\s*(?:to|bis|[\u2013\u2014,;/])\s*", gap, re.IGNORECASE):
            continue
        first, second = numbers[0].group(), numbers[1].group()
        if not (_has_decimal(first) or _has_decimal(second)):
            continue
        low, high = sorted((_float(first), _float(second)))
        found.append(Interval(raw=(text or "")[start:end], start=start,
                              end=end, low=low, high=high))
    return found


def _covers(interval: Interval, row: dict, tol: float) -> bool:
    ci_low = _float(row.get("ci_low"))
    ci_high = _float(row.get("ci_high"))
    if ci_low is not None and ci_high is not None:
        return abs(ci_low - interval.low) <= tol and abs(ci_high - interval.high) <= tol
    effect = _float(row.get("effect"))
    if effect is not None and interval.point is not None:
        return abs(effect - interval.point) <= tol
    return False


def _usable(row: dict) -> bool:
    """Zaehlt nur eine Zeile, die nicht abgelehnt wurde und einen Wert hat."""
    if str(row.get("rejection_reason") or "").strip():
        return False
    return (_float(row.get("effect")) is not None
            or _float(row.get("ci_low")) is not None)


def audit_quote(quote: str, rows: Sequence[dict], tol: float = 0.02) -> GapReport:
    """Vergleicht die Intervalle einer Quote mit ihren Extraktionszeilen."""

    text = " ".join(str(quote or "").split())
    intervals = tuple(find_intervals(text))
    rows = list(rows or [])
    rejected = sum(1 for r in rows if str(r.get("rejection_reason") or "").strip())
    usable = [r for r in rows if _usable(r)]

    free = list(usable)
    matched_intervals = []
    missing = []
    for interval in intervals:
        hit = next((r for r in free if _covers(interval, r, tol)), None)
        if hit is None:
            missing.append(interval)
        else:
            free.remove(hit)
            matched_intervals.append(interval)

    if not intervals:
        status = "nicht_pruefbar"
        message = "Quote nennt kein Konfidenzintervall - Luecke nicht pruefbar"
    elif not usable:
        status = "keine_zeile"
        message = (f"Quote nennt {len(intervals)} Intervall(e), "
                   f"keine Zeile extrahiert")
    elif len(usable) < len(intervals):
        status = "luecke"
        message = (f"Quote nennt {len(intervals)} Intervalle, "
                   f"{len(usable)} Zeile(n) extrahiert")
        if missing:
            message += " - nicht belegt: " + ", ".join(i.label() for i in missing)
        else:
            message += (" - welches Intervall fehlt, ist aus den Zahlen "
                        "nicht bestimmbar")
    else:
        status = "ok"
        message = (f"Quote nennt {len(intervals)} Intervall(e), "
                   f"{len(usable)} Zeile(n) - vollstaendig")

    return GapReport(quote=text, intervals=intervals, rows=len(usable),
                     rejected=rejected, matched=len(matched_intervals),
                     missing=tuple(missing), status=status, message=message)


def audit_rows(rows: Sequence[dict], tol: float = 0.02) -> List[GapReport]:
    """Prueft alle Zeilen einer Quelle, gruppiert nach ihrer Quote.

    Zeilen ohne Quote bilden eine eigene Gruppe und landen auf
    ``nicht_pruefbar``: Sie werden nicht als Luecke gezaehlt, aber auch nicht
    als geprueft.
    """

    groups: Dict[str, List[dict]] = {}
    order: List[str] = []
    for row in rows or []:
        key = " ".join(str(row.get("quote") or "").split())
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)
    return [audit_quote(key, groups[key], tol) for key in order]


def summarize(reports: Sequence[GapReport]) -> Dict[str, int]:
    """Zaehler fuer Telemetrie und Bericht."""

    return {
        "quotes": len(reports),
        "ok": sum(1 for r in reports if r.status == "ok"),
        "luecken": sum(1 for r in reports if r.status == "luecke"),
        "ohne_zeile": sum(1 for r in reports if r.status == "keine_zeile"),
        "nicht_pruefbar": sum(1 for r in reports if r.status == "nicht_pruefbar"),
        "zeilen": sum(r.rows for r in reports),
        "intervalle": sum(len(r.intervals) for r in reports),
        "fehlende_intervalle": sum(len(r.missing) for r in reports),
    }

"""Deterministischer Umrechner: Arm-Deskriptiva -> Hedges g mit SE.

Der Effekt-Extraktor liest nur, was als Effekt dasteht. Viele Tabellen
liefern stattdessen Mittelwert, Streuung und n je Arm; daraus laesst sich
die standardisierte Mittelwertdifferenz exakt berechnen - ohne Modell,
ohne Schaetzung. Dieses Modul tut genau das, und es speichert nur Zeilen,
deren beide Arme vollstaendig belegt sind und deren Zitat woertlich im
gespeicherten Dokument steht.

Formeln (Hedges & Olkin 1985):
    s_pooled^2 = ((n1-1) s1^2 + (n2-1) s2^2) / (n1 + n2 - 2)
    d          = (m1 - m2) / s_pooled
    J          = 1 - 3 / (4 (n1 + n2) - 9)
    g          = J * d
    SE(g)      = sqrt((n1 + n2) / (n1 n2) + g^2 / (2 (n1 + n2)))

Streuungsangaben werden nur uebernommen, wenn sie eindeutig sind:
  * "391.8 ± 12.4"                -> SD
  * "7.21 (SE 1.13)"              -> SE, SD = SE * sqrt(n)
  * "16.7 (11.6 to 22.0)"         -> 95 %-CI des Mittelwerts,
                                     SE = (hi - lo) / (2 z), SD = SE * sqrt(n)
  * "16.7 (11.6)"                 -> unklar (SD? CI? IQR?) und wird verworfen
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

ARM_LEVEL_VERSION = "arm-level/1"

_MIN_ARM_N = 2


@dataclass
class ArmStats:
    """Ein Arm mit Mittelwert, Streuung und Fallzahl."""

    label: str
    n: int
    mean: float
    sd: float
    sd_source: str = "sd"     # "sd" | "se" | "ci"


@dataclass
class ArmEffect:
    """Ergebnis der Umrechnung, bevor es gespeichert wird."""

    effect: float
    se: float
    n_total: int
    arm1: ArmStats
    arm2: ArmStats
    d: float
    correction: float
    direction: str

    def to_dict(self) -> Dict:
        return {
            "effect": round(self.effect, 6),
            "se": round(self.se, 6),
            "n": self.n_total,
            "d": round(self.d, 6),
            "correction": round(self.correction, 6),
            "direction": self.direction,
            "arms": [
                {"label": a.label, "n": a.n, "mean": a.mean,
                 "sd": round(a.sd, 6), "sd_source": a.sd_source}
                for a in (self.arm1, self.arm2)
            ],
        }


# --------------------------------------------------------------------------
# Zahlen und Streuungen lesen
# --------------------------------------------------------------------------

_NUM_RE = re.compile(r"[-+\u2212\u2013]?\d[\d.,]*")


def parse_number(value) -> Optional[float]:
    """Eine Zahl aus einer Zelle, oder None.

    Grenzen wie "<.001" sind p-Werte, keine Messwerte, und werden verworfen.
    Trennzeichen folgen einer festen Konvention, nicht dem Zufall der Zelle:
    stehen Punkt und Komma, entscheidet das LETZTE Zeichen ("1,234.5" ->
    1234.5), mehrere Kommas sind Tausendertrenner ("1,234,567"), ein
    einzelnes Komma ist in diesem Projekt das Dezimalkomma ("0,42" -> 0.42).
    Nichts wird gerundet oder geschaetzt.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    text = str(value).strip()
    if not text or "<" in text or ">" in text:
        return None
    text = (text.replace("\u2212", "-").replace("\u2013", "-")
                .replace("\u00a0", " ").replace("\u2009", " "))
    match = _NUM_RE.search(text)
    if not match:
        return None
    token = match.group(0).lstrip("+").rstrip(".,")
    if not token:
        return None
    if "," in token and "." in token:
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif token.count(",") > 1:
        token = token.replace(",", "")
    elif "," in token:
        token = token.replace(",", ".")
    try:
        number = float(token)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def sd_from_se(se: float, n: int) -> Optional[float]:
    """SD = SE * sqrt(n)."""
    if se is None or n is None:
        return None
    if se <= 0 or int(n) < _MIN_ARM_N:
        return None
    return float(se) * math.sqrt(int(n))


def sd_from_ci(low: float, high: float, n: int,
               level: float = 0.95) -> Optional[float]:
    """SD aus einem Konfidenzintervall des Mittelwerts (ueber den SE)."""
    from .extraction import derive_se  # dieselbe z-Tabelle wie im Extraktor

    se = derive_se(low, high, level)
    return sd_from_se(se, n) if se else None


_RANGE_RE = re.compile(
    r"(-?\d+(?:[.,]\d+)?)\s*(?:to|bis|-|\u2013|,)\s*(-?\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)


def parse_mean_spread(cell: str, role: str = "") -> Optional[Tuple[float, float, str]]:
    """(Mittelwert, Streuung, Art) aus einer Zelle - oder None.

    ``role`` kommt aus dem Spaltenkopf ("sd", "se", "ci") und entscheidet
    nur dann, wenn die Zelle selbst nichts sagt. Alles andere wird
    verworfen: eine Zahl in Klammern ohne Etikett kann SD, SE, CI oder
    Interquartilsabstand sein, und Raten waere hier ein erfundener Wert.

    Ein "\u00b1" ohne Etikett gilt als SD. Nennt die Zelle oder der Kopf
    dagegen SE, wird daraus ein Standardfehler - sonst wuerde ein Kopf
    "mean \u00b1 SE" als Standardabweichung gelesen und g um ein Vielfaches
    zu gross.
    """
    text = str(cell or "").strip()
    if not text:
        return None
    mean = parse_number(text)
    if mean is None:
        return None
    lowered = text.lower()
    has_sd = bool(re.search(r"\bsd\b|standard\s+deviation", lowered))
    has_se = bool(re.search(r"\bse\b|standard\s+error", lowered))
    has_ci = bool(re.search(r"95\s*%|confidence\s+interval|\bci\b", lowered))

    # "mean ± spread"
    if "\u00b1" in text:
        spread = parse_number(text.split("\u00b1", 1)[1])
        if not spread or spread <= 0:
            return None
        if has_se:
            return mean, spread, "se"
        if has_sd:
            return mean, spread, "sd"
        if role == "ci":
            return None      # kein Intervall; nicht umdeuten
        return mean, spread, role if role in ("sd", "se") else "sd"

    inner = re.search(r"\(([^()]*)\)", text)
    if not inner:
        return None
    body = inner.group(1)
    kind = ""
    if has_sd:
        kind = "sd"
    elif has_se:
        kind = "se"
    elif has_ci:
        kind = "ci"
    elif _RANGE_RE.search(body):
        kind = "ci"          # Wertebereich in Klammern ohne Etikett
    elif role in ("sd", "se", "ci"):
        kind = role
    if not kind:
        return None

    if kind == "ci":
        span = _RANGE_RE.search(body)
        if not span:
            return None
        low, high = parse_number(span.group(1)), parse_number(span.group(2))
        if low is None or high is None or high <= low:
            return None
        # Die Streuung selbst braucht die Fallzahl; sie wird im Aufrufer
        # ueber _split_ci geholt. Hier nur die Art markieren.
        return mean, high - low, "ci"
    spread = parse_number(body)
    if spread is None or spread <= 0:
        return None
    return mean, spread, kind


def _split_ci(cell: str) -> Optional[Tuple[float, float, float]]:
    """(Mittelwert, low, high) fuer den CI-Fall; getrennt, weil der Aufrufer
    die Fallzahl fuer die Umrechnung braucht."""
    text = str(cell or "").strip()
    mean = parse_number(text)
    span = _RANGE_RE.search(text)
    if mean is None or not span:
        return None
    low, high = parse_number(span.group(1)), parse_number(span.group(2))
    if low is None or high is None or high <= low:
        return None
    return mean, low, high


# --------------------------------------------------------------------------
# Rechnen
# --------------------------------------------------------------------------

def cohens_d(m1: float, sd1: float, n1: int, m2: float, sd2: float,
             n2: int) -> Optional[float]:
    if int(n1) < _MIN_ARM_N or int(n2) < _MIN_ARM_N:
        return None
    if sd1 is None or sd2 is None or sd1 <= 0 or sd2 <= 0:
        return None
    pooled = (((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2)
              / (n1 + n2 - 2))
    if pooled <= 0:
        return None
    return (m1 - m2) / math.sqrt(pooled)


def hedges_correction(n1: int, n2: int) -> float:
    """J = 1 - 3 / (4 (n1 + n2) - 9)."""
    total = int(n1) + int(n2)
    return 1.0 - 3.0 / (4.0 * total - 9.0)


def se_of_g(g: float, n1: int, n2: int) -> float:
    """SE(g) = sqrt((n1+n2)/(n1 n2) + g^2 / (2 (n1+n2)))."""
    return math.sqrt(((n1 + n2) / (n1 * n2))
                     + (g * g) / (2.0 * (n1 + n2)))


def smd_from_arms(arm1: ArmStats, arm2: ArmStats) -> Optional[ArmEffect]:
    """Hedges g mit Standardfehler aus zwei vollstaendigen Armen."""
    if arm1 is None or arm2 is None:
        return None
    d = cohens_d(arm1.mean, arm1.sd, arm1.n, arm2.mean, arm2.sd, arm2.n)
    if d is None:
        return None
    correction = hedges_correction(arm1.n, arm2.n)
    g = correction * d
    se = se_of_g(g, arm1.n, arm2.n)
    if not math.isfinite(se) or se <= 0:
        return None
    direction = (f"hoeherer Wert in '{arm1.label}' als in '{arm2.label}' "
                 f"bedeutet einen hoeheren Outcome-Wert")
    return ArmEffect(effect=g, se=se, n_total=arm1.n + arm2.n,
                     arm1=arm1, arm2=arm2, d=d, correction=correction,
                     direction=direction)


# --------------------------------------------------------------------------
# Tabellenzeile -> zwei Arme
# --------------------------------------------------------------------------

_MEDIAN_RE = re.compile(r"median|\biqr\b|interquartile", re.IGNORECASE)
_DIRECT_EFFECT_RE = re.compile(r"hedges|\beffect\s+size\b|\bg\s*\(95", re.IGNORECASE)
_RATIO_RE = re.compile(
    r"\b(?:OR|RR|HR|IRR)\b|odds\s+ratio|risk\s+ratio|hazard\s+ratio",
    re.IGNORECASE)

_REASONS = {
    "few_columns": "zu wenige Spalten",
    "no_arm": "kein Mittelwert mit eindeutiger Streuung in zwei Spalten",
    "no_n": "Fallzahl je Arm fehlt",
    "bad_spread": "Streuung nicht eindeutig (SD/SE/CI)",
    "bad_n": "Fallzahl zu klein",
    "bad_sd": "Streuung nicht positiv",
    "arm_count": "nicht genau zwei Spalten mit Mittelwert und Streuung",
    "median": "Median/IQR statt Mittelwert mit SD/SE/CI (kein SMD)",
    "ratio": "direkter Effekt mit OR/RR/HR - nicht Aufgabe des Arm-Rechners",
    "baseline": ("Baseline-Zeile (Tag 0 / vor Intervention) - "
                 "kein Behandlungseffekt"),
    "cross_sectional": ("kein Interventionsarm - Querschnitts- oder "
                        "Gruppenvergleich"),
}

# Zeitpunkt der Zeile: eine Spalte "Day", "Week", "Visit" oder "Time
# point" nennt ihn ausdruecklich, sonst traegt ihn die Zeilenbeschriftung
# ("Day 30", "post-BLT1").
_TIME_COLUMN = re.compile(
    r"^(?:day|week|month|visit|time\s*point|timepoint|time|session)\b",
    re.IGNORECASE)
_TIMEPOINT_LABEL = re.compile(
    r"^(?:day|week|month|visit|post(?:[\s-]|$)|follow[\s-]?up|t\d+)\b",
    re.IGNORECASE)
# Tag 0, "baseline" und "pre-BLT" sind der Zustand vor der Intervention.
# Die Muster verlangen den ganzen Zellwert: "0" und "Day 0" ja, "0.5 mg" nein.
_BASELINE_VALUE = re.compile(
    r"^\s*(?:(?:day|week|month|visit|time)\s*[-_ ]?)?0(?:\.0+)?\s*$"
    r"|^\s*(?:(?:day|week|month|visit)\s*)?baseline\s*$"
    r"|^\s*pre(?:[\s-][\w-]*)?\s*$"
    r"|^\s*t0\s*$",
    re.IGNORECASE)
# Woerter, die eine Spalte nur als Statistik beschreiben ("Mean (SD)",
# "Arm 1"). Solche Etiketten benennen keine Gruppe; ohne Gruppennamen gibt
# es nichts zu klassifizieren, also wird auch nichts abgelehnt.
_GENERIC_LABEL = re.compile(
    r"\b(?:mean|median|sd|se|sem|ci|value|values|score|scores|m|n|arm|group|column)\b"
    r"|\d|[\.\,\(\)\[\]\u00b1%:;=\-\u2013/+<>]",
    re.IGNORECASE)
# Ein Arm muss eine Intervention benennen. "Active children" gegen
# "Inactive children" oder "Patients" gegen "Healthy Controls" sind
# Querschnittsgruppen, keine randomisierten Arme.
_INTERVENTION_ARM = re.compile(
    r"intervention|treatment|placebo|sham|verum|vehicle|supplement|dos(?:e|ing)"
    r"|\bmg\b|\u00b5g|\biu\b|therapy|training|exercise|diet\b|nutrition|cbt\b"
    r"|usual\s+care|comparator|drug|capsule|tablet|infusion|melatonin|caffeine",
    re.IGNORECASE)


def _role_columns(header: Sequence[str]) -> Dict[str, List[int]]:
    """Spaltenrollen aus dem Kopf (n, sd, se, ci) - nur diese vier."""
    from ..research.jats_tables import _col_semantics

    roles: Dict[str, List[int]] = {"n": [], "sd": [], "se": [], "ci": []}
    for index, role in _col_semantics(list(header or [])).items():
        if role in roles:
            roles[role].append(index)
    # "Melatonin n" ist eine Fallzahlspalte, auch ohne "n = 25" im Kopf; die
    # Rollenlogik des Tabellenlesers erkennt nur die Schreibweise mit Wert.
    for index, head in enumerate(list(header or [])):
        if any(index in roles[key] for key in roles):
            continue
        text = str(head or "")
        if re.search(r"\bn\b\s*\)?\s*$", text, re.IGNORECASE):
            roles["n"].append(index)
            continue
        # "Melatonin No of children" ist ebenfalls eine Fallzahlspalte; die
        # Schreibweise mit "n = 25" deckt die Rollenlogik oben nicht ab.
        if re.search(r"\b(?:no\.?|number)\s+of\s+"
                     r"(?:children|patients|participants|subjects)\b",
                     text, re.IGNORECASE):
            roles["n"].append(index)
    for key in roles:
        roles[key].sort()
    return roles


def _role_for(roles: Dict[str, List[int]], index: int) -> str:
    for key in ("sd", "se", "ci"):
        if index in roles.get(key, []):
            return key
    return ""


# Eine Zelle, die nur eine Zahl traegt. Fuer die Paarbildung aus getrennten
# Spalten ist das die Bedingung: "38.2 (4.1)" ist ein Arm in einer Zelle,
# "38.2" ist ein Mittelwert, der seine Streuung in der Nachbarspalte hat.
_BARE_NUMBER = re.compile(r"^\s*[-+\u2212\u2013]?\d+(?:[.,]\d+)?\s*$")


def _paired_arms(header: Sequence[str], cells: Sequence[str],
                 roles: Dict[str, List[int]]) -> List[Tuple[int, float, float, str]]:
    """Arme aus getrennten Mittelwert- und Streuungsspalten.

    Kopf ``Melatonin Mean | Melatonin SD | Placebo Mean | Placebo SD``: die
    Mittelwertspalte traegt nur die Zahl, die Streuung steht daneben. Gepaart
    wird nur, wenn beide Zellen reine Zahlen sind und der Kopf die rechte
    Spalte als SD oder SE benennt. Ein Bereich in der Streuungsspalte ist ein
    CI und braucht eine Fallzahl; er wird hier nicht gepaart, sondern bleibt
    dem Zwei-Zellen-Fall vorbehalten.
    """
    pairs: List[Tuple[int, float, float, str]] = []
    spreads = [index for index in sorted((roles.get("sd") or []) + (roles.get("se") or []))]
    for index in spreads:
        if index < 1 or index >= len(cells):
            continue
        spread_cell = str(cells[index] or "")
        mean_cell = str(cells[index - 1] or "")
        if not _BARE_NUMBER.match(spread_cell) or not _BARE_NUMBER.match(mean_cell):
            continue
        spread, mean = parse_number(spread_cell), parse_number(mean_cell)
        if spread is None or mean is None or spread <= 0:
            continue
        head = str(header[index - 1]) if header and index - 1 < len(header) else ""
        if (_RATIO_RE.search(head) or _DIRECT_EFFECT_RE.search(head)
                or _MEDIAN_RE.search(head)):
            continue
        kind = "sd" if index in (roles.get("sd") or []) else "se"
        pairs.append((index - 1, mean, spread, kind))
    return pairs


def arms_from_row(header: Sequence[str], cells: Sequence[str],
                  n_per_arm: Optional[Sequence[int]] = None,
                  row_group: str = "", spread_hint: str = ""
                  ) -> Tuple[List[ArmStats], str]:
    """Zwei Arme aus einer Tabellenzeile, oder ([], Grund).

    Erwartet je Arm eine Spalte mit "Mittelwert (Streuung)" und eine
    Fallzahl - entweder als eigene n-Spalte je Arm, als "n = 25" im
    Spaltenkopf oder als ``n_per_arm`` von aussen. Eine einzelne
    Gesamt-Fallzahl reicht nicht: g braucht n je Arm.
    """
    if not cells or len(cells) < 2:
        return [], _REASONS["few_columns"]
    roles = _role_columns(header or [])
    n_cols = set(roles.get("n") or [])

    # Eine Armspalte ist die, deren ZELLE Mittelwert plus eindeutige
    # Streuung traegt ("10.0 (2.0)", "16.7 (11.6 to 22.0)"). Reine
    # Zahlenspalten (n, p-Wert) fallen dabei von selbst heraus; eine
    # Spalte "Mean (SD)" ist ein Arm, kein Streuungsfeld.
    chosen: List[Tuple[int, float, float, str]] = []
    skipped_median = False
    skipped_ratio = False
    for index, cell in enumerate(cells):
        if index in n_cols:
            continue
        header_cell = str(header[index]) if header and index < len(header) else ""
        if _MEDIAN_RE.search(header_cell):
            # Median mit IQR ist keine Mittelwertdifferenz: die SMD-Formel
            # gilt fuer Mittelwerte, ein Median braucht einen anderen
            # Schaetzer. Nicht umdeuten, sondern auslassen.
            skipped_median = True
            continue
        if _DIRECT_EFFECT_RE.search(header_cell):
            # "Hedges g (95% CI)" ist schon ein Effekt - den liest der
            # Effekt-Extraktor, der Arm-Rechner darf ihn nicht als Arm
            # missverstehen.
            continue
        if _RATIO_RE.search(header_cell):
            # "OR (95% CI)" ist ein direkt berichtetes Verhaeltnis; es in
            # zwei Arme zu zerlegen waere eine Rueckrechnung ohne Daten.
            skipped_ratio = True
            continue
        parsed = parse_mean_spread(
            cell, role=_role_for(roles, index) or spread_hint)
        if not parsed:
            continue
        mean, spread, kind = parsed
        chosen.append((index, mean, spread, kind))

    # Genau zwei Arme. Eine Zeile mit vier oder acht Wertspalten (Gruppen,
    # Zeitpunkte, Geschlechter) ist kein Zwei-Arm-Vergleich; zwei beliebige
    # davon zu greifen wuerde eine Differenz erfinden, die niemand berichtet.
    if len(chosen) < 2:
        # Getrennte Spalten: Mittelwert hier, Streuung daneben. Nur ergaenzen,
        # nie ersetzen - eine Zelle, die schon Mittelwert und Streuung traegt,
        # bleibt die belegte Quelle.
        for pair in _paired_arms(header, cells, roles):
            if all(pair[0] != column for column, _m, _s, _k in chosen):
                chosen.append(pair)

    if not chosen and skipped_median:
        return [], _REASONS["median"]
    if not chosen and skipped_ratio:
        return [], _REASONS["ratio"]
    if len(chosen) < 2:
        return [], _REASONS["no_arm"]
    if len(chosen) > 2:
        return [], _REASONS["arm_count"]
    chosen = chosen[:2]

    from .baseline_columns import baseline_violation
    violation = baseline_violation(
        header or [], [column for column, _m, _s, _k in chosen], row_group)
    if violation:
        return [], violation

    labels = []
    for index, _m, _s, _k in chosen:
        text = (str(header[index]).strip()
                if header and index < len(header) else "")
        labels.append(text or f"Spalte {index + 1}")

    arms: List[ArmStats] = []
    for position, (index, mean, spread, kind) in enumerate(chosen):
        if n_per_arm and position < len(n_per_arm):
            n = int(n_per_arm[position])
        else:
            n = _n_for_column(header or [], cells, index, roles, position)
        if not n or n < _MIN_ARM_N:
            return [], _REASONS["no_n"]
        if kind == "ci":
            ci = _split_ci(cells[index])
            if not ci:
                return [], _REASONS["bad_spread"]
            _m, low, high = ci
            sd = sd_from_ci(low, high, n)
            source = "ci"
        elif kind == "se":
            sd = sd_from_se(spread, n)
            source = "se"
        else:
            sd, source = spread, "sd"
        if not sd or sd <= 0:
            return [], _REASONS["bad_sd"]
        arms.append(ArmStats(label=labels[position], n=n, mean=mean, sd=sd,
                             sd_source=source))
    return arms, ""


def _named_group(label: str) -> bool:
    """True, wenn das Arm-Etikett eine Gruppe benennt (nicht nur Statistik)."""
    rest = _GENERIC_LABEL.sub(" ", str(label or ""))
    return bool(rest.strip(" -_/"))


def _n_for_column(header: Sequence[str], cells: Sequence[str], index: int,
                  roles: Dict[str, List[int]],
                  arm_position: int = 0) -> Optional[int]:
    """Fallzahl fuer eine Armspalte finden - nie raten.

    Reihenfolge: eigene n-Spalten in Arm-Reihenfolge (zwei Arme, zwei
    n-Spalten), "n = 25" im Spaltenkopf, "n=25" in der Zelle. Eine einzelne
    n-Spalte ist die Gesamt-Fallzahl und wird hier nicht verwendet.
    """
    n_cols = roles.get("n") or []
    if len(n_cols) >= 2 and arm_position < len(n_cols):
        value = parse_number(cells[n_cols[arm_position]])
        if value and value >= _MIN_ARM_N:
            return int(value)
    header_cell = str(header[index] if index < len(header) else "")
    match = re.search(r"\(?\s*n\s*=\s*(\d+)", header_cell, re.IGNORECASE)
    if match:
        return int(match.group(1))
    cell = str(cells[index] if index < len(cells) else "")
    match = re.search(r"\bn\s*=\s*(\d+)", cell, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def convert_row(header: Sequence[str], cells: Sequence[str], outcome: str = "",
                quote: str = "", n_per_arm: Optional[Sequence[int]] = None,
                caption: str = "", row_group: str = "",
                spread_hint: str = "") -> Dict:
    """Eine Tabellenzeile umrechnen; Ergebnis ist speicherfertig oder leer.

    Der ``quote`` muss die Zeile woertlich enthalten - der Aufrufer prueft
    das gegen den gespeicherten Text, bevor er speichert.

    Abgelehnt wird zusaetzlich, was kein Behandlungseffekt ist: eine
    Baseline-Zeile (Tag 0, ``pre-...``) und ein Vergleich ohne
    Interventionsarm (aktive vs. inaktive Kinder, Patienten vs. Kontrollen).
    Der Zeitpunkt der Zeile (``Day 30``, ``Week 4``) wird als ``time_point``
    mitgefuehrt, statt in der Tabellen-Caption zu verschwinden.
    """
    header_cells = list(header or [])
    row_cells = list(cells or [])

    time_point = ""
    for index, head in enumerate(header_cells):
        if not _TIME_COLUMN.match(str(head or "").strip()):
            continue
        if index >= len(row_cells):
            continue
        value = str(row_cells[index] or "").strip()
        if not value:
            continue
        if _BASELINE_VALUE.match(value):
            return {"ok": False, "reason": _REASONS["baseline"]}
        time_point = f"{str(head).strip().lower()} {value}"

    first = str(row_cells[0] or "").strip() if row_cells else ""
    if _BASELINE_VALUE.match(first):
        return {"ok": False, "reason": _REASONS["baseline"]}
    if not time_point and _TIMEPOINT_LABEL.match(first):
        time_point = first.lower()

    # Outcome aus der Zeile selbst, nicht aus der Caption: eine Zelle
    # "Day 0" ist ein Zeitpunkt, kein Endpunkt.
    derived = ""
    for cell in row_cells:
        text = str(cell or "").strip()
        if not text or not re.search(r"[A-Za-z]", text):
            continue
        if _BASELINE_VALUE.match(text) or _TIMEPOINT_LABEL.match(text):
            continue
        derived = text[:90]
        break

    arms, reason = arms_from_row(header, cells, n_per_arm,
                                  row_group=row_group, spread_hint=spread_hint)
    if not arms:
        return {"ok": False, "reason": reason}
    named = [arm for arm in arms if _named_group(str(arm.label or ""))]
    if named and not any(_INTERVENTION_ARM.search(str(arm.label or ""))
                         for arm in named):
        return {"ok": False, "reason": _REASONS["cross_sectional"]}
    effect = smd_from_arms(arms[0], arms[1])
    if effect is None:
        return {"ok": False, "reason": _REASONS["bad_sd"]}
    payload = effect.to_dict()
    payload.update({
        "ok": True,
        "outcome": outcome or derived or (caption or "")[:90],
        "quote": quote,
        "time_point": time_point,
    })
    return payload


# --------------------------------------------------------------------------
# Speichern - nur vollstaendig belegte Zeilen
# --------------------------------------------------------------------------

def store_arm_level_effects(db, source_id: str, source_text_id: str,
                            document_text: str,
                            candidates: Iterable[Dict],
                            extractor: str = ARM_LEVEL_VERSION
                            ) -> Tuple[List[Dict], List[Dict]]:
    """Vollstaendige, belegte Zeilen speichern; den Rest zurueckmelden.

    Gespeichert wird nur, wenn
      * die Umrechnung gelungen ist (beide Arme mit n und Streuung),
      * das Zitat woertlich im gespeicherten Dokument steht (locate_quote)
        und
      * die Werte die Plausibilitaetspruefung des Effekt-Stores bestehen.

    Nichts wird ergaenzt, interpoliert oder mit einer Gesamt-Fallzahl
    aufgefuellt.
    """
    import datetime as _dt
    import json as _json
    import uuid as _uuid

    from ..research.fulltext import locate_quote
    from .extraction import check_plausibility

    stored: List[Dict] = []
    rejected: List[Dict] = []
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()

    for candidate in candidates:
        if not candidate.get("ok"):
            rejected.append({"quote": candidate.get("quote", ""),
                             "reason": candidate.get("reason", "unbekannt")})
            continue
        quote = str(candidate.get("quote") or "")
        span = locate_quote(document_text, quote) if (quote and document_text) else None
        if not span:
            rejected.append({"quote": quote, "reason": "Zitat nicht im Dokument"})
            continue
        row = {
            "id": _uuid.uuid4().hex,
            "source_id": source_id,
            "outcome": str(candidate.get("outcome") or ""),
            "outcome_key": str(candidate.get("outcome") or ""),
            "comparison": " vs. ".join(
                a["label"] for a in candidate.get("arms") or []) or "Arm 1 vs. Arm 2",
            "effect_type": "g",
            "effect": float(candidate["effect"]),
            "se": float(candidate["se"]),
            "ci_low": None,
            "ci_high": None,
            "ci_level": 0.95,
            "n": int(candidate["n"]),
            "design": "",
            "population": "",
            "direction": str(candidate.get("direction") or ""),
            "unit": "Hedges g",
            "quote": quote,
            "quote_start": span.start,
            "quote_end": span.end,
            "source_text_id": source_text_id,
            "extractor": extractor,
            "extraction_pass": 1,
            "disputed": 0,
            "rejection_reason": "",
            "adjusted": -1,
            "time_point": str(candidate.get("time_point") or ""),
            "moderators": _json.dumps(
                {**(candidate.get("moderators") or {}),
                 "arms": candidate.get("arms") or []},
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

"""Deterministischer Leser fuer Veraenderungswerte (mean change +- SD).

Zwei Faelle, klar getrennt:

**A - gemeldete Veraenderung.** Der Satz nennt die Differenz selbst:
``"SOL decrease was -13.8 +- 6.1 min with melatonin (n = 20) and
-3.6 +- 7.4 min with placebo (n = 20)"``. Dann ist die Streuung der
Veraenderung direkt gegeben, und die Korrelation zwischen den Messzeit-
punkten spielt **keine** Rolle. g wird exakt gerechnet.

**B - Prae- und Post-Werte.** Der Satz nennt beide Zeitpunkte:
``"SOL decreased from 32.1 +- 9.4 to 18.3 +- 7.2 min in the melatonin
group (n = 20)"``. Die Veraenderung ist ``post - pre``, aber ihre
Streuung ist

    SD_change = sqrt(SD_pre^2 + SD_post^2 - 2 * rho * SD_pre * SD_post)

und ``rho`` steht in fast keinem Papier. Es wird deshalb **nicht** still
gesetzt: der gespeicherte Wert ist der Primaerwert bei ``rho = 0.5``
(offengelegt im Datensatz), und jede Zeile traegt zusaetzlich ein
Sensitivitaetsgrid ueber ``rho`` in 0.0, 0.3, 0.5, 0.7, 0.9. Wer die
Zahlen poolt, sieht damit, wie stark das Ergebnis an der Annahme haengt.

Abgelehnt wird alles, was auch der Post-Wert-Leser ablehnt: SEM/SE,
Median/IQR, Tabellen- und Zitationsreste, Designsaetze, demografische
Outcomes und Vergleiche ohne Interventionsarm. Gespeichert wird ueber
denselben Store wie die anderen Arm-Leser, also nur mit woertlichem
Zitatbeleg und Plausibilitaetspruefung.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .arm_level import (
    cohens_d,
    hedges_correction,
    parse_number,
    se_of_g,
    store_arm_level_effects,
)
from .arm_text import (
    _CITATION,
    _DEMOGRAPHIC,
    _DESIGN_CUE,
    _INTERVENTION_ARM,
    _MEDIAN_CUE,
    _N_EQUALS,
    _clean_label,
    _label_ok,
    _named_group,
    _outcome_from,
    arm_mentions,
    split_sentences,
)

CHANGE_VERSION = "arm-change/1"
DEFAULT_RHO = 0.5
RHO_GRID = (0.0, 0.3, 0.5, 0.7, 0.9)

_UNIT = r"(?:min|mins|minutes|h|hrs|hours|%|points?|s|sec|ms)"
_SEP = r"(?:\u00b1|\+/-|\+-)"

# "from 32.1 +- 9.4 to 18.3 +- 7.2"
_PREPOST = re.compile(
    rf"from\s+(?P<pre_m>[-+\u2212\u2013]?\d+(?:[.,]\d+)?)\s*(?:{_UNIT})?\s*{_SEP}\s*"
    rf"(?P<pre_sd>\d+(?:[.,]\d+)?)"
    rf"(?:\s*(?:{_UNIT}))?\s*(?:to|zu|\u2192|->)\s*"
    rf"(?P<post_m>[-+\u2212\u2013]?\d+(?:[.,]\d+)?)\s*(?:{_UNIT})?\s*{_SEP}\s*"
    rf"(?P<post_sd>\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)

# Ein Veraenderungswort irgendwo im Satz genuegt; die Zahlen selbst werden
# wie beim Text-Leser ueber "mean +- SD" erkannt. Sonst scheitert der zweite
# Arm, weil das Cue-Wort nur einmal dasteht ("change was -13.8 +- 6.1 ...
# and -3.6 +- 7.4").
_CHANGE_CUE_TEXT = re.compile(
    r"\bchange[sd]?\b|\bdecreas\w+|\bincreas\w+|\breduc\w+|\bimproved?\b"
    r"|\bdelta\b|\bdifferences?\b|\bdeclin\w+",
    re.IGNORECASE,
)

_NEGATIVE = re.compile(r"decreas|reduc|lower|shorten|improv|fall|fell|drop",
                       re.IGNORECASE)


@dataclass
class ChangeArm:
    """Ein Arm mit Veraenderung und Fallzahl."""

    label: str
    n: int
    delta: float
    sd_reported: Optional[float] = None
    pre_sd: Optional[float] = None
    post_sd: Optional[float] = None
    detail: Dict = field(default_factory=dict)

    def sd_change(self, rho: float = DEFAULT_RHO) -> Optional[float]:
        """SD der Veraenderung - exakt, wenn berichtet, sonst mit rho."""
        if self.sd_reported is not None:
            return self.sd_reported
        if self.pre_sd is None or self.post_sd is None:
            return None
        variance = (self.pre_sd ** 2 + self.post_sd ** 2
                    - 2.0 * rho * self.pre_sd * self.post_sd)
        return math.sqrt(variance) if variance > 0 else None


def smd_of_change(arm1: ChangeArm, arm2: ChangeArm,
                  rho: float = DEFAULT_RHO) -> Optional[Dict]:
    """Hedges g fuer die Differenz der Veraenderungen."""
    sd1, sd2 = arm1.sd_change(rho), arm2.sd_change(rho)
    if not sd1 or not sd2:
        return None
    d = cohens_d(arm1.delta, sd1, arm1.n, arm2.delta, sd2, arm2.n)
    if d is None:
        return None
    correction = hedges_correction(arm1.n, arm2.n)
    g = correction * d
    se = se_of_g(g, arm1.n, arm2.n)
    if not math.isfinite(se) or se <= 0:
        return None
    return {"g": g, "se": se, "d": d, "correction": correction,
            "sd1": sd1, "sd2": sd2}


def sensitivity(arm1: ChangeArm, arm2: ChangeArm) -> List[Dict]:
    """g ueber das rho-Grid - die offengelegte Abhaengigkeit."""
    rows: List[Dict] = []
    for rho in RHO_GRID:
        result = smd_of_change(arm1, arm2, rho)
        if result:
            rows.append({"rho": rho, "g": round(result["g"], 6),
                         "se": round(result["se"], 6)})
    return rows


# --------------------------------------------------------------------------
# Saetze
# --------------------------------------------------------------------------

_REASONS = {
    "no_change": "kein Veraenderungswert im Satz",
    "arm_count": "nicht genau zwei Arme mit Veraenderung im Satz",
    "no_n": "Fallzahl je Arm fehlt",
    "no_label": "Arm-Etikett fehlt oder ist keine Gruppe",
    "same_label": "beide Arme tragen dasselbe Etikett",
    "cross_sectional": "kein Interventionsarm - Gruppenvergleich ohne Intervention",
    "outcome": "kein Outcome vor dem ersten Arm",
    "demographic": "demografische Angabe statt Outcome",
    "median": "Median/IQR statt Mittelwert mit SD",
    "explained": "Streuung als SEM/SE im Satz (nicht SD)",
    "artifact": "Tabellen-/Zitationsrest statt Ergebnissatz",
    "design": "Stichproben- oder Designbeschreibung statt Ergebnis",
    "bad_sd": "Streuung der Veraenderung nicht positiv",
}


def _nearest_n(text: str, start: int, end: int,
               used: set) -> Optional[Tuple[int, int]]:
    """Naechste freie "n = 20"-Stelle zu einem Wertebereich."""
    numbers = [(m.start(), int(m.group(1))) for m in _N_EQUALS.finditer(text)]
    free = [i for i in range(len(numbers)) if i not in used]
    if not free:
        return None
    def distance(index: int) -> int:
        n_start = numbers[index][0]
        if n_start >= end:
            return n_start - end
        if n_start + 8 <= start:
            return start - (n_start + 8)
        return 0
    index = min(free, key=distance)
    return index, numbers[index][1]


def _arms(text: str) -> Tuple[List[ChangeArm], str, str, int]:
    """(Arme, Modell, Ablehnungsgrund, Position des ersten Werts)."""
    used: set = set()
    pre_post = list(_PREPOST.finditer(text))
    if pre_post:
        if len(pre_post) != 2:
            return [], "prepost", _REASONS["arm_count"], pre_post[0].start()
        arms: List[ChangeArm] = []
        for match in pre_post:
            found = _nearest_n(text, match.start(), match.end(), used)
            if not found:
                return [], "prepost", _REASONS["no_n"], pre_post[0].start()
            index, n = found
            used.add(index)
            pre_m = parse_number(match.group("pre_m"))
            pre_sd = parse_number(match.group("pre_sd"))
            post_m = parse_number(match.group("post_m"))
            post_sd = parse_number(match.group("post_sd"))
            if None in (pre_m, pre_sd, post_m, post_sd):
                return [], "prepost", _REASONS["bad_sd"], pre_post[0].start()
            label = ""
            arms.append(ChangeArm(
                label=label, n=n, delta=post_m - pre_m,
                pre_sd=pre_sd, post_sd=post_sd,
                detail={"pre": pre_m, "post": post_m,
                        "pre_sd": pre_sd, "post_sd": post_sd},
            ))
        # Etikett steht hinter dem Zahlenpaar ("... to 18.3 +- 7.2 min in
        # the melatonin group (n = 20)") - dort nachlesen.
        for position, match in enumerate(pre_post):
            found_n = list(_N_EQUALS.finditer(text))
            if not found_n:
                continue
            nearest = min(found_n,
                          key=lambda m: abs(m.start() - match.end()))
            label = _clean_label(text[max(0, nearest.start() - 70):nearest.start()])
            if _named_group(label):
                arms[position].label = label
        return arms, "prepost", "", pre_post[0].start()

    if not _CHANGE_CUE_TEXT.search(text):
        return [], "", _REASONS["no_change"], 0
    mentions = arm_mentions(text)
    if len(mentions) != 2:
        return [], "reported", _REASONS["arm_count"], 0
    negative = bool(_NEGATIVE.search(text))
    arms = []
    for mention in mentions:
        if not mention.n:
            return [], "reported", _REASONS["no_n"], 0
        delta = mention.mean
        if negative and delta > 0:
            # "decreased by 13.8" berichtet den Betrag der Abnahme.
            delta = -delta
        arms.append(ChangeArm(label=mention.label, n=mention.n, delta=delta,
                              sd_reported=mention.sd,
                              detail={"reported_change": delta, "sd": mention.sd}))
    return arms, "reported", "", mentions[0].start


def convert_sentence(sentence: str, quote: str = "") -> Dict:
    """Ein Satz -> speicherfertiger Kandidat oder Ablehnung mit Grund."""
    text = " ".join(str(sentence or "").split())
    if not text or "|" in text or text.startswith("|"):
        return {"ok": False, "reason": _REASONS["artifact"]}
    if _MEDIAN_CUE.search(text):
        return {"ok": False, "reason": _REASONS["median"]}
    if re.search(r"\bSEM\b|standard\s+error|\bSE\b", text):
        return {"ok": False, "reason": _REASONS["explained"]}
    if _CITATION.search(text):
        return {"ok": False, "reason": _REASONS["artifact"]}
    if _DESIGN_CUE.search(text):
        return {"ok": False, "reason": _REASONS["design"]}

    arms, model, reason, first = _arms(text)
    if not arms:
        return {"ok": False, "reason": reason}
    if any(not arm.n or arm.n < 2 for arm in arms):
        return {"ok": False, "reason": _REASONS["no_n"]}

    outcome = _outcome_from(text, first)
    if len(outcome) < 2:
        return {"ok": False, "reason": _REASONS["outcome"]}
    if _DEMOGRAPHIC.search(outcome):
        return {"ok": False, "reason": _REASONS["demographic"]}

    labels = [arm.label for arm in arms]
    if any(not _label_ok(label) for label in labels):
        return {"ok": False, "reason": _REASONS["no_label"]}
    if labels[0].lower() == labels[1].lower():
        return {"ok": False, "reason": _REASONS["same_label"]}
    if not any(_INTERVENTION_ARM.search(label) for label in labels):
        return {"ok": False, "reason": _REASONS["cross_sectional"]}

    primary = smd_of_change(arms[0], arms[1], DEFAULT_RHO)
    if primary is None:
        return {"ok": False, "reason": _REASONS["bad_sd"]}

    sensitivity_rows = (sensitivity(arms[0], arms[1])
                        if model == "prepost" else [])
    payload = {
        "ok": True,
        "outcome": outcome,
        "quote": quote or text,
        "time_point": "",
        "effect": primary["g"],
        "se": primary["se"],
        "n": arms[0].n + arms[1].n,
        "direction": (f"negatives g = staerkere Abnahme in '{arms[0].label}' "
                      f"als in '{arms[1].label}'"),
        "arms": [
            {"label": arm.label, "n": arm.n, "mean": round(arm.delta, 6),
             "sd": round(arm.sd_change(DEFAULT_RHO) or 0.0, 6),
             "sd_source": ("change-sd" if model == "reported"
                           else f"change-sd(rho={DEFAULT_RHO})")}
            for arm in arms
        ],
        "moderators": {
            "change_model": model,
            "rho": None if model == "reported" else DEFAULT_RHO,
            "rho_assumed": model == "prepost",
            "sensitivity": sensitivity_rows,
            "arms_detail": [arm.detail for arm in arms],
        },
    }
    return payload


def change_candidates(text: str) -> List[Dict]:
    """Alle Saetze eines Dokuments pruefen; Tabellenzeilen ueberspringen."""
    candidates: List[Dict] = []
    for line in (text or "").splitlines():
        if line.count("|") >= 2:
            continue
        for _start, _end, sentence in split_sentences(line):
            candidate = convert_sentence(sentence)
            if candidate.get("ok"):
                candidate["quote"] = sentence
                candidates.append(candidate)
    return candidates


def store_change_effects(db, source_id: str, source_text_id: str,
                         document_text: str, candidates):
    """Speichern mit eigener Extraktor-Kennung (arm-change/1)."""
    return store_arm_level_effects(
        db, source_id, source_text_id, document_text, candidates,
        extractor=CHANGE_VERSION)

"""Deterministischer Fliesstext-Arm-Leser: "mean +- SD" mit n im Satz.

Die Tabellen-Leser finden nur, was als Zwei-Arm-Tabelle dasteht. In
Schlafstudien stehen die Gruppenmittelwerte aber meist im Ergebnistext:
"sleep onset latency was 18.3 +- 7.2 min in the melatonin group (n = 20)
and 27.9 +- 8.1 min in the placebo group (n = 20)".

Dieses Modul liest genau diese Form - ohne Modell, ohne Schaetzung. Es
akzeptiert nur Saetze, in denen

  * genau zwei Mittelwerte mit ausdruecklicher Streuung stehen
    ("18.3 +- 7.2", "18.3 (SD 7.2)", "18.3 min +- 7.2"),
  * jeder Mittelwert eine Fallzahl traegt ("n = 20" im selben Satzteil),
  * beide Mittelwerte ein Arm-Etikett tragen und mindestens eines
    Interventionsvokabular enthaelt,
  * kein Baseline- oder Veraenderungsmuster steht ("baseline",
    "from 32.1 to 18.3", "change", "delta") - solche Saetze berichten
    keinen Gruppenvergleich, sondern einen Verlauf,
  * kein Median steht (IQR ist keine Mittelwertdifferenz).

Alles andere wird mit Grund abgelehnt. Gespeichert wird ueber denselben
Store wie der Tabellen-Rechner, also nur mit woertlichem Zitatbeleg und
Plausibilitaetspruefung.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .arm_level import (
    ARM_LEVEL_VERSION,
    ArmStats,
    _INTERVENTION_ARM,
    _named_group,
    parse_number,
    smd_from_arms,
    store_arm_level_effects,
)

TEXT_ARM_VERSION = "arm-text/1"

# --------------------------------------------------------------------------
# Saetze
# --------------------------------------------------------------------------

_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[])")
# Nach diesen Kuerzeln beginnt kein neuer Satz ("18.3 vs. 27.9").
_ABBREV = {"vs", "e.g", "i.e", "fig", "no", "resp", "approx", "ca", "dr", "al",
           "cf", "et"}


def split_sentences(text: str) -> List[Tuple[int, int, str]]:
    """(Start, Ende, Satz) - deterministisch, ohne Satzmodell.

    Ein Punkt nach einem Kuerzel ("vs.", "e.g.") oder innerhalb einer Zahl
    ist keine Satzgrenze; die Grenze verlangt Leerraum und einen folgenden
    Grossbuchstaben, eine Ziffer oder eine Klammer.
    """
    spans: List[Tuple[int, int, str]] = []
    start = 0
    for match in _BOUNDARY.finditer(text or ""):
        end = match.start()
        chunk = text[start:end]
        tail = chunk.rstrip().rsplit(" ", 1)[-1].lower().rstrip(".")
        if tail in _ABBREV:
            continue
        if chunk.strip():
            spans.append((start, end, chunk))
        start = match.end()
    rest = (text or "")[start:]
    if rest.strip():
        spans.append((start, len(text), rest))
    return spans


# --------------------------------------------------------------------------
# Mittelwert und Streuung im Satz
# --------------------------------------------------------------------------

_SPREAD = re.compile(
    r"(?P<mean>[-+\u2212\u2013]?\d+(?:[.,]\d+)?)"
    r"(?:\s*(?:min|mins|minutes|h|hrs|hours|%|points?|ms|sec|s))?"
    r"\s*(?:\u00b1|\+/-|\+-)\s*"
    r"(?P<sd>\d+(?:[.,]\d+)?)"
)
_SD_LABELLED = re.compile(
    r"(?P<mean>[-+\u2212\u2013]?\d+(?:[.,]\d+)?)"
    r"(?:\s*(?:min|mins|minutes|h|hrs|hours|%|points?|ms|sec|s))?"
    r"\s*\(\s*SD\s*[=:]?\s*(?P<sd>\d+(?:[.,]\d+)?)\s*\)",
    re.IGNORECASE,
)

_N_EQUALS = re.compile(r"\bn\s*=\s*(\d{1,4})\b", re.IGNORECASE)
_PAREN = re.compile(r"\([^()]*\)")
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9\-/']*")
_LEAD = {
    "in", "the", "a", "an", "of", "with", "and", "versus", "vs", "than",
    "for", "at", "to", "after", "during", "was", "were", "by", "on", "from",
    "group", "groups", "arm", "arms", "condition", "compared",
    "min", "mins", "minutes", "h", "hrs", "hours", "point", "points",
    "mean", "respectively",
}

# "pre-treatment", "pre-dose" und ein alleinstehendes "pre" sind der
# Zustand vor der Intervention. "presence" oder "pressure" sind es nicht -
# das Muster verlangt deshalb einen Trenner nach "pre".
_CHANGE_CUE = re.compile(
    r"\bbaseline\b|\bpre[-\s]\w+|\bpre\b"
    r"|\bfrom\s+[-+\u2212]?\d|\bchange[sd]?\b"
    r"|\bdelta\b|\bdifference\s+in\s+change\b|\bimproved?\s+from\b"
    r"|\bdecreas\w+\s+from\b|\bincreas\w+\s+from\b",
    re.IGNORECASE,
)
# Reste aus dem Tabellen-Flachtext, Zitationsspalten und
# Stichprobenbeschreibungen sind keine Ergebnissaetze. Sie tragen zwar
# "mean +- SD", aber die Zahlen sind Alter, BMI oder Zeilen aus einer
# Uebersichtstabelle - kein Behandlungseffekt.
_CITATION = re.compile(r"\bet\s+al\b|\[\s*\d+\s*\]")
_DESIGN_CUE = re.compile(
    r"were\s+(?:randomly\s+)?(?:assigned|randomi[sz]ed|enrolled|recruited)"
    r"|enrolled\s+and\s+randomi[sz]ed|study\s+characteristics"
    r"|participants\s+were|subjects\s+were",
    re.IGNORECASE,
)
_DEMOGRAPHIC = re.compile(
    r"\b(?:age|ages|bmi|sex|male|males|female|females|weight|height|"
    r"education|income|ethnicity)\b",
    re.IGNORECASE,
)
_TRAIL_STOP = {
    "was", "were", "is", "are", "had", "by", "of", "in", "for", "with",
    "to", "at", "showed", "averaged", "advanced", "decreased", "increased",
    "compared", "and", "remained", "reported", "lower", "higher", "greater",
    "shorter", "longer", "than", "also", "significantly",
}
_MEDIAN_CUE = re.compile(r"\bmedian\b|\bIQR\b|interquartile", re.IGNORECASE)
_TIMEPOINT = re.compile(r"\b(day|week|month)\s*(\d{1,3})\b", re.IGNORECASE)


@dataclass
class ArmMention:
    label: str
    n: Optional[int]
    mean: float
    sd: float
    start: int = 0


def _clean_label(window: str) -> str:
    """Arm-Etikett aus dem Text vor dem Mittelwert.

    Klammern mit Zahlen (Fallzahl, Dosis, p-Wert) fallen weg; danach zaehlen
    nur die letzten Woerter, damit "the sleep onset latency was 18.3" nicht
    als Etikett durchgeht.
    """
    text = _PAREN.sub(" ", window or "")
    text = re.sub(r"[;:,]", " ", text)
    words = _WORD.findall(text)[-6:]
    for index in range(len(words) - 1, 0, -1):
        if words[index].lower() in ("in", "for", "with", "among", "between",
                                    "and", "versus", "vs", "than", "compared"):
            words = words[index + 1:]
            break
    while words and words[0].lower() in _LEAD:
        words.pop(0)
    return " ".join(words).strip()


def _n_before(window: str) -> Optional[int]:
    """Fallzahl aus dem Text vor dem Mittelwert - nur die naechste "n = 20"."""
    matches = list(_N_EQUALS.finditer(window or ""))
    if not matches:
        return None
    return int(matches[-1].group(1))


def _distance(spread_start: int, spread_end: int, n_start: int) -> int:
    """Abstand zwischen einer Streuungsstelle und einer "n = 20"-Stelle."""
    n_end = n_start + 8
    if n_start >= spread_end:
        return n_start - spread_end
    if n_end <= spread_start:
        return spread_start - n_end
    return 0


def arm_mentions(sentence: str) -> List[ArmMention]:
    """Alle "Mittelwert +- SD"-Stellen eines Satzes mit Etikett und Fallzahl.

    Etikett und Fallzahl gehoeren zusammen: das Etikett steht direkt vor
    seiner ``n = 20``-Angabe. Darum wird jede Streuungsstelle der naechsten
    Fallzahl zugeordnet und das Etikett aus dem Text davor gelesen - so
    funktionieren beide Reihenfolgen, "melatonin (n = 20): 18.3 +- 7.2"
    und "18.3 +- 7.2 min in the melatonin group (n = 20)".
    """
    text = sentence or ""
    spreads: List[Tuple[int, int, float, float]] = []
    for match in _SPREAD.finditer(text):
        mean = parse_number(match.group("mean"))
        sd = parse_number(match.group("sd"))
        if mean is None or sd is None or sd <= 0:
            continue
        spreads.append((match.start("mean"), match.end("sd"), mean, sd))
    for match in _SD_LABELLED.finditer(text):
        start, end = match.start("mean"), match.end("sd")
        if any(low <= start < high for low, high, _m, _s in spreads):
            # Der SD-Wert einer bereits gelesenen Stelle ist kein zweiter Arm.
            continue
        mean = parse_number(match.group("mean"))
        sd = parse_number(match.group("sd"))
        if mean is None or sd is None or sd <= 0:
            continue
        spreads.append((start, end, mean, sd))
    spreads.sort()

    numbers = [(m.start(), int(m.group(1))) for m in _N_EQUALS.finditer(text)]
    used: set = set()
    mentions: List[ArmMention] = []
    for start, end, mean, sd in spreads:
        if not numbers:
            mentions.append(ArmMention(label="", n=None, mean=mean, sd=sd, start=start))
            continue
        free = [i for i in range(len(numbers)) if i not in used]
        if not free:
            # Eine Fallzahl kann nicht zwei Arme belegen.
            mentions.append(ArmMention(label="", n=None, mean=mean, sd=sd, start=start))
            continue
        index = min(free, key=lambda i: _distance(start, end, numbers[i][0]))
        n_start, n = numbers[index]
        used.add(index)
        label = _clean_label(text[max(0, n_start - 70):n_start])
        mentions.append(ArmMention(label=label, n=n, mean=mean, sd=sd, start=start))
    return mentions


def _outcome_from(sentence: str, first_mention: int) -> str:
    """Outcome = das letzte Substantiv vor dem ersten Arm.

    "Following melatonin treatment (n = 23), DLMO was advanced by 0.73 +- 1.21"
    liefert "DLMO" - nicht die halbe Satzhuelle und keine Klammern.
    """
    head = (sentence or "")[:max(0, first_mention)]
    head = _PAREN.sub(" ", head)
    parts = [part.strip() for part in re.split(r"[,;:]", head) if part.strip()]
    head = parts[-1] if parts else ""
    words = _WORD.findall(head)
    while words and words[-1].lower() in _TRAIL_STOP:
        words.pop()
    while words and words[0].lower() in _LEAD:
        words.pop(0)
    return " ".join(words[-10:])


def _label_ok(label: str) -> bool:
    """Ein brauchbares Arm-Etikett: 1-4 reine Woerter, nichts Numerisches."""
    words = _WORD.findall(label or "")
    if not 1 <= len(words) <= 4:
        return False
    if len(words) != len(str(label or "").split()):
        return False
    return _named_group(label)


# --------------------------------------------------------------------------
# Satz -> Kandidat
# --------------------------------------------------------------------------

_REASONS = {
    "no_arm": "kein Mittelwert mit Streuung im Satz",
    "arm_count": "nicht genau zwei Mittelwerte mit Streuung im Satz",
    "no_n": "Fallzahl je Arm fehlt",
    "no_label": "Arm-Etikett fehlt",
    "same_label": "beide Arme tragen dasselbe Etikett",
    "cross_sectional": "kein Interventionsarm - Gruppenvergleich ohne Intervention",
    "outcome": "kein Outcome vor dem ersten Arm",
    "baseline": "Baseline-/Veraenderungsmuster statt Gruppenvergleich",
    "median": "Median/IQR statt Mittelwert mit SD",
    "bad_sd": "Streuung nicht positiv",
    "explained": "Streuung als SEM/SE im Satz (nicht SD)",
    "artifact": "Tabellen-/Zitationsrest statt Ergebnissatz",
    "design": "Stichproben- oder Designbeschreibung statt Ergebnis",
    "demographic": "demografische Angabe statt Outcome",
}


def convert_sentence(sentence: str, quote: str = "") -> Dict:
    """Ein Satz -> speicherfertiger Kandidat oder Ablehnung mit Grund."""
    text = " ".join(str(sentence or "").split())
    if not text:
        return {"ok": False, "reason": _REASONS["no_arm"]}
    if text.startswith("|"):
        return {"ok": False, "reason": _REASONS["no_arm"]}
    if _MEDIAN_CUE.search(text):
        return {"ok": False, "reason": _REASONS["median"]}
    if _CHANGE_CUE.search(text):
        return {"ok": False, "reason": _REASONS["baseline"]}
    # "SEM" oder "SE" im Satz heisst: die Streuung ist kein SD. Das wird
    # nicht umgedeutet, sondern abgelehnt.
    if re.search(r"\bSEM\b|standard\s+error|\bSE\b", text):
        return {"ok": False, "reason": _REASONS["explained"]}
    if "|" in text or _CITATION.search(text):
        return {"ok": False, "reason": _REASONS["artifact"]}
    if _DESIGN_CUE.search(text):
        return {"ok": False, "reason": _REASONS["design"]}

    mentions = arm_mentions(text)
    if not mentions:
        return {"ok": False, "reason": _REASONS["no_arm"]}
    if len(mentions) != 2:
        return {"ok": False, "reason": _REASONS["arm_count"]}
    if any(not m.n or m.n < 2 for m in mentions):
        return {"ok": False, "reason": _REASONS["no_n"]}

    outcome = _outcome_from(text, mentions[0].start)

    labels = [m.label for m in mentions]
    if any(not _label_ok(label) for label in labels):
        return {"ok": False, "reason": _REASONS["no_label"]}
    if labels[0].lower() == labels[1].lower():
        return {"ok": False, "reason": _REASONS["same_label"]}
    if not any(_INTERVENTION_ARM.search(label) for label in labels):
        return {"ok": False, "reason": _REASONS["cross_sectional"]}
    if len(outcome) < 2:
        return {"ok": False, "reason": _REASONS["outcome"]}
    if _DEMOGRAPHIC.search(outcome):
        return {"ok": False, "reason": _REASONS["demographic"]}

    arms = [ArmStats(label=m.label, n=int(m.n), mean=m.mean, sd=m.sd)
            for m in mentions]
    effect = smd_from_arms(arms[0], arms[1])
    if effect is None:
        return {"ok": False, "reason": _REASONS["bad_sd"]}

    stamp = _TIMEPOINT.search(text)
    time_point = f"{stamp.group(1).lower()} {stamp.group(2)}" if stamp else ""
    payload = effect.to_dict()
    payload.update({
        "ok": True,
        "outcome": outcome,
        "quote": quote or text,
        "time_point": time_point,
    })
    return payload


def text_arm_candidates(text: str) -> List[Dict]:
    """Alle Saetze eines Dokuments pruefen und Kandidaten zurueckgeben.

    Zeilen, die als Tabellenzeile beginnen ("|"), werden uebersprungen - die
    liest der Tabellen-Rechner. Das Zitat bleibt der unveraenderte Satz aus
    dem Dokument, damit ``locate_quote`` ihn woertlich findet.
    """
    candidates: List[Dict] = []
    for line in (text or "").splitlines():
        # Der JATS-Flachtext trennt Tabellenzellen mit "|"; eine Zeile mit
        # mehreren Trennern ist eine Tabellenzeile, kein Ergebnissatz.
        if line.count("|") >= 2:
            continue
        for _start, _end, sentence in split_sentences(line):
            candidate = convert_sentence(sentence)
            if candidate.get("ok"):
                candidate["quote"] = sentence
                candidates.append(candidate)
    return candidates


# --------------------------------------------------------------------------
# Speichern
# --------------------------------------------------------------------------

def store_text_arm_effects(db, source_id: str, source_text_id: str,
                           document_text: str,
                           candidates: Iterable[Dict]):
    """Wie der Tabellen-Store, nur mit eigener Extraktor-Kennung."""
    return store_arm_level_effects(
        db, source_id, source_text_id, document_text, candidates,
        extractor=TEXT_ARM_VERSION)

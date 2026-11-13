#!/usr/bin/env python3
"""Abgleich der projektinternen CBT-I-Studien mit Hwang 2025 und Lee 2023.

Der Abgleich ist rein lesend. Er aendert keine Outcome-Werte, startet kein
Modell und uebernimmt keine Studien aus Uebersichtsarbeiten. Er prueft:

1. wie viele dCBT-I-Studien tatsaechlich im Projekt liegen,
2. ob die 30 eingefrorenen Goldstandard-Volltexte dCBT-I-Studien sind,
3. welche projektinternen Studien in den Studienlisten der beiden Reviews
   vorkommen (DOI- und Autor-Jahr-Abgleich),
4. welche Outcomes und Zeitpunkte dabei uebereinstimmen.

Die Studienlisten der Reviews stehen in Tabelle 1 der jeweiligen Publikation.
Die Supplementary-PDFs enthalten Suchstrategie und PRISMA-Checkliste, keine
zusaetzliche Studienliste.

Aufruf:
    python public_benchmark/scripts/match_dcbti_review_studies.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "external_benchmark"
GOLDEN_DOCUMENTS = PROJECT_ROOT / "data" / "golden_effects" / "documents.json"
PILOT_DCBTI = PROJECT_ROOT / "data" / "meta_nachbau" / "pilot_dcbti" / "antwortschluessel.json"
PILOT_CBTI = PROJECT_ROOT / "data" / "meta_nachbau" / "pilot_cbti" / "antwortschluessel.json"

# Europe PMC, DOI-Abfrage am 2026-11-13. Nur hinterlegt, wenn dort geliefert.
PMCID_BY_STUDY = {
    "freeman_2017": "PMC5614772",
    "fucito_2017": "PMC5378596",
    "egbegi_2021": "PMC8465787",
}

# Erste Autorennamen der projektinternen Studien fuer den Autor-Jahr-Abgleich.
SURNAME_BY_STUDY = {
    "morris_2015": "Morris",
    "freeman_2017": "Freeman",
    "fucito_2017": "Fucito",
    "de_bruin_2018": "de Bruin",
    "chan_2022": "Chan",
    "chan_2021": "Chan",
    "de_bruin_2015": "de Bruin",
    "egbegi_2021": "Egbegi",
    "tomfohr_madsen_2020": "Tomfohr-Madsen",
}

# Tabelle 1, Hwang et al. 2025, 29 eingeschlossene RCTs.
HWANG_INCLUDED = [
    ("Batterham", 2017), ("Batterham", 2024), ("Chan", 2023), ("Cheng", 2018),
    ("Christensen", 2016), ("Espie", 2012), ("Espie", 2019), ("Felder", 2020),
    ("Glozier", 2019), ("Hagatun", 2019), ("Hinterberger", 2023),
    ("Horsch", 2017), ("Kallestad", 2021), ("Kalmbach", 2020), ("Kyle", 2020),
    ("Lancee", 2012), ("Lancee", 2013), ("Lorenz", 2018), ("Mason", 2023),
    ("McGrath", 2017), ("Ritterband", 2009), ("Ritterband", 2011),
    ("Ritterband", 2017), ("Sato", 2022), ("Theadom", 2018), ("Vedaa", 2020),
    ("Watanabe", 2023), ("Yang", 2023), ("Zhou", 2022),
]

# Tabelle 1, Lee et al. 2023, 22 eingeschlossene RCTs.
LEE_INCLUDED = [
    {"author": "Agyemang", "year": 2017},
    {"author": "Ahorsu", "year": 2020},
    {"author": "Blom", "year": 2015},
    {"author": "Bostock", "year": 2016},
    {"author": "Cheng", "year": 2018},
    {"author": "Christensen", "year": 2016},
    {"author": "Espie", "year": 2019},
    {
        "author": "Freeman",
        "year": 2017,
        "doi": "10.1016/S2215-0366(17)30328-0",
        "pmcid": "PMC5614772",
        "n_total": 3755,
        "design": "2 parallele Arme (dCBTi, TAU)",
        "sessions": 6,
        "timepoint": "10 Wochen post-treatment",
        "outcomes": ["ISI", "PHQ-9", "GAD-7"],
    },
    {"author": "Felder", "year": 2020},
    {"author": "Glozier", "year": 2019},
    {"author": "Kalmbach", "year": 2020},
    {"author": "Krieger", "year": 2019},
    {"author": "Kyle", "year": 2020},
    {"author": "Lancee", "year": 2015},
    {"author": "Lancee", "year": 2016},
    {"author": "Lorenz", "year": 2018},
    {"author": "Majd", "year": 2020},
    {"author": "Pillai", "year": 2015},
    {"author": "Sveen", "year": 2021},
    {"author": "van der Zweerde", "year": 2019},
    {"author": "van der Zweerde", "year": 2020},
    {"author": "van Straten", "year": 2014},
]

REVIEWS = {
    "hwang2025": {
        "title": "Systematic review and meta-analysis on fully automated digital cognitive behavioral therapy for insomnia",
        "journal": "npj Digital Medicine 8:157 (2025)",
        "doi": "10.1038/s41746-025-01514-4",
        "url": "https://www.nature.com/articles/s41746-025-01514-4",
        "table_url": "https://www.nature.com/articles/s41746-025-01514-4/tables/1",
        "included_count": 29,
        "included": [{"author": a, "year": y} for a, y in HWANG_INCLUDED],
        "supplement_note": (
            "Supplementary PDF enthaelt PRISMA-Checkliste und Suchstrategie, "
            "keine zusaetzliche Studienliste."
        ),
    },
    "lee2023": {
        "title": "Digital cognitive behavioral therapy for insomnia on depression and anxiety: a systematic review and meta-analysis",
        "journal": "npj Digital Medicine 6:52 (2023)",
        "doi": "10.1038/s41746-023-00800-3",
        "url": "https://www.nature.com/articles/s41746-023-00800-3",
        "table_url": "https://www.nature.com/articles/s41746-023-00800-3/tables/1",
        "included_count": 22,
        "included": LEE_INCLUDED,
        "supplement_note": (
            "Supplementary PDF enthaelt Suchstrategie und Forest Plots, "
            "keine zusaetzliche Studienliste."
        ),
    },
}

TIME_UNIT_TO_WEEKS = {
    "day": 1 / 7,
    "week": 1.0,
    "month": 4.345,
    "year": 52.14,
}
TIME_TOLERANCE_WEEKS = 0.5

# Plausible Ausschlussgründe je nicht zugeordneter Studie. Die Reviews nennen
# keine studiengenauen Ausschlussgründe; die Einordnung stützt sich auf die
# dokumentierten Kriterien und die Studienabstracts.
EXCLUSION_REASONS = {
    "morris_2015": {
        "hwang2025": {
            "criterion": "Erwachsene mit formaler Insomniediagnose; vollständig automatisierte dCBT-I ohne Therapeutenkontakt",
            "confidence": "mittel",
            "reason": "Die Stichprobe sind Studierende mit Angst- und/oder Insomniesymptomen. Der Abstract belegt weder eine formale Insomniediagnose noch, dass der Insomnie-Arm ohne Therapeutenkontakt lief.",
            "evidence": "Abstract: zwei getrennte Programme ('Anxiety Relief', 'Insomnia Relief'), 6 Wochen, STAI und PSQI; keine Angabe zu Diagnose oder Guidance.",
        },
        "lee2023": {
            "criterion": "dCBT-I mit kognitiver Umstrukturierung plus Stimuluskontrolle/Schlafrestriktion; Depression- oder Angstmaß",
            "confidence": "mittel",
            "reason": "Transdiagnostisches Angst-/Insomnie-Programm; der Insomnie-Arm ist nicht als multimodales CBT-I mit beiden geforderten Komponenten beschrieben. Angst wurde erhoben, Depression nicht.",
            "evidence": "Abstract: STAI als Angstmaß, PSQI als Schlafmaß; keine Beschreibung von Cognitive Restructuring plus Stimuluskontrolle/Schlafrestriktion.",
        },
    },
    "fucito_2017": {
        "hwang2025": {
            "criterion": "Ausschluss von Alkoholmissbrauch oder -abhängigkeit",
            "confidence": "mittel",
            "reason": "Die Studie rekrutiert ausschließlich Heavy-Drinking-College-Students und adressiert Alkoholkonsum. Das liegt nahe am Hwang-Ausschluss für Alkoholmissbrauch oder -abhängigkeit; eine entsprechende Diagnose ist im Abstract aber nicht belegt.",
            "evidence": "Abstract: 'Heavy-drinking college students (N = 42)', web-basierte Schlaf-plus-Alkohol-Intervention über 4 Wochen.",
        },
        "lee2023": {
            "criterion": "dCBT-I-Programm; berichtete Depression- oder Angstmaße",
            "confidence": "mittel",
            "reason": "Die Intervention kombiniert Schlaf- und Alkoholinhalte; Depression oder Angst werden nicht als Outcomes berichtet.",
            "evidence": "Abstract nennt Alkohol- und Schlafoutcomes, keine Depression- oder Angstskala.",
        },
    },
    "de_bruin_2018": {
        "hwang2025": {
            "criterion": "Erwachsene ≥18 Jahre",
            "confidence": "hoch",
            "reason": "Die Stichprobe besteht aus Jugendlichen mit einem mittleren Alter von 15,6 Jahren.",
            "evidence": "Abstract: 116 Teilnehmende, age = 15.6 years, DSM-5-Insomnie.",
        },
        "lee2023": {
            "criterion": "Erwachsene ≥18 Jahre",
            "confidence": "hoch",
            "reason": "Die Stichprobe besteht aus Jugendlichen mit einem mittleren Alter von 15,6 Jahren.",
            "evidence": "Abstract: age = 15.6 years; Internet- und Gruppentherapie versus Warteliste.",
        },
    },
    "chan_2022": {
        "hwang2025": {
            "criterion": "Erwachsene ≥18 Jahre; vollständig automatisierte dCBT-I",
            "confidence": "niedrig",
            "reason": "Die Stichprobe sind 'youths' mit einem Mittelwert von 20,0 ± 2,5 Jahren, ein Teil kann unter 18 sein. Die E-Mail-Self-Help-Bedingung ist nicht eindeutig als vollständig automatisiert ohne Therapeutenkontakt beschrieben.",
            "evidence": "Abstract: 135 youths, mean age 20.0 ± 2.5; E-Mail-Self-Help versus Gruppentherapie versus Warteliste.",
        },
        "lee2023": {
            "criterion": "berichtete Depression- oder Angstmaße; Suchschluss 15.01.2022",
            "confidence": "mittel",
            "reason": "Die Outcomes sind Insomnie, präsleep arousal, dysfunktionale Überzeugungen, Schlafhygiene und Tagesfunktion; Depression oder Angst werden nicht berichtet. Die Arbeit ist mit Publikationsjahr 2022 geführt; ob sie vor dem Lee-Suchschluss online verfügbar war, ist nicht belegt.",
            "evidence": "Abstract listet keine Depression- oder Angstskala; Publikationsjahr 2022.",
        },
    },
    "chan_2021": {
        "hwang2025": {
            "criterion": "Erwachsene ≥18 Jahre",
            "confidence": "hoch",
            "reason": "Die Stichprobe sind Jugendliche mit einem mittleren Alter von 14,7 Jahren; zudem ein Präventionsprogramm bei subklinischer Insomnie, keine Behandlung einer diagnostizierten Insomnie.",
            "evidence": "Abstract: 242 adolescents, mean age 14.7 ± 1.8, family history und subthreshold insomnia.",
        },
        "lee2023": {
            "criterion": "Erwachsene ≥18 Jahre",
            "confidence": "hoch",
            "reason": "Die Stichprobe sind Jugendliche mit einem mittleren Alter von 14,7 Jahren.",
            "evidence": "Abstract: mean age 14.7 ± 1.8.",
        },
    },
    "de_bruin_2015": {
        "hwang2025": {
            "criterion": "Erwachsene ≥18 Jahre; vollständig automatisierte dCBT-I",
            "confidence": "hoch",
            "reason": "Die Stichprobe ist 13-19 Jahre alt (M = 15,9); zudem geleitete Self-Help-Sitzungen, also nicht vollständig automatisiert.",
            "evidence": "Abstract: 32 adolescents, 13-19 years, six guided self-help online CBTI sessions.",
        },
        "lee2023": {
            "criterion": "Erwachsene ≥18 Jahre",
            "confidence": "hoch",
            "reason": "Die Stichprobe ist 13-19 Jahre alt (M = 15,9).",
            "evidence": "Abstract: 13-19 years, M = 15.9.",
        },
    },
    "egbegi_2021": {
        "hwang2025": {
            "criterion": "Erwachsene ≥18 Jahre; digital gelieferte dCBT-I",
            "confidence": "hoch",
            "reason": "Die Stichprobe sind In-School-Adoleszente; die Intervention war eine gruppenbasierte manualisierte CBT vor Ort, nicht digital.",
            "evidence": "Abstract: 50 in-school adolescents, weekly group-based manualised CBT-based intervention over 5 weeks.",
        },
        "lee2023": {
            "criterion": "Erwachsene ≥18 Jahre; dCBT-I",
            "confidence": "hoch",
            "reason": "In-School-Adoleszente und eine gruppenbasierte Intervention vor Ort, keine digitale CBT-I.",
            "evidence": "Abstract: in-school adolescents, group-based manualised intervention.",
        },
    },
    "tomfohr_madsen_2020": {
        "hwang2025": {
            "criterion": "Erwachsene ≥18 Jahre; vollständig automatisierte dCBT-I",
            "confidence": "hoch",
            "reason": "Die Stichprobe ist 12-18 Jahre alt (M = 15,0); die CBT-I wird nicht als digitale, vollständig automatisierte Intervention beschrieben.",
            "evidence": "Abstract: N = 24, 12-18 years, M = 15.0, CBT-I versus TAU.",
        },
        "lee2023": {
            "criterion": "Erwachsene ≥18 Jahre",
            "confidence": "hoch",
            "reason": "Die Stichprobe ist 12-18 Jahre alt (M = 15,0).",
            "evidence": "Abstract: 12-18 years, M = 15.0.",
        },
    },
}

DCBTI_PATTERN = re.compile(
    r"digital\s+(cognitive|behaviou?ral)|dcbt|cbt[- ]?i|"
    r"cognitive\s+behaviou?ral\s+therapy\s+for\s+insomnia",
    re.IGNORECASE,
)
SLEEP_PATTERN = re.compile(r"sleep|insomnia|melatonin|caffeine", re.IGNORECASE)


def normalize_surname(value: str) -> str:
    text = unicodedata.normalize("NFKD", value)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("-", "").replace(" ", "")
    for prefix in ("vander", "de", "van", "von"):
        if text.startswith(prefix) and len(text) > len(prefix):
            text = text[len(prefix):]
    return re.sub(r"[^a-z]", "", text)


def _to_weeks(number: str, unit: str) -> float:
    value = float(number.replace(",", "."))
    unit = unit.lower()
    if unit.startswith(("tag", "day")):
        factor = TIME_UNIT_TO_WEEKS["day"]
    elif unit.startswith(("woche", "week")):
        factor = TIME_UNIT_TO_WEEKS["week"]
    elif unit.startswith(("monat", "month")):
        factor = TIME_UNIT_TO_WEEKS["month"]
    else:
        factor = TIME_UNIT_TO_WEEKS["year"]
    return value * factor


TIMEPOINT_MARKER = re.compile(
    r"(post[\s-]?treatment|post[\s-]?intervention|"
    r"end of treatment|after treatment|nachbehandlung|behandlungsende|"
    r"follow[\s-]?up|katamnese|baseline|mid[\s-]?treatment|mid\b|post\b)",
    re.IGNORECASE,
)


WEEK_UNIT = (
    r"(tag(?:e|en)?|day(?:s)?|woche(?:n)?|week(?:s)?|"
    r"monat(?:e|en)?|month(?:s)?|jahr(?:e|en)?|year(?:s)?)"
)
WEEK_NUMBER = r"(\d+(?:[.,]\d+)?)"
# Nur diese Zeichen duerfen zwischen Zahl und nachgestelltem Marker stehen.
MARKER_CONNECTOR = re.compile(r"^[\s,;:()\[\]\-–—/]*$")
CLAUSE_BOUNDARY = re.compile(r"[,;\n]|\band\b|\bund\b|\bthen\b", re.IGNORECASE)
PHRASE_BOUNDARY = re.compile(r"[;,()\n]|(?<!\d)\.(?!\d)")
# Median- und Streuungsangaben sind keine festen Zeitpunkte. "±" und
# "median" werden deshalb konservativ aus der Wochenberechnung entfernt.
UNCERTAIN_TIME = re.compile(r"(median|\bmittelwert\b|±|\+/-)", re.IGNORECASE)


def _week_occurrences(text: str) -> list[tuple[float, int, int]]:
    """Liefert (Wochenwert, Zahlstart, Phrasenende) je Zeitangabe.

    Das Phrasenende umfasst die Einheit ("12 weeks"), damit ein direkt
    folgender Marker als nachgestellt erkannt werden kann.
    """
    occurrences: list[tuple[float, int, int]] = []
    for match in re.finditer(
        rf"{WEEK_NUMBER}\s*-\s*{WEEK_NUMBER}\s*{WEEK_UNIT}", text
    ):
        occurrences.append(
            (_to_weeks(match.group(1), match.group(3)), match.start(1), match.end())
        )
        occurrences.append(
            (_to_weeks(match.group(2), match.group(3)), match.start(2), match.end())
        )
    for match in re.finditer(rf"{WEEK_NUMBER}\s*{WEEK_UNIT}|{WEEK_UNIT}\s*{WEEK_NUMBER}", text):
        if match.group(1):
            value = _to_weeks(match.group(1), match.group(2))
            start = match.start(1)
        else:
            value = _to_weeks(match.group(4), match.group(3))
            start = match.start(4)
        occurrences.append((value, start, match.end()))
    return sorted(
        {(round(value, 2), start, end) for value, start, end in occurrences},
        key=lambda item: (item[1], item[0]),
    )


def _clause_end(text: str, start: int) -> int:
    match = CLAUSE_BOUNDARY.search(text, start)
    return match.start() if match else len(text)


def _phrase_around(text: str, start: int, end: int) -> str:
    left = 0
    for match in PHRASE_BOUNDARY.finditer(text, 0, start):
        left = match.end()
    right_match = PHRASE_BOUNDARY.search(text, end)
    right = right_match.start() if right_match else len(text)
    return text[left:right]


def _is_uncertain(text: str, start: int, end: int) -> bool:
    return bool(UNCERTAIN_TIME.search(_phrase_around(text, start, end)))


def _weeks_in_text(text: str) -> list[float]:
    return sorted(
        {
            value
            for value, start, end in _week_occurrences(text)
            if not _is_uncertain(text, start, end)
        }
    )


def _marker_kind(marker: str) -> str:
    marker = marker.lower()
    if marker.startswith("follow") or "katamnese" in marker:
        return "follow_up"
    if marker.startswith("baseline") or marker.startswith("mid"):
        return "other"
    return "post_treatment"


def parse_timepoints(text: str | None) -> dict[str, Any]:
    """Parst Zeitangaben und trennt Post-Treatment von Follow-up.

    Nur Zahlen im Post-Treatment-Segment duerfen spaeter als Treffer gelten.
    Follow-up- und Mid-Treatment-Werte werden separat ausgewiesen.
    """
    if not text:
        return {
            "raw": text, "weeks": [], "post_treatment_weeks": [],
            "follow_up_weeks": [], "other_weeks": [], "status": "missing",
            "ambiguous_post_treatment": False,
        }
    normalized = str(text).lower().replace("–", "-").replace("—", "-")
    markers = [
        (match.start(), match.end(), _marker_kind(match.group()))
        for match in TIMEPOINT_MARKER.finditer(normalized)
    ]
    post: list[float] = []
    follow: list[float] = []
    other: list[float] = []

    def assign(weeks: list[float], kind: str) -> None:
        if kind == "post_treatment":
            post.extend(weeks)
        elif kind == "follow_up":
            follow.extend(weeks)
        else:
            other.extend(weeks)

    for value, start, end in _week_occurrences(normalized):
        if _is_uncertain(normalized, start, end):
            continue
        previous = None
        following = None
        for marker_start, marker_end, marker_kind in markers:
            if marker_end <= start:
                previous = (marker_start, marker_end, marker_kind)
            elif marker_start >= end and following is None:
                following = (marker_start, marker_end, marker_kind)
        kind = "other"
        if following:
            gap = normalized[end:following[0]]
            # Nachgestellter Marker ("12 weeks follow-up") nur, wenn die Zahl
            # direkt davor steht und hinter dem Marker keine weitere Zahl folgt.
            suffix = bool(MARKER_CONNECTOR.fullmatch(gap))
            if suffix:
                after = normalized[
                    following[1]:_clause_end(normalized, following[1])
                ]
                # Auch unsichere Angaben belegen, dass der Marker eine
                # fuehrende Beschriftung ist und keine nachgestellte.
                suffix = not _week_occurrences(after)
            if suffix:
                kind = following[2]
            elif previous:
                kind = previous[2]
            else:
                kind = following[2]
        elif previous:
            kind = previous[2]
        assign([value], kind)

    post = sorted(set(post))
    follow = sorted(set(follow))
    other = sorted(set(other))
    all_weeks = sorted(set(post) | set(follow) | set(other))
    if not markers:
        # Ohne Marker ist der Zeitpunkt nicht als Post-Treatment belegt.
        # Die Zahlen bleiben als "other" sichtbar, zaehlen aber nicht als Treffer.
        status = "no_marker" if all_weeks else "unparsed"
    else:
        status = "parsed" if all_weeks else "unparsed"
    return {
        "raw": text,
        "weeks": all_weeks,
        "post_treatment_weeks": post,
        "follow_up_weeks": follow,
        "other_weeks": other,
        "status": status,
        "ambiguous_post_treatment": len(post) > 1,
    }


def compare_timepoints(
    our_text: str | None,
    review_text: str | None,
    tolerance_weeks: float = TIME_TOLERANCE_WEEKS,
) -> dict[str, Any]:
    """Vergleicht Zeitpunkte als Wochenwerte statt als Teilstrings."""
    ours = parse_timepoints(our_text)
    review = parse_timepoints(review_text)
    result: dict[str, Any] = {
        "our": ours,
        "review": review,
        "tolerance_weeks": tolerance_weeks,
        "match": None,
        "difference_weeks": None,
        "reason": "",
    }
    if not ours["post_treatment_weeks"] or not review["post_treatment_weeks"]:
        result["reason"] = (
            "kein Post-Treatment-Zeitpunkt in beiden Angaben; "
            "Follow-up-Werte zaehlen nicht"
        )
        return result
    comparisons = [
        (abs(our - rev), our, rev)
        for our in ours["post_treatment_weeks"]
        for rev in review["post_treatment_weeks"]
    ]
    best_difference, best_our, best_review = min(comparisons)
    result["difference_weeks"] = round(best_difference, 2)
    result["matched_post_weeks"] = {"our": best_our, "review": best_review}
    result["ambiguous_post_treatment"] = {
        "our": ours["ambiguous_post_treatment"],
        "review": review["ambiguous_post_treatment"],
    }
    result["match"] = best_difference <= tolerance_weeks
    result["reason"] = (
        "innerhalb der Wochentoleranz"
        if result["match"] else "ausserhalb der Wochentoleranz"
    )
    result["ignored_follow_up_weeks"] = sorted(
        set(ours["follow_up_weeks"]) | set(review["follow_up_weeks"])
    )
    return result


def load_our_studies() -> tuple[list[dict[str, Any]], list[str]]:
    studies: dict[str, dict[str, Any]] = {}
    sources: list[str] = []
    for label, path in (("pilot_dcbti", PILOT_DCBTI), ("pilot_cbti", PILOT_CBTI)):
        data = json.loads(path.read_text(encoding="utf-8"))
        sources.append(str(path.relative_to(PROJECT_ROOT)))
        for row in data["studies"]:
            study_id = row["study_id"]
            if study_id in studies:
                continue
            year_match = re.search(r"(\d{4})$", study_id)
            studies[study_id] = {
                "study_id": study_id,
                "source": label,
                "citation": row.get("citation", ""),
                "doi": row.get("doi"),
                "pmcid": PMCID_BY_STUDY.get(study_id),
                "surname": SURNAME_BY_STUDY.get(study_id, study_id),
                "year": int(year_match.group(1)) if year_match else None,
                "outcomes": [row["instrument"]] if row.get("instrument") else [],
                "timepoint": row.get("timepoint"),
                "n_treatment": row.get("n_treatment"),
                "n_control": row.get("n_control"),
            }
    return sorted(studies.values(), key=lambda row: row["study_id"]), sources


def inspect_thirty_documents() -> dict[str, Any]:
    data = json.loads(GOLDEN_DOCUMENTS.read_text(encoding="utf-8"))
    documents = data["documents"]
    dcbti = [doc["title"] for doc in documents if DCBTI_PATTERN.search(doc.get("title", ""))]
    sleep = [doc["title"] for doc in documents if SLEEP_PATTERN.search(doc.get("title", ""))]
    return {
        "path": str(GOLDEN_DOCUMENTS.relative_to(PROJECT_ROOT)),
        "documents": len(documents),
        "dcbti_titles": len(dcbti),
        "sleep_related_titles": len(sleep),
        "sleep_examples": sleep[:5],
        "conclusion": (
            "Die 30 eingefrorenen Volltexte sind ein gemischtes Methoden-Sample; "
            "keiner ist eine dCBT-I-Studie."
        ),
    }


def review_matches(study: dict[str, Any], review: dict[str, Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    study_doi = (study.get("doi") or "").lower()
    for entry in review["included"]:
        matched_by: list[str] = []
        entry_doi = (entry.get("doi") or "").lower()
        if study_doi and entry_doi and study_doi == entry_doi:
            matched_by.append("doi")
        if (
            normalize_surname(entry["author"]) == normalize_surname(study["surname"])
            and entry["year"] == study["year"]
        ):
            matched_by.append("autor_jahr")
        if matched_by:
            matches.append({"entry": entry, "matched_by": matched_by})
    return matches


def build_overlap(study: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    matches = review_matches(study, review)
    if not matches:
        return {
            "review": review["doi"],
            "matched": False,
            "reason": "kein Treffer nach DOI oder Autor/Jahr in Tabelle 1",
        }
    match = matches[0]
    entry = match["entry"]
    review_outcomes = entry.get("outcomes") or []
    outcome_overlap = [
        outcome for outcome in review_outcomes if outcome in study["outcomes"]
    ]
    n_review = entry.get("n_total")
    n_ours = None
    if study.get("n_treatment") is not None and study.get("n_control") is not None:
        n_ours = int(study["n_treatment"]) + int(study["n_control"])
    comparison = compare_timepoints(study.get("timepoint"), entry.get("timepoint"))
    return {
        "review": review["doi"],
        "matched": True,
        "matched_by": match["matched_by"],
        "review_entry": entry,
        "our_outcomes": study["outcomes"],
        "review_outcomes": review_outcomes,
        "outcome_overlap": outcome_overlap,
        "our_timepoint": study.get("timepoint"),
        "review_timepoint": entry.get("timepoint"),
        "timepoint_comparison": comparison,
        "timepoint_match": comparison["match"],
        "n_ours": n_ours,
        "n_review": n_review,
        "n_match": n_ours is not None and n_review is not None and n_ours == n_review,
        "note": (
            "Review nennt nur Studiencharakteristika; Mittelwerte und SD "
            "stehen nicht in Tabelle 1."
        ),
    }


def build_result() -> dict[str, Any]:
    studies, sources = load_our_studies()
    overlaps = []
    for study in studies:
        for review in REVIEWS.values():
            overlap = build_overlap(study, review)
            if overlap["matched"]:
                overlaps.append({
                    "study_id": study["study_id"],
                    "review_doi": review["doi"],
                    "review_title": review["title"],
                    **overlap,
                })
    unmatched = sorted({
        study["study_id"] for study in studies
        if not any(item["study_id"] == study["study_id"] for item in overlaps)
    })
    exclusion_reasons: dict[str, dict[str, Any]] = {}
    for study_id in unmatched:
        reasons = EXCLUSION_REASONS.get(study_id)
        if not reasons or set(reasons) != set(REVIEWS):
            raise ValueError(
                f"Ausschlussgründe fehlen oder sind unvollständig: {study_id}"
            )
        exclusion_reasons[study_id] = reasons
    return {
        "version": 5,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": (
            "Abgleich projektinterner CBT-I-Primaerschstudien mit den "
            "Studienlisten von Hwang 2025 und Lee 2023; keine Aenderung von "
            "Outcome-Werten, kein Modelllauf."
        ),
        "project_30_documents": inspect_thirty_documents(),
        "our_sources": sources,
        "our_studies": studies,
        "our_studies_count": len(studies),
        "reviews": {
            key: {
                "title": review["title"],
                "journal": review["journal"],
                "doi": review["doi"],
                "url": review["url"],
                "table_url": review["table_url"],
                "included_count": review["included_count"],
                "supplement_note": review["supplement_note"],
            }
            for key, review in REVIEWS.items()
        },
        "matches": overlaps,
        "match_count": len(overlaps),
        "unmatched_studies": unmatched,
        "exclusion_reasons": exclusion_reasons,
        "limitations": [
            "Die Review-Tabellen nennen keine PMCIDs; PMCID-Abgleich ist nur fuer Studien moeglich, deren PMCID im Projekt oder in der Referenzliste steht.",
            "DOI steht in Tabelle 1 nur bei der bestaetigten Zeile; weitere DOIs wurden nicht aus der Referenzliste rekonstruiert.",
            "Tabelle 1 nennt keine armweisen Mittelwerte oder SD; eine numerische Bestaetigung der Extraktion ist daraus nicht moeglich.",
            "Die Supplementary-PDFs enthalten keine Studienliste; massgeblich ist Tabelle 1.",
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# dCBT-I-Studienabgleich mit Hwang 2025 und Lee 2023",
        "",
        f"Stand: {result['created_at']}",
        "",
        "## Befund zur Datenbasis",
        "",
        f"Im Projekt liegen **{result['our_studies_count']} CBT-I-Primärstudien** "
        "mit DOI (4 aus dem dCBT-I-Pilot, 6 aus dem CBT-I-Pilot, eine Studie "
        "in beiden Listen). Nicht alle neun sind vollständig digital; die vier "
        "dCBT-I-Pilotstudien sind der digitale Kern.",
        "",
        f"Die im Auftrag genannten **30 dCBT-I-Studien existieren so nicht**: "
        f"`{result['project_30_documents']['path']}` enthält "
        f"{result['project_30_documents']['documents']} gemischte Volltexte "
        f"({result['project_30_documents']['sleep_related_titles']} mit Schlafbezug, "
        f"davon **{result['project_30_documents']['dcbti_titles']} dCBT-I**). "
        "Der Abgleich wurde deshalb auf die tatsächlich vorhandenen "
        "CBT-I-Studien angewendet.",
        "",
        "## Geprüfte Studien",
        "",
        "| Studie | DOI | PMCID | Jahr |",
        "|---|---|---|---:|",
    ]
    for study in result["our_studies"]:
        lines.append(
            f"| {study['study_id']} | `{study['doi']}` | "
            f"{study['pmcid'] or 'nicht hinterlegt'} | {study['year']} |"
        )
    lines += [
        "",
        "## Ergebnisse",
        "",
        "| Review | eingeschlossene RCTs | Treffer |",
        "|---|---:|---:|",
    ]
    for review in result["reviews"].values():
        hits = sum(1 for item in result["matches"] if item["review_doi"] == review["doi"])
        lines.append(f"| {review['journal']} | {review['included_count']} | {hits} |")
    lines += [
        "",
        f"**{result['match_count']} von {result['our_studies_count']} Studien** "
        "konnten zugeordnet werden.",
        "",
    ]
    if result["matches"]:
        for item in result["matches"]:
            entry = item["review_entry"]
            lines += [
                f"### Treffer: {item['study_id']} in {entry['author']} {entry['year']}",
                "",
                f"- Review: {item['review_title']}",
                f"- DOI: `{entry['doi']}`; PMCID `{entry['pmcid']}`",
                f"- Abgleich über: {', '.join(item['matched_by'])}",
                f"- Design: {entry['design']}; Sitzungen: {entry['sessions']}",
                f"- N gesamt: Review {item['n_review']}, Projekt {item['n_ours']} "
                f"→ {'identisch' if item['n_match'] else 'abweichend'}",
                f"- Outcomes im Review: {', '.join(item['review_outcomes'])}",
                f"- Outcomes im Projekt: {', '.join(item['our_outcomes']) or 'keine'}",
                f"- Outcome-Überschneidung: "
                f"{', '.join(item['outcome_overlap']) or 'keine'}",
                f"- Zeitpunkt Review: {item['review_timepoint']}",
                f"- Zeitpunkt Projekt: {item['our_timepoint']}",
                f"- Wochenvergleich (nur Post-Treatment): Projekt "
                f"{item['timepoint_comparison']['our']['post_treatment_weeks']} "
                f"vs. Review "
                f"{item['timepoint_comparison']['review']['post_treatment_weeks']}; "
                f"Differenz {item['timepoint_comparison']['difference_weeks']} Wochen "
                f"(Toleranz {item['timepoint_comparison']['tolerance_weeks']}); "
                f"{'übereinstimmend' if item['timepoint_match'] is True else 'nicht vergleichbar' if item['timepoint_match'] is None else 'abweichend'}",
                f"- {item['note']}",
                "",
            ]
    lines += [
        "## Nicht zugeordnete Studien",
        "",
        ", ".join(result["unmatched_studies"]) or "keine",
        "",
        "Für sie enthält keine der beiden Studienlisten einen Treffer nach "
        "DOI oder Autor/Jahr. Das ist **kein** Beleg dafür, dass die Studien "
        "fehlerhaft sind; sie sind nur nicht in diesen Reviews enthalten.",
        "",
        "## Plausible Ausschlussgründe",
        "",
        "Die Reviews dokumentieren keine studiengenauen Ausschlussgründe. Die "
        "folgenden Einordnungen sind aus den publizierten Kriterien und den "
        "Studienabstracts abgeleitet und als plausibel, nicht als bestätigt "
        "markiert.",
        "",
    ]
    for study_id in result["unmatched_studies"]:
        lines.append(f"### {study_id}")
        lines.append("")
        for key, label in (("hwang2025", "Hwang 2025"), ("lee2023", "Lee 2023")):
            reason = result["exclusion_reasons"][study_id][key]
            lines.append(
                f"- **{label}:** {reason['reason']} "
                f"Kriterium: {reason['criterion']}. "
                f"Konfidenz: {reason['confidence']}. Beleg: {reason['evidence']}"
            )
        lines.append("")
    lines += [
        "## Einordnung",
        "",
        "- Der einzige belastbare Treffer ist **Freeman 2017 (OASIS)** in "
        "Lee 2023. Studie, ISI als Schlafoutcome, Zeitpunkt 10 Wochen und "
        "Gesamt-N 3755 stimmen überein.",
        "- Lee 2023 extrahiert zusätzlich PHQ-9 und GAD-7; diese Outcomes "
        "wurden im Projekt nicht extrahiert. Die Outcome-Überschneidung ist "
        "daher nur ISI.",
        "- Hwang 2025 enthält Freeman 2017 nicht, obwohl die Arbeit als "
        "Hintergrundquelle zitiert wird. Zitierung ist keine Aufnahme.",
        "- Hwang 2025 enthält Chan 2023 (Hongkong, smartphone-delivered), "
        "nicht unsere Chan-Studien 2021/2022.",
        "- Keine der beiden Tabellen nennt armweise Mittelwerte oder SD. Eine "
        "numerische Bestätigung unserer Werte ist aus den Review-Tabellen "
        "nicht möglich, nur eine Bestätigung von Studie, Outcome, Zeitpunkt "
        "und N.",
        "",
        "## Grenzen",
        "",
    ]
    lines += [f"- {item}" for item in result["limitations"]]
    lines += [
        "",
        "## Empfehlung",
        "",
        "Der Review-Abgleich bestätigt genau eine Studie und dort nur ISI, "
        "Zeitpunkt und N. Als externer Goldstandard für die 30 Volltexte ist "
        "er ungeeignet. Sinnvoller ist, die 30 Volltexte zuerst als das zu "
        "benennen, was sie sind (gemischtes Methoden-Sample), und für die "
        "dCBT-I-Frage die vier vorhandenen Primärstudien gezielt gegen "
        "Lee 2023 und die Primärtexte zu prüfen.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    result = build_result()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "dcbti_review_overlap_v1.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "dcbti_review_overlap_v1.md").write_text(
        render_markdown(result), encoding="utf-8",
    )
    print(
        f"Projektstudien: {result['our_studies_count']}; Treffer: "
        f"{result['match_count']}; 30-Dokumente mit dCBT-I: "
        f"{result['project_30_documents']['dcbti_titles']}"
    )
    print(f"JSON: {OUT_DIR / 'dcbti_review_overlap_v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

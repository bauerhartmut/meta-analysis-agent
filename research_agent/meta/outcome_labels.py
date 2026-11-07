"""Deterministische Normalisierung von Outcome-Namen fuer das Pooling.

Studien benennen denselben Endpunkt verschieden: ``Sleep onset latency, min``,
``Sleep latency (min)``, ``SOL``. Exakte Labels erzeugen daraus drei Gruppen
mit je k = 1, obwohl dieselbe Groesse gemessen wurde. Diese Normalisierung
fasst nur zusammen, was belegbar dasselbe ist:

1. Kleinschreibung, Gedankenstriche und Markup entfernen.
2. Klammerinhalt: ein bekanntes Skalenkuerzel wird angehaengt (PSQI, ESS,
   ISI, PDSS, WASO, TST, SOL), alles andere faellt weg (``primary``).
3. Die Einheit wird als Token angehaengt, nicht geloescht (``min``, ``pct``,
   ``sec``, ``hour``, ``events_per_hour``). ``Sleep efficiency (%)`` und
   ``Sleep efficiency, min`` bleiben damit getrennt.
4. Ein abschliessendes ``score`` faellt weg (``PSQI score`` -> ``psqi``).
5. Eine kurze, gepruefte Synonymtabelle bildet bekannte Varianten auf einen
   kanonischen Namen ab. Keine Aehnlichkeitsheuristik: was nicht in der
   Tabelle steht, bleibt getrennt.

Bewusst NICHT zusammengelegt: Prozent- und Zeitangaben desselben Endpunkts
(``Stage N1`` vs ``Stage N1 time``), REM-Latenz und Einschlaflatenz, und
Endpunkte ohne Skalenkuerzel (ein nacktes ``overall sleep quality`` kann ein
anderes Instrument sein als der PSQI).
"""

from __future__ import annotations

import re

# Einheiten, in der Reihenfolge der Pruefung. "events/h" vor "h", sonst
# bliebe vom Inzidenzausdruck nur ein "h" uebrig.
_UNITS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r"events?\s*(?:/|per)\s*(?:h|hour)\b", re.I), "events_per_hour"),
    (re.compile(r"\bms\b", re.I), "ms"),
    (re.compile(r"\bmin(?:ute)?s?\.?\b", re.I), "min"),
    (re.compile(r"\bsec(?:ond)?s?\.?\b", re.I), "sec"),
    (re.compile(r"\bhours?\b|\bh\b", re.I), "hour"),
    (re.compile(r"%|\bpercent\b", re.I), "pct"),
)

# Skalenkuerzel, die im Klammerzusatz stehen duerfen. Nur diese werden
# uebernommen; "primary", "total" und freier Text fallen weg.
_SCALES = frozenset({"psqi", "ess", "isi", "pdss", "waso", "tst", "sol", "ahi",
                     "mslt", "vas"})

# Geprueft an den Korpora (43 + 100 XML). Links steht der normalisierte
# Wortlaut, rechts der kanonische Name. Kein Eintrag ohne Belegzeile im
# jeweiligen Lauf.
_SYNONYMS = {
    "sol": "sleep onset latency",
    "sol min": "sleep onset latency min",
    "sleep latency": "sleep onset latency",
    "sleep latency min": "sleep onset latency min",
    "latency to sleep onset": "sleep onset latency",
    "waso": "wake after sleep onset",
    "waso pct": "wake after sleep onset pct",
    "tst": "total sleep time",
    "psqi": "psqi",
    # PSQI ist der Pittsburgh Sleep Quality Index; "overall sleep quality"
    # mit diesem Kuerzel ist dieselbe Punktskala.
    "overall sleep quality psqi": "psqi",
    "ess": "ess",
    "excessive daytime sleepiness ess": "ess",
    "isi": "isi",
}


def normalize_outcome(label: str) -> str:
    """Kanonischer Name eines Outcomes; leerer Input bleibt leer."""
    text = str(label or "").strip().lower()
    if not text:
        return ""
    for dash in ("\u2212", "\u2013", "\u2014"):
        text = text.replace(dash, "-")

    unit = ""
    for pattern, token in _UNITS:
        if pattern.search(text):
            unit = token
            text = pattern.sub(" ", text)
            break

    acronyms: list[str] = []

    def _keep_scale(match: re.Match) -> str:
        inner = " ".join(match.group(1).lower().split())
        if inner in _SCALES:
            acronyms.append(inner)
        return " "

    text = re.sub(r"\(([^()]*)\)", _keep_scale, text)
    text = re.sub(r"\[([^\[\]]*)\]", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)

    words = text.split()
    if words and words[-1] == "score":
        words.pop()
    if unit:
        words.append(unit)
    for acronym in acronyms:
        if acronym not in words:
            words.append(acronym)

    key = " ".join(words)
    return _SYNONYMS.get(key, key)

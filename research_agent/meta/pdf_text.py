"""PDF-Text normalisieren: Silbentrennung, Spalten, Zeilenumbrueche.

PDF-Extraktion liefert Text so, wie er auf der Seite steht. Fuer den
Fliesstext-Leser, der mit Saetzen arbeitet, sind drei Eigenheiten relevant:

* Silbentrennung am Zeilenende ("la-" + "tency" -> "latency"),
* zwei Spalten in einer Zeile (Extraktoren legen sie gelegentlich zusammen),
* Saetze, die an der Satzbreite umbrechen.

Die Schritte aendern nur Leerraum und Trennstriche, nie Ziffern. Reihenfolge:
erst Silbentrennung, dann Spalten, dann Saetze gluecken - jede Stufe braucht
die Zeilenumbrueche der vorherigen.
"""

from __future__ import annotations

import re

_PROSE_WORD = re.compile(r"[A-Za-zÄÖÜäöüß]{3,}")


def dehyphenate(text: str) -> str:
    """Silbentrennung am Zeilenende aufloesen.

    Nur, wenn die naechste Zeile klein weitergeht: "la-" + "tency" wird zu
    "latency". Ein Bindestrich vor Grossbuchstaben bleibt stehen, weil dort ein
    Kompositum endet ("Melatonin-RCT") und keine Silbe.
    """
    cleaned = (text or "").replace("\u00ad", "")
    return re.sub(r"(\w)[-\u2010]\n(?=[a-z])", r"\1", cleaned)


def _prose_like(segment: str) -> bool:
    """Grobe Unterscheidung Text gegenueber Tabellenzellen."""
    if len(_PROSE_WORD.findall(segment)) < 2:
        return False
    digits = sum(ch.isdigit() for ch in segment)
    return digits <= max(2, len(segment) // 8)


def split_line(line: str, min_gap: int = 3) -> list[str]:
    """Eine Zeile an der breitesten Luecke trennen, wenn beides Text ist.

    Eine Tabellenzeile ("SOL (min)      18.3        27.9") bleibt zusammen: die
    linke Seite hat dort keinen Satz, sondern ein Etikett.
    """
    gaps = [(m.start(), m.end()) for m in re.finditer(r"[ \t]{%d,}" % min_gap, line)]
    if not gaps:
        return [line]
    start, end = max(gaps, key=lambda gap: gap[1] - gap[0])
    left, right = line[:start].strip(), line[end:].strip()
    if _prose_like(left) and _prose_like(right):
        return [left, right]
    return [line]


def split_columns(text: str, min_gap: int = 3) -> str:
    """Zeilen mit zwei Spaltenfragmenten in zwei Zeilen zerlegen."""
    out: list[str] = []
    for line in (text or "").splitlines():
        out.extend(split_line(line, min_gap))
    return "\n".join(out)


def flatten_prose(text: str) -> str:
    """Saetze ueber Zeilenumbrueche gluecken; Tabellenzeilen bleiben stehen."""
    out: list[str] = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not out:
            out.append(line)
            continue
        prev = out[-1]
        ends_sentence = prev.rstrip().endswith((".", ":", ";", "!", "?"))
        tabular = bool(re.search(r"\s{2,}|\|", line)) or bool(
            re.search(r"\s{2,}|\|", prev))
        if stripped and not ends_sentence and not tabular:
            out[-1] = prev.rstrip() + " " + stripped
        else:
            out.append(line)
    return "\n".join(out)


def normalize(text: str) -> str:
    """Alle drei Schritte in der Reihenfolge, in der sie greifen muessen."""
    return flatten_prose(split_columns(dehyphenate(text)))

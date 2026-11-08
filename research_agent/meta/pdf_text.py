"""PDF-Text normalisieren: Silbentrennung, Spalten, Zeilenumbrueche.

PDF-Extraktion liefert Text so, wie er auf der Seite steht. Fuer den
Fliesstext-Leser, der mit Saetzen arbeitet, sind drei Eigenheiten relevant:

* Silbentrennung am Zeilenende ("la-" + "tency" -> "latency"),
* zwei Spalten in einer Zeile (Extraktoren legen sie gelegentlich zusammen),
* Saetze, die an der Satzbreite umbrechen.

Tabellen sind die Gegenrichtung: dort traegt jeder Zeilenumbruch Bedeutung.
Deshalb laesst ``normalize`` erkannte Tabellenbereiche (``TableBlock.start``
bis ``.end``) unveraendert und normalisiert nur den Text dazwischen. Ohne
diesen Schutz hat die Verklebung in echten Volltexten Tabellen zerstoert.

Die Schritte aendern nur Leerraum und Trennstriche, nie Ziffern.
"""

from __future__ import annotations

import re
from typing import List, Tuple

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


def split_line(line: str, min_gap: int = 3) -> List[str]:
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
    out: List[str] = []
    for line in (text or "").splitlines():
        out.extend(split_line(line, min_gap))
    return "\n".join(out)


def _numeric_heavy(line: str) -> bool:
    """Zeile, die ueberwiegend aus Zahlen besteht (Tabellenzeile)."""
    digits = sum(ch.isdigit() for ch in line)
    letters = sum(ch.isalpha() for ch in line)
    return digits >= 3 and letters == 0


def flatten_prose(text: str) -> str:
    """Saetze ueber Zeilenumbrueche gluecken; Zahlenzeilen bleiben stehen.

    Verklebt wird nur, wenn die vorige Zeile mitten im Satz endet (Buchstabe,
    Komma oder Bindestrich). Eine Zeile, die mit einer Zahl endet, ist in aller
    Regel eine Tabellenzeile - dort traegt der Umbruch Bedeutung.
    """
    out: List[str] = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not out:
            out.append(line)
            continue
        prev = out[-1]
        tabular = bool(re.search(r"\s{2,}|\|", line)) or bool(
            re.search(r"\s{2,}|\|", prev))
        ends_sentence = prev.rstrip().endswith((".", ":", ";", "!", "?"))
        if stripped and not tabular and not ends_sentence and not _numeric_heavy(prev):
            out[-1] = prev.rstrip() + " " + stripped
        else:
            out.append(line)
    return "\n".join(out)


def _table_spans(text: str) -> List[Tuple[int, int]]:
    """Zeichenbereiche erkannter Tabellen, ueberlappend zusammengefasst.

    Der Import steht in der Funktion, damit ``meta.pdf_text`` nicht beim
    Modulstart von ``research.table_extractor`` abhaengt (und umgekehrt).
    """
    try:
        from research_agent.research.table_extractor import find_table_blocks
    except Exception:
        return []
    spans: List[Tuple[int, int]] = []
    for block in find_table_blocks(text):
        start = getattr(block, "start", -1)
        end = getattr(block, "end", -1)
        if isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text):
            spans.append((start, end))
    spans.sort()
    merged: List[Tuple[int, int]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _normalize_prose(text: str) -> str:
    return flatten_prose(split_columns(dehyphenate(text)))


def normalize(text: str) -> str:
    """Fliesstext normalisieren, erkannte Tabellen unangetastet lassen."""
    text = text or ""
    spans = _table_spans(text)
    if not spans:
        return _normalize_prose(text)
    pieces: List[str] = []
    pos = 0
    for start, end in spans:
        pieces.append(_normalize_prose(text[pos:start]))
        pieces.append(text[start:end])
        pos = end
    pieces.append(_normalize_prose(text[pos:]))
    out: List[str] = []
    for piece in pieces:
        if not piece:
            continue
        if out and not out[-1].endswith("\n") and not piece.startswith("\n"):
            out.append("\n")
        out.append(piece)
    return "".join(out)

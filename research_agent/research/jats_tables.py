"""JATS/PMC-Tabellen strukturiert lesen (Implementierungsplan T4, Stufe 1).

Der Coverage-Manager grinzt XML-Volltexte zu Fließtext ab
(``_xml_to_text``) und verliert dabei Tabellenstruktur. Dieses Modul liest
dieselben Inbox-XMLs erneut, dieses Mal strukturiert: Tabellen mit Label,
Caption, Headerzeilen und Zellen; plus eine Zeilen-Klassifizierung, die
stat-reiche Kandidatenzeilen (SE/CI/SD/MIT-N/Effektwert) markiert.

Der Parser ist rein deterministisch, braucht keine LLM-Ausgabe und ändert
nichts an Datenbanken oder an den Inbox-Dateien (Read-only).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

CI_RANGE = re.compile(r"\d+\.\d+\s*(?:[-–-]|to)\s*\d+\.\d")
SE_TOKEN = re.compile(r"\b(?:SE|S\.E\.|standard error)\b", re.I)
SD_TOKEN = re.compile(r"\b(?:SD|S\.D\.|standard deviation)\b", re.I)
N_TOKEN = re.compile(r"(?:^|\W)N?\s*=\s*\d+")
PLUS_MINUS = re.compile(r"[±]\s*\d+\.\d")
NUMBER = re.compile(r"[-–-]?\d+\.\d+")


def _tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return " ".join(" ".join(el.itertext()).split())


@dataclass
class JatsRow:
    cells: list[str]
    # Label aus einer rowspan-Zelle der Zeile darueber (meist die Spalte, die
    # eine Zeilengruppe benennt). Es steht bewusst NICHT in ``cells``: die
    # Zellen bleiben woertlich, damit die Zeile als Zitat ein Teilstring des
    # Dokumenttexts bleibt.
    row_group: str = ""
    has_se: bool = False
    has_ci: bool = False
    has_sd: bool = False
    has_n: bool = False
    has_effect_metric: bool = False
    numbers: int = 0
    stat_rich: bool = False


@dataclass
class JatsTable:
    label: str = ""
    caption: str = ""
    header: list[str] = field(default_factory=list)
    rows: list[JatsRow] = field(default_factory=list)

    @property
    def stat_rich_rows(self) -> list[JatsRow]:
        return [r for r in self.rows if r.stat_rich]


_EFFECT_METRIC = re.compile(
    r"\b(?:OR\b|RR\b|HR\b|SMD\b|IRR\b|beta|β|hazard|odds|risk ratio|"
    r"effect size|measure of effect)\b", re.I)


def _col_semantics(header: list[str]) -> dict:
    """Weist jeder Zellspalte ihre semantische Rolle aus dem Header zu.

    Plan 4.3 #2: 'Mean, SD und N müssen der richtigen Gruppe zugeordnet
    bleiben' - ein SE-Wert steht in einer Zelle ohne 'SE'-Text, nur der
    Header trägt die Rolle.
    """
    roles: dict[int, str] = {}
    for i, cell in enumerate(header or []):
        c = cell.lower()
        if re.search(r"\b(?:95?\s*%?\s*ci|confidence interval)\b", c, re.I):
            roles.setdefault(i, "ci")
        elif SE_TOKEN.search(c):
            roles.setdefault(i, "se")
        elif SD_TOKEN.search(c):
            roles.setdefault(i, "sd")
        elif re.fullmatch(r"\s*n\s*", c, re.I) or N_TOKEN.search(cell):
            roles.setdefault(i, "n")
    return roles


def _classify(cells: list[str], header: list[str] | None = None,
              row_group: str = "") -> JatsRow:
    joined = " | ".join(cells)
    numbers = sum(bool(NUMBER.search(c)) for c in cells)
    roles = _col_semantics(header or [])
    row_has_se = row_has_ci = row_has_sd = row_has_n = False
    for idx, role in roles.items():
        if idx >= len(cells):
            continue
        cell = cells[idx]
        if not re.search(r"[-–-]?\d+(?:\.\d+)?", cell):
            continue
        if role == "se":
            row_has_se = True
        elif role == "ci":
            row_has_ci = True
        elif role == "sd":
            row_has_sd = True
        elif role == "n":
            row_has_n = True
    row = JatsRow(
        cells=cells,
        row_group=row_group,
        has_se=bool(SE_TOKEN.search(joined)) or row_has_se,
        has_ci=bool(re.search(r"\b(?:95?\s*%?\s*CI|confidence interval)\b", joined, re.I))
                or row_has_ci,
        has_sd=bool(SD_TOKEN.search(joined)) or bool(PLUS_MINUS.search(joined)) or row_has_sd,
        has_n=bool(N_TOKEN.search(joined)) or row_has_n,
        has_effect_metric=bool(_EFFECT_METRIC.search(joined)),
        numbers=numbers,
    )
    row.stat_rich = (row.has_ci or row.has_se
                     or (row.has_sd and row.has_n and row.numbers >= 2))
    return row


def _colspan(cell: ET.Element) -> int:
    """Spaltenbreite einer Kopfzelle (colspan), mindestens 1."""
    raw = cell.get("colspan") or cell.get("cols") or "1"
    try:
        return max(1, int(str(raw).strip()))
    except (TypeError, ValueError):
        return 1


def _rowspan(cell: ET.Element) -> int:
    """Zeilentiefe einer Kopfzelle (rowspan), mindestens 1."""
    raw = cell.get("rowspan") or cell.get("rows") or "1"
    try:
        return max(1, int(str(raw).strip()))
    except (TypeError, ValueError):
        return 1


def _is_head_row(tr: ET.Element) -> bool:
    """Zeile, deren Zellen alle th sind (Kopfzeile ohne thead-Element)."""
    tags = [_tag(td) for td in tr if _tag(td) in ("td", "th")]
    return bool(tags) and all(tag == "th" for tag in tags)


def _compose_header(blocks: list[list[tuple[str, int, int]]]) -> list[str]:
    """Mehrzeiligen Kopf zu einer Beschriftung je Datenspalte zusammensetzen.

    Medizinische Tabellen haben haeufig zwei Kopfzeilen:

        | Outcome     | Treatment |        | Placebo |        |
        |             | Mean      | SD     | Mean    | SD     |

    Bisher wurde nur die erste Zeile gelesen; die zweite landete als
    Datenzeile im Leser und verschob jede Zahl. Hier wird ueber alle
    Kopfzeilen ein Spaltenraster aufgebaut (colspan breitet aus, rowspan
    traegt die Beschriftung in die naechste Zeile) und je Spalte der Pfad
    "Treatment Mean" gebildet. Eine Zeile, die nur eine Zelle ueber alle
    Spalten traegt, ist ein Tabellentitel und wird verworfen.
    """
    if not blocks:
        return []
    # Eine Kopfzeile mit genau einer Zelle ueber eine Spalte ist, wenn weitere
    # Kopfzeilen folgen, ein Tabellentitel ("Table 2 Sleep outcomes") und
    # keine Spaltenbeschriftung: eine echte Beschriftungszeile hat je Spalte
    # eine Zelle.
    if len(blocks) > 1:
        blocks = [block for block in blocks
                  if not (len(block) == 1 and block[0][1] <= 1)]
        if not blocks:
            return []
    carry: dict[int, tuple[str, int]] = {}
    grid: list[dict[int, str]] = []
    for cells in blocks:
        line: dict[int, str] = {}
        col = 0
        index = 0
        while index < len(cells) or col in carry:
            if col in carry:
                text, left = carry[col]
                line[col] = text
                if left > 1:
                    carry[col] = (text, left - 1)
                else:
                    del carry[col]
                col += 1
                continue
            text, span, depth = cells[index]
            index += 1
            for offset in range(span):
                line[col + offset] = text
                if depth > 1:
                    carry[col + offset] = (text, depth - 1)
            col += span
        grid.append(line)

    width = max((max(line) + 1 for line in grid if line), default=0)
    if width == 0:
        return []
    if len(grid) > 1:
        # Titelzeile: genau ein Text, der ueber die ganze Breite laeuft.
        grid = [line for line in grid
                if not (len({v.strip() for v in line.values() if v.strip()}) == 1
                        and len(line) >= width)]

    labels: list[str] = []
    for column in range(width):
        parts: list[str] = []
        for line in grid:
            part = line.get(column, "").strip()
            if not part:
                continue
            if parts and (part == parts[-1] or part in parts[-1]
                          or parts[-1] in part):
                continue
            parts.append(part)
        labels.append(" ".join(parts))
    return labels


def _rows_from(element: ET.Element) -> tuple[list[str], list[JatsRow]]:
    """Kopf (alle Kopfzeilen zusammengesetzt) und Datenzeilen einer Tabelle.

    Der Kopf wird aus allen Zeilen des ``thead`` (oder, ohne thead, aus den
    fuehrenden reinen th-Zeilen) gebaut; colspan und rowspan werden dabei
    aufgeloest. Datenzellen bleiben woertlich und unexpandiert: eine
    zusammengefasste Datenzelle laesst sich nicht zerlegen, ohne einen Wert
    zu doppeln, und die Zeile muss als Zitat weiterhin ein Teilstring des
    Dokumenttexts sein. Solche Zeilen fallen im Abgleich von Kopfbreite und
    Zellenzahl auf, statt geraten zu werden.
    """
    all_rows = [el for el in element.iter() if _tag(el) == "tr"]
    head_rows = [tr for thead in element.iter() if _tag(thead) == "thead"
                 for tr in thead.iter() if _tag(tr) == "tr"]
    if not head_rows:
        for tr in all_rows:
            if _is_head_row(tr):
                head_rows.append(tr)
            elif head_rows:
                break

    head_ids = {id(tr) for tr in head_rows}
    blocks = [[(_text(td), _colspan(td), _rowspan(td))
               for td in tr if _tag(td) in ("td", "th")]
              for tr in head_rows]
    header = _compose_header([block for block in blocks if block])

    rows: list[JatsRow] = []
    # Eine erste Zelle mit rowspan benennt die folgenden Zeilen mit ("Sleep
    # parameter" ueber drei Messwerte). Diese Zeilen tragen das Label nicht
    # selbst; ohne Mitschrift hiesse ihr Outcome dann wie ein Code aus der
    # Nachbarspalte ("T2") oder wie die Caption.
    pending: list[str] = []
    section = ""
    for tr in all_rows:
        if id(tr) in head_ids:
            continue
        cells = [_text(td) for td in tr if _tag(td) in ("td", "th")]
        if not cells:
            continue
        filled = [str(c).strip() for c in cells if str(c).strip()]
        # Eine Zeile mit genau einer gefuellten Zelle und sonst leer heisst
        # Zwischenueberschrift: sie benennt die folgenden Zeilen ("Total fat"
        # ueber "Model 1"..."Model 3"). Ohne Mitschrift hiessen diese Zeilen
        # nach dem Modell ("Model 1") - ein Name, der kein Outcome ist.
        if len(filled) == 1 and len(cells) > 1 and not re.search(r"\d", filled[0]):
            section = filled[0]
            group = ""
        elif pending:
            group = pending.pop(0)
        else:
            group = section if len(header) > len(cells) or section else ""
        first = next((td for td in tr if _tag(td) in ("td", "th")), None)
        depth = _rowspan(first) if first is not None else 1
        if depth > 1 and cells and not re.search(r"\d", cells[0]):
            pending = [cells[0]] * (depth - 1)
        else:
            pending = []
        rows.append(_classify(cells, header, row_group=group))
    return header, rows


def _tables_from_root(root: ET.Element) -> list[JatsTable]:
    tables: list[JatsTable] = []
    for tw in [el for el in root.iter() if _tag(el) == "table-wrap"]:
        table = JatsTable()
        table_el = None
        for child in tw:
            tag = _tag(child)
            if tag == "label":
                table.label = _text(child)
            elif tag == "caption":
                table.caption = _text(child)
            elif tag == "table":
                table_el = child
        if table_el is None:
            continue  # Plan 3.1: Tabelle ohne korrektes Objekt überspringen
        table.header, table.rows = _rows_from(table_el)
        tables.append(table)
    return tables


def parse_jats(path: str | Path) -> list[JatsTable]:
    """List[JatsTable] aus einer JATS/PMC-XML-Datei (Read-only)."""
    return _tables_from_root(ET.parse(Path(path)).getroot())


def parse_jats_text(xml: str) -> list[JatsTable]:
    """Wie ``parse_jats``, aber aus dem XML-String (z. B. Europe-PMC-Antwort)."""
    return _tables_from_root(ET.fromstring(xml or ""))


def _pipe_row(cells: list[str]) -> str:
    """Zeile in derselben Form, in der der XML-Text die Tabelle rendert."""
    return "|" + "|".join((c.strip() or " ") for c in cells)


def blocks_from_jats(xml: str) -> list[dict]:
    """Tabellen als Artefakt-Bloecke in der Form von ``save_extracted_tables``.

    ``body`` enthaelt nur die Pipe-Zeilen (labelfrei), damit er ein woert-
    licher Teilstring des aus derselben XML gerenderten Dokumenttexts bleibt.
    ``effect_cells`` traegt die stat-reichen Zeilen mit ihren Zellwerten und
    Flags - keine erfundenen Effektgroessen.
    """
    blocks: list[dict] = []
    for table in parse_jats_text(xml):
        rows = [_pipe_row(r.cells) for r in table.rows]
        if not rows:
            continue
        blocks.append({
            "table_label": table.label,
            "caption": table.caption,
            "body": "\n".join(rows),
            "start": -1,
            "end": -1,
            "n_lines": len(rows),
            "confidence": 0.9,
            "parser": "jats-table/1",
            "effect_cells": [
                {
                    "line": _pipe_row(r.cells),
                    "cells": list(r.cells),
                    "has_se": r.has_se,
                    "has_ci": r.has_ci,
                    "has_sd": r.has_sd,
                    "has_n": r.has_n,
                }
                for r in table.stat_rich_rows
            ],
        })
    return blocks


def stat_rich_candidates(path: str | Path) -> list[dict]:
    """Bequeme Ausgabe für Diagnose/Extraktion: stat-reiche Zeilen als dict."""
    out = []
    for t in parse_jats(path):
        for r in t.stat_rich_rows:
            out.append({
                "table_label": t.label,
                "caption_excerpt": t.caption[:160],
                "cells": r.cells,
                "has_se": r.has_se, "has_ci": r.has_ci, "has_sd": r.has_sd,
                "has_n": r.has_n, "numbers": r.numbers,
            })
    return out

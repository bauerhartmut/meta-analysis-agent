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


def _classify(cells: list[str], header: list[str] | None = None) -> JatsRow:
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


def _rows_from(element: ET.Element) -> tuple[list[str], list[JatsRow]]:
    """Header (erste th-Zeile) und Datenzeilen eines table-Elements."""
    header: list[str] = []
    rows: list[JatsRow] = []
    for i, tr in enumerate(el for el in element.iter() if _tag(el) == "tr"):
        cells = [_text(td) for td in tr if _tag(td) in ("td", "th")]
        tags = [_tag(td) for td in tr if _tag(td) in ("td", "th")]
        if not cells:
            continue
        if i == 0 and "th" in tags:
            header = cells
            continue
        rows.append(_classify(cells, header))
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

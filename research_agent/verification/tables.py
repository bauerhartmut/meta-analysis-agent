"""Deterministic table reconstruction from stored Markdown/plain text.

The C1/Yun corpus stores tables as whitespace-aligned text after XML
conversion.  That is not a PDF layout layer, but it preserves the properties
verification needs: table label, header text, row label, cell text and exact
character offsets.  This parser never invents a value and never rewrites a
number.  A caller can therefore cite the returned span verbatim.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

_DELIMITER = re.compile(r"^\s*-{3,}(?:\s+-{3,})+\s*$")
_CAPTION = re.compile(r"^\s*(?:Supplementary\s+)?Table\s+[A-Z0-9]+", re.I)
_TERMINATOR = re.compile(r"^\s*:::+(?:\s*table-wrap)?\s*$")
_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")
_MEAN_SD_PAIR = re.compile(
    r"(?P<mean>-?\d+(?:[.,]\d+)?)\s*(?:±|\+/-)\s*(?P<sd>-?\d+(?:[.,]\d+)?)")
_PAREN_PAIR = re.compile(
    r"(?P<mean>-?\d+(?:[.,]\d+)?)\s*\(\s*(?P<sd>-?\d+(?:[.,]\d+)?)\s*\)")
_FRACTION = re.compile(r"(?P<events>\d+)\s*/\s*(?P<n>\d+)")
_COUNT = re.compile(r"(?<![\d.])-?\d+(?![\d.])")
_GROUP_SIZE = re.compile(r"\(\s*n\s*=\s*(\d+)\s*\)", re.I)

# Lines that look like a multi-column header: at least two separated cells,
# mostly short tokens.  Data rows are allowed too; the row selector later
# decides which line carries the outcome label.
_CELL_GAP = re.compile(r"[ \t]{2,}")


def normalize_cell(text: str) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").split())


def numeric_text(text: str) -> Optional[str]:
    """The first number in a cell, preserving its printed form."""
    match = _NUMBER.search(str(text or ""))
    return match.group(0) if match else None


def as_float(text: str) -> Optional[float]:
    if text in (None, ""):
        return None
    try:
        return float(str(text).replace(",", "."))
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class Cell:
    text: str
    start: int
    end: int

    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text, "start": self.start, "end": self.end}


@dataclass
class Row:
    line_no: int
    offset: int
    label: str
    cells: List[Cell]
    section: str = ""
    raw: str = ""

    @property
    def display_label(self) -> str:
        return normalize_cell(f"{self.section} {self.label}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line_no": self.line_no,
            "offset": self.offset,
            "label": self.label,
            "section": self.section,
            "display_label": self.display_label,
            "raw": self.raw,
            "cells": [c.to_dict() for c in self.cells],
        }


@dataclass
class Table:
    table_id: str
    caption: str
    start: int
    end: int
    line_start: int
    line_end: int
    header_lines: List[str] = field(default_factory=list)
    header_cells: List[Cell] = field(default_factory=list)
    rows: List[Row] = field(default_factory=list)
    raw: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_id": self.table_id,
            "caption": self.caption,
            "start": self.start,
            "end": self.end,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "header_lines": list(self.header_lines),
            "header_cells": [c.to_dict() for c in self.header_cells],
            "rows": [r.to_dict() for r in self.rows],
            "parser": "markdown-layout/1",
        }


def split_cells(line: str, base: int = 0) -> List[Cell]:
    """Split at runs of two or more spaces, preserving absolute positions.

    Single spaces remain inside a cell ("Group I", "mean (SD)").  A lazy
    regex with a lookahead merged aligned numeric columns; this pattern only
    permits one separating space inside a cell and therefore keeps the
    table's column boundaries intact.
    """
    cells: List[Cell] = []
    for match in re.finditer(r"\S+(?:[ \t]\S+)*", line or ""):
        text = match.group(0).strip()
        if not text:
            continue
        leading = len(match.group(0)) - len(match.group(0).lstrip())
        start = base + match.start() + leading
        cells.append(Cell(text=text, start=start, end=start + len(text)))
    return cells


def _line_offsets(lines: Sequence[str]) -> List[int]:
    offsets: List[int] = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1
    return offsets


def _is_table_row(line: str) -> bool:
    if not line.strip() or _DELIMITER.match(line) or _TERMINATOR.match(line):
        return False
    cells = split_cells(line)
    return len(cells) >= 2 and bool(_NUMBER.search(line))


def _looks_like_header(line: str) -> bool:
    cells = split_cells(line)
    if len(cells) < 2:
        return False
    if _DELIMITER.match(line) or _TERMINATOR.match(line):
        return False
    numeric = sum(bool(re.fullmatch(r"-?\d+(?:[.,]\d+)?", c.text)) for c in cells)
    return numeric <= max(1, len(cells) // 2)


def _caption_before(lines: Sequence[str], index: int) -> str:
    for back in range(index - 1, max(-1, index - 8), -1):
        text = normalize_cell(lines[back])
        if _CAPTION.match(text):
            return text
        if text.startswith(":::"):
            continue
        if text and len(text.split()) >= 3 and not _is_table_row(text):
            # Usually the wrapped caption directly above the header.
            if re.search(r"\b(table|comparison|outcomes?|baseline|week|effect)\b",
                         text, re.I):
                return text
    return ""


def parse_tables(text: str) -> List[Table]:
    """All delimiter-based tables with exact line and character offsets."""
    lines = (text or "").splitlines()
    offsets = _line_offsets(lines)
    tables: List[Table] = []
    i = 0
    while i < len(lines):
        if not _DELIMITER.match(lines[i]):
            i += 1
            continue
        header_start = i
        header_lines: List[str] = []
        for back in range(i - 1, max(-1, i - 10), -1):
            line = lines[back]
            if not line.strip():
                if header_lines:
                    break
                continue
            if _TERMINATOR.match(line):
                break
            if _DELIMITER.match(line):
                break
            if len(split_cells(line)) >= 2 or _looks_like_header(line):
                header_lines.append(line)
                header_start = back
            elif header_lines:
                break
        header_lines.reverse()

        body_start = i + 1
        body_end = body_start
        seen_data = False
        while body_end < len(lines):
            line = lines[body_end]
            if _TERMINATOR.match(line):
                break
            if _CAPTION.match(line) and seen_data:
                break
            if line.strip():
                if _is_table_row(line) or len(split_cells(line)) >= 2:
                    seen_data = True
                elif seen_data and len(normalize_cell(line).split()) > 12:
                    break
            body_end += 1

        # Some XML renderings put a second header block after the delimiter.
        post_header: List[str] = []
        for line in lines[body_start:min(body_end, body_start + 12)]:
            if not line.strip():
                continue
            numeric_count = len(_NUMBER.findall(line))
            # Header rows carry at most the arm labels, week labels and a few
            # group sizes.  A data row has many more numbers; accepting it as
            # a header would attach every later value to the wrong column.
            if (numeric_count > 4 and not _GROUP_SIZE.search(line)
                    and not re.search(r"\b(?:placebo|group|week|dose|czp|pbo)\b",
                                      line, re.I)):
                break
            if ((_looks_like_header(line)
                 or re.search(r"\b(?:placebo|group|week|dose|czp|pbo)\b",
                              line, re.I))
                    and (_GROUP_SIZE.search(line)
                         or re.search(r"\b(?:week|group|placebo|control|treatment|dose|czp|pbo)\b",
                                      line, re.I))):
                post_header.append(line)
        header_lines.extend(post_header)

        header_cells: List[Cell] = []
        for line in header_lines:
            base = offsets[lines.index(line)] if line in lines else 0
            header_cells.extend(split_cells(line, base))

        rows: List[Row] = []
        section = ""
        for idx in range(body_start, body_end):
            line = lines[idx]
            if not line.strip() or _DELIMITER.match(line):
                continue
            cells = split_cells(line)
            if len(cells) < 2:
                text = normalize_cell(line)
                if text and len(text.split()) <= 8 and not _NUMBER.search(text):
                    section = text
                continue
            if not _NUMBER.search(line):
                # A group row such as "MCS" or "Shoulder flexion".
                text = normalize_cell(line)
                if len(text.split()) <= 8:
                    section = text
                continue
            label = cells[0].text
            if _NUMBER.fullmatch(label) and len(cells) >= 3:
                # Dose header row (0.2 1 5 ...), not an outcome row.
                continue
            rows.append(Row(
                line_no=idx + 1,
                offset=offsets[idx],
                label=label,
                cells=cells[1:],
                section=section,
                raw=line,
            ))

        if rows:
            caption = _caption_before(lines, header_start)
            table_id = "md:" + hashlib.sha256(
                (caption + "\n" + "\n".join(header_lines)).encode("utf-8")
            ).hexdigest()[:16]
            tables.append(Table(
                table_id=table_id,
                caption=caption,
                start=offsets[header_start] if header_start < len(offsets) else 0,
                end=offsets[body_end] if body_end < len(offsets) else len(text),
                line_start=header_start + 1,
                line_end=body_end,
                header_lines=header_lines,
                header_cells=header_cells,
                rows=rows,
                raw="\n".join(lines[header_start:body_end]),
            ))
        i = max(body_end, i + 1)
    return tables


def table_to_prompt(table: Table) -> str:
    """Verbatim table for a reader prompt; no value is normalised."""
    return "\n".join(table.header_lines + [r.raw for r in table.rows])


def rows_matching(table: Table, query: str) -> List[Row]:
    """Rows scored by exact/partial token overlap with an outcome phrase."""
    query_tokens: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", (query or "").lower()):
        if len(token) <= 2 or token in {"the", "and", "for", "with", "from",
                                         "patients", "group", "score", "scores"}:
            continue
        query_tokens.add(token)
        if token.endswith("s") and len(token) > 3:
            query_tokens.add(token[:-1])
    scored: List[Tuple[float, Row]] = []
    for row in table.rows:
        text = row.display_label.lower()
        tokens = set(re.findall(r"[a-z0-9]+", text))
        tokens |= {token[:-1] for token in list(tokens)
                   if token.endswith("s") and len(token) > 3}
        overlap = len(query_tokens & tokens)
        if not overlap:
            continue
        score = overlap / max(1, len(query_tokens))
        if normalize_cell(query).lower() in normalize_cell(text).lower():
            score += 0.75
        scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1].line_no))
    return [row for _, row in scored]

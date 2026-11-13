"""Minimaler XLSX-Leser ohne externe Abhaengigkeit.

Liest ein Arbeitsblatt als Liste von Woerterbuechern ``{Spaltenbuchstabe: Wert}``.
Unterstuetzt sharedStrings, Inline-Strings und Zahlen. Bewusst klein gehalten,
weil im Projekt kein ``openpyxl`` installiert ist und keine neue Abhaengigkeit
eingefuehrt werden soll.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

_ROW = re.compile(r"<row[^>]*>(.*?)</row>", re.S)
_CELL = re.compile(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', re.S)
_VALUE = re.compile(r"<v>(.*?)</v>", re.S)
_TEXT = re.compile(r"<t[^>]*>(.*?)</t>", re.S)


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    payload = archive.read("xl/sharedStrings.xml").decode("utf-8")
    strings = []
    for item in re.findall(r"<si>(.*?)</si>", payload, re.S):
        strings.append("".join(_TEXT.findall(item)))
    return strings


def sheet_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
    return re.findall(r'<sheet name="([^"]+)"', workbook)


def read_sheet(path: Path, sheet_index: int = 1) -> list[dict[str, str]]:
    """Liest das n-te Arbeitsblatt (1-basiert) als Zeilenliste."""
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        payload = archive.read(f"xl/worksheets/sheet{sheet_index}.xml").decode("utf-8")
    rows: list[dict[str, str]] = []
    for match in _ROW.finditer(payload):
        values: dict[str, str] = {}
        for column, attributes, body in _CELL.findall(match.group(1)):
            raw = _VALUE.search(body)
            kind = re.search(r't="([^"]+)"', attributes)
            if raw is None:
                value = "".join(_TEXT.findall(body))
            elif kind and kind.group(1) == "s":
                value = shared[int(raw.group(1))]
            else:
                value = raw.group(1)
            values[column] = value.strip()
        rows.append(values)
    return rows


def header_map(row: dict[str, str]) -> dict[str, str]:
    """Bildet Spaltenname auf Spaltenbuchstaben ab (erste Fundstelle gewinnt)."""
    mapping: dict[str, str] = {}
    for column, name in row.items():
        if name and name not in mapping:
            mapping[name] = column
    return mapping

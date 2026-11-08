"""Aus einer Textdatei ein PDF mit echter Textebene bauen (ohne Fremdbibliothek).

Gegenstueck zu ``make_scan_probe.py``: dort entsteht ein PDF ohne Textlayer
(Scan), hier eines, aus dem jeder Extraktor den Text wieder herausliest. Damit
laesst sich die PDF-Kette probelaufen, bevor echte Verlags-PDFs eintreffen.

Nur Standardbibliothek: eine Seite, Helvetica, eine Zeile je ``Tj``-Anweisung.
Zeilenumbrueche der Quelldatei werden uebernommen, lange Zeilen nicht
umgebrochen - die Quelldatei bestimmt das Layout.

Aufruf:
    .venv/bin/python.exe scripts/make_text_pdf.py <quelle.txt> <ziel.pdf>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PAGE_W, PAGE_H = 595.0, 842.0
MARGIN = 50.0
FONT_SIZE = 11.0
LEADING = 14.0
MAX_LINES = int((PAGE_H - 2 * MARGIN) / LEADING)


def escape(text: str) -> str:
    """PDF-String escapen: Backslash und Klammern."""
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_text_pdf(lines: list[str]) -> bytes:
    """Minimales PDF mit einer Seite und echtem Textlayer."""
    if len(lines) > MAX_LINES:
        raise ValueError(f"zu viele Zeilen: {len(lines)} > {MAX_LINES}")

    body = ["BT", f"/F1 {FONT_SIZE} Tf", f"{LEADING} TL",
            f"{MARGIN} {PAGE_H - MARGIN} Td"]
    for line in lines:
        body.append(f"({escape(line)}) Tj T*")
    body.append("ET")
    stream = "\n".join(body).encode("latin-1", "replace")

    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        (f"<</Type/Page/Parent 2 0 R/MediaBox[0 0 {PAGE_W:.0f} {PAGE_H:.0f}]"
         f"/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>").encode("ascii"),
        b"<</Length %d>>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for num, body_obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{num} 0 obj\n".encode("ascii") + body_obj + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (f"trailer\n<</Size {len(objects) + 1}/Root 1 0 R>>\n"
            f"startxref\n{xref_pos}\n%%EOF\n").encode("ascii")
    return bytes(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Textdatei, eine Zeile je PDF-Zeile")
    ap.add_argument("target", help="Ziel-PDF")
    args = ap.parse_args(argv[1:])

    source, target = Path(args.source), Path(args.target)
    if not source.is_file():
        print(f"Quelle fehlt: {source}")
        return 2
    lines = source.read_text(encoding="utf-8").splitlines()
    try:
        data = build_text_pdf(lines)
    except ValueError as exc:
        print(exc)
        return 2
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"{target}  {len(lines)} Zeilen  {target.stat().st_size} Bytes (mit Textlayer)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

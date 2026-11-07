"""Markdown-Briefing in ein PDF rendern (vorhandene Edge-Kette).

Nutzt research_agent/report_pdf.py: python-markdown rendert den Text, Edge
druckt ihn headless. Kein zusaetzlicher PDF-Renderer, keine neue Abhaengigkeit.

Aufruf:
    .venv/bin/python.exe scripts/make_briefing_pdf.py docs/briefing.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research_agent.report_pdf import markdown_to_pdf


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Aufruf: make_briefing_pdf.py <pfad.md>")
        return 2
    md_path = Path(argv[1])
    if not md_path.is_file():
        print(f"Datei fehlt: {md_path}")
        return 2
    pdf = markdown_to_pdf(md_path)
    if not pdf:
        print("PDF-Export fehlgeschlagen (Edge nicht gefunden oder kein Output)")
        return 1
    size = Path(pdf).stat().st_size
    print(f"PDF: {pdf} ({size} Bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

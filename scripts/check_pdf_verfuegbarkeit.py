"""Offline pruefen, welche Korpus-Dokumente als PDF belegbar sind.

Hintergrund (offene Frage 2 aus ``probleme_und_offene_fragen_20261105.md``):
Lauf 1 hat 33 Dokumente mit PMCID gesammelt, aber nur XML geladen. Vor einem
Netzlauf soll klar sein, fuer welche Quellen ein PDF schon lokal liegt oder
ueber PMC erreichbar waere - ohne einen einzigen Netzaufruf.

Das Skript behauptet nichts, was es nicht belegen kann. Drei Belegklassen:

* ``lokale_pdf``  - PDF-Datei liegt im Projekt, Zuordnung ueber die
  ``source_texts.original_pdf_path`` der Lauf-DB (das ist die einzige
  belastbare DOI-zu-Hash-Zuordnung; die Dateinamen sind Hashes).
* ``lokale_xml``  - Volltext-XML liegt unter ``--xml-dir`` oder in der
  Inbox (``data/fulltext_inbox``), benannt nach der DOI.
* ``pmc_oa``      - die gespeicherte Europe-PMC-Antwort meldet
  ``isOpenAccess = Y`` und eine PMCID; daraus laesst sich die PDF-Adresse
  ableiten. **Abgeleitet, nicht verifiziert** - die Pruefung braucht Netz.

Publisher-PDFs (Unpaywall) sind offline **nicht** belegbar; das Skript
schreibt dafuer ``unbekannt`` statt einer Vermutung.

Read-only, kein Netz, kein Modell. Aufruf:

    .venv/bin/python.exe scripts/check_pdf_verfuegbarkeit.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PMC_PDF = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextPDF"
PMC_RENDER = "https://europepmc.org/articles/{pmc}?pdf=render"


def _rel(path: Path) -> str:
    """Projektrelativer Pfad mit Schraegstrichen, auch bei relativer Eingabe."""
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def inbox_names(doi: str) -> list:
    """Dateinamen, unter denen die Inbox eine DOI ablegen kann."""
    doi = str(doi or "").strip()
    if not doi:
        return []
    names = []
    for sep in ("-", "_"):
        names.append(doi.replace("/", sep))
    names.extend(n.lower() for n in list(names))
    return list(dict.fromkeys(names))


def pdf_by_doi(db_path: Path) -> dict:
    """doi -> PDF-Pfad aus der Lauf-DB (nur vorhandene Dateien)."""
    if not db_path.exists():
        return {}
    mapping = {}
    try:
        con = sqlite3.connect(str(db_path))
        rows = con.execute(
            "select s.doi, st.original_pdf_path from source_texts st "
            "join sources s on s.id = st.source_id "
            "where coalesce(st.original_pdf_path, '') <> ''"
        ).fetchall()
        con.close()
    except sqlite3.Error:
        return {}
    for doi, path in rows:
        doi = str(doi or "").strip().lower()
        path = str(path or "").strip()
        if not doi or not path:
            continue
        candidate = ROOT / "data" / path
        if candidate.exists():
            mapping.setdefault(doi, str(candidate.relative_to(ROOT)).replace("\\", "/"))
    return mapping


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/bench/sol/q1_stichprobe_20261108.json")
    parser.add_argument("--xml-dirs", nargs="+",
                        default=["data/bench/sol/xml_q1", "data/bench/sol/xml",
                                 "data/bench/xml_all"])
    parser.add_argument("--inbox-dir", default="data/fulltext_inbox")
    parser.add_argument("--run-db", default="data/bench/backfill/run1.db")
    parser.add_argument("--out", default="data/bench/sol/pdf_verfuegbarkeit_20261108.json")
    parser.add_argument("--md", default="data/bench/sol/pdf_verfuegbarkeit_20261108.md")
    args = parser.parse_args(argv)

    docs = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    xml_dirs = [Path(item) if Path(item).is_absolute() else ROOT / item
                for item in args.xml_dirs]
    inbox_dir = Path(args.inbox_dir)
    if not inbox_dir.is_absolute():
        inbox_dir = ROOT / inbox_dir
    pdfs = pdf_by_doi(Path(args.run_db))

    entries = []
    counts = Counter()
    for doc in docs:
        doi = str(doc.get("doi") or "").strip()
        pmc = str(doc.get("pmc") or "").strip()
        local_xml = None
        for directory in xml_dirs:
            candidate = directory / f"{pmc}.xml" if pmc else None
            if candidate and candidate.exists():
                local_xml = candidate
                break

        inbox = None
        for name in inbox_names(doi):
            for suffix in (".xml", ".pdf"):
                candidate = inbox_dir / f"{name}{suffix}"
                if candidate.exists():
                    inbox = candidate
                    break
            if inbox:
                break

        local_pdf = pdfs.get(doi.lower())
        if local_pdf:
            counts["lokale_pdf"] += 1
        elif local_xml or inbox:
            counts["lokale_xml"] += 1
        elif pmc:
            counts["nur_pmc_abgeleitet"] += 1
        else:
            counts["keine_datei"] += 1

        entries.append({
            "doi": doi,
            "pmc": pmc,
            "title": str(doc.get("title") or "")[:180],
            "year": str(doc.get("year") or ""),
            "query": str(doc.get("query") or ""),
            "lokale_pdf": bool(local_pdf),
            "lokale_pdf_pfad": local_pdf or "",
            "lokale_xml": bool(local_xml),
            "lokale_xml_pfad": _rel(local_xml) if local_xml else "",
            "inbox_datei": _rel(inbox) if inbox else "",
            "pmc_pdf_url": PMC_PDF.format(pmc=pmc) if pmc else "",
            "pmc_render_url": PMC_RENDER.format(pmc=pmc) if pmc else "",
            "pmc_pdf_beleg": ("abgeleitet: PMCID vorhanden und Europe PMC meldet "
                              "isOpenAccess = Y (gespeicherte Suchantwort), "
                              "nicht verifiziert") if pmc else "",
            "publisher_pdf": "unbekannt (Unpaywall offline nicht belegbar)",
        })

    report = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "manifest": args.manifest,
        "documents": len(entries),
        "verfuegbarkeit": dict(counts),
        "belege": {
            "lokale_pdf": "data/bench/backfill/run1.db: source_texts.original_pdf_path",
            "lokale_xml": ", ".join(str(d) for d in xml_dirs) + f" und {inbox_dir}",
            "pmc_pdf": "data/bench/sol/search_europepmc.json: isOpenAccess",
        },
        "grenzen": [
            "Kein Netzaufruf: PMC-PDF-Adressen sind abgeleitet, nicht abgerufen.",
            "Europe PMC meldet isOpenAccess fuer alle 1067 gespeicherten Treffer "
            "als Y - das Feld unterscheidet hier nicht, es belegt nur den OA-Zugang.",
            "Publisher-PDFs brauchen Unpaywall/Crossref-Links; beide sind lokal "
            "nicht gespeichert, also unbekannt statt geraten.",
            "Die Zuordnung lokaler PDFs laeuft ueber die DOI der Lauf-DB; Dateien "
            "ohne dort eingetragene DOI bleiben unzuordenbar.",
        ],
        "eintraege": entries,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# PDF-Verfuegbarkeit der 33 Korpus-Dokumente (offline)",
        "",
        f"Stand: {report['generated']}. Grundlage: {args.manifest}. "
        "Kein Netzaufruf.",
        "",
        "| Beleg | Dokumente |",
        "|---|---:|",
        f"| lokale PDF | {counts.get('lokale_pdf', 0)} |",
        f"| lokale XML (Korpus oder Inbox) | {counts.get('lokale_xml', 0)} |",
        f"| nur PMC-PDF abgeleitet | {counts.get('nur_pmc_abgeleitet', 0)} |",
        f"| keine Datei | {counts.get('keine_datei', 0)} |",
        f"| **Summe** | **{len(entries)}** |",
        "",
        "## Grenzen",
        "",
    ]
    lines += [f"- {item}" for item in report["grenzen"]]
    lines += ["", "## Dokumente", "",
              "| DOI | PMCID | lokal PDF | lokal XML | Inbox | PMC-PDF |",
              "|---|---|---:|---:|---|---|"]
    for entry in entries:
        lines.append(
            f"| {entry['doi']} | {entry['pmc']} | "
            f"{'ja' if entry['lokale_pdf'] else '-'} | "
            f"{'ja' if entry['lokale_xml'] else '-'} | "
            f"{'ja' if entry['inbox_datei'] else '-'} | "
            f"{'abgeleitet' if entry['pmc_pdf_url'] else '-'} |")
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"documents": len(entries), "verfuegbarkeit": dict(counts)},
                     ensure_ascii=False))
    print(f"JSON: {args.out}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

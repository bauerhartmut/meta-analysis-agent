"""Neu gelieferte PDFs lesen, je Datei triagieren, k-Stand fortschreiben.

Die Lesekette selbst ist ``scripts/read_pdf_corpus.py``; dieses Skript ruft sie
auf und macht daraus den Ablauf aus
``data/bench/sol2/warteliste_nach_lieferung_20261108.md``:

  1. lesen (PDF -> Text -> Arme/Tabellen, deterministisch, offline),
  2. je Datei einordnen (Scan, Endpunkt nicht berichtet, Leser-Luecke, poolbar),
  3. k gegen das Schritt-Ziel fortschreiben,
  4. Dateien gegen die Zugangsliste abgleichen (fehlend / fremd).

Alle Zahlen stammen aus dem Bericht der Lesekette und aus der Zugangsliste.
Nichts wird geschaetzt; fehlende Artikel bleiben als Luecke stehen.

Aufruf:
    .venv/bin/python.exe scripts/triage_lieferung.py \
        --dir data/bench/sol2/volltext \
        --json data/bench/sol2/lieferung.json \
        --md data/bench/sol2/lieferung.md

Exit-Code 2 heisst: im Ordner liegt keine PDF - dann ist der Stand nicht
fortgeschrieben, und das soll ein Automatiklauf nicht als Erfolg melden.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
for path in (ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import read_pdf_corpus  # noqa: E402

# Zustand -> was der Befund bedeutet und was zu tun ist (Warteliste, Schritt 2).
AKTIONEN = {
    "poolbar": "Zeile poolbar - weiter zu Schritt 4 (poolen)",
    "scan": "kein Textlayer - mit Bitte um Textebene nachbestellen oder "
            "abtippen, nicht als leere Studie buchen",
    "leser_luecke": "SOL-Zeile erkannt, aber keine gespeichert - Zitat suchen, "
                    "erst dann eine Regel mit Testfall ergaenzen",
    "sol_nicht_poolbar": "SOL-Zeile vorhanden, aber kein poolbarer Effekt - "
                         "Effekttyp im Bericht pruefen",
    "kandidaten_abgelehnt": "Kandidaten gefunden, alle abgelehnt - "
                            "Ablehnungsgrund im Bericht pruefen",
    "endpunkt_nicht_berichtet": "Endpunkt nicht berichtet - als 'nicht "
                                "berichtet' zaehlen, kein Kettenfehler",
}

PMC_REFERENZ = "PMC3489506"


def stamm_pmid(name: str) -> str | None:
    """PMID aus dem Dateinamen: erste Ziffernfolge mit 6 bis 9 Stellen."""
    match = re.search(r"(?<!\d)(\d{6,9})(?!\d)", Path(str(name or "")).stem)
    return match.group(1) if match else None


def load_erwartet(path: Path) -> dict[str, dict]:
    """Zugangsliste als {pmid: Eintrag}; fehlende Datei ergibt leere Liste."""
    path = Path(path)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        out: dict[str, dict] = {}
        for row in rows:
            pmid = str(row.get("pmid") or "").strip()
            if not pmid:
                continue
            out[pmid] = {
                "prioritaet": str(row.get("prioritaet") or "").strip().upper(),
                "doi": str(row.get("doi") or "").strip(),
                "titel": str(row.get("titel") or "").strip(),
            }
    return out


def triage_dokument(doc: dict) -> str:
    """Zustand einer gelesenen Datei nach der Triage-Tabelle der Warteliste."""
    if "error" in doc:
        return "scan"
    if int(doc.get("sol_poolable") or 0) > 0:
        return "poolbar"
    sol_rows = int(doc.get("sol_rows") or 0)
    stored = int(doc.get("arm_stored") or 0) + int(doc.get("direct_stored") or 0)
    candidates = (int(doc.get("arm_candidates") or 0)
                  + int(doc.get("direct_candidates") or 0))
    if sol_rows > 0:
        return "leser_luecke" if stored == 0 else "sol_nicht_poolbar"
    if candidates > 0:
        return "kandidaten_abgelehnt"
    return "endpunkt_nicht_berichtet"


def k_stand(basis_k: int, poolbar: int, ziel: int) -> dict:
    """k nach dieser Lieferung, Abstand zum Ziel, ohne Rundung oder Schaetzung."""
    basis = max(0, int(basis_k))
    zuwachs = max(0, int(poolbar))
    neu = basis + zuwachs
    return {
        "basis_k": basis,
        "zuwachs": zuwachs,
        "k_neu": neu,
        "ziel": int(ziel),
        "erreicht": neu >= int(ziel),
        "fehlt_bis_ziel": max(0, int(ziel) - neu),
    }


def tabellenzeile(doc: dict) -> str:
    """Eine Zeile der Dateitabelle; fehlende Werte als '-', nie 'None'."""

    def zelle(value) -> str:
        return "-" if value is None or value == "" else str(value)

    chars = "-" if doc.get("error") else doc.get("chars")
    return (f"| {zelle(doc.get('file'))} | {zelle(doc.get('pmid'))} | "
            f"{zelle(doc.get('prioritaet'))} | {zelle(doc.get('zustand'))} | "
            f"{zelle(chars)} | {zelle(doc.get('sol_rows'))} | "
            f"{zelle(doc.get('sol_poolable'))} |")


def naechster_schritt(k: dict, zustaende: list[str]) -> str:
    """Ein Satz, der aus dem gemessenen k folgt - keine Prognose."""
    if k["erreicht"]:
        return ("k >= Ziel: poolen (Warteliste Schritt 4). Bei k = 2 ist "
                "I-Quadrat per Definition 0 - das hinschreiben, nicht als "
                "Heterogenitaetsbefund verkaufen.")
    zaehler = Counter(zustaende)
    if zaehler.get("scan"):
        return ("Ziel nicht erreicht, mindestens eine Datei ohne Textebene: "
                "mit Bitte um Textebene nachbestellen und erneut triagieren. "
                "Keine gepoolte Zahl.")
    if zaehler.get("leser_luecke") or zaehler.get("kandidaten_abgelehnt"):
        return ("Ziel nicht erreicht, aber Kandidaten vorhanden: erst die "
                "Ablehnungsgruende im Bericht aufloesen (Regel plus Testfall). "
                "Keine gepoolte Zahl.")
    return ("Ziel nicht erreicht und kein Kettenfehler: B-Liste bestellen "
            "oder die Untersuchung mit dem Befund 'Berichtsstil traegt keine "
            "Arm-Mittelwerte' abschliessen. Keine gepoolte Zahl.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="data/bench/sol2/volltext")
    parser.add_argument("--erwartet",
                        default="data/bench/sol2/zugangsliste_20261108.csv")
    parser.add_argument("--prioritaet", default="A",
                        help="Prioritaetsstufe, die als angefordert gilt")
    parser.add_argument("--basis-k", type=int, default=1,
                        help="k vor dieser Lieferung (Default 1: PMC3489506)")
    parser.add_argument("--ziel", type=int, default=2,
                        help="Schritt-Ziel; Gesamtziel k >= 5 nur mit A + B")
    parser.add_argument("--work-dir", default="data/bench/sol2")
    parser.add_argument("--json", default="data/bench/sol2/lieferung.json")
    parser.add_argument("--md", default="data/bench/sol2/lieferung.md")
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument("--min-chars", type=int, default=2000)
    args = parser.parse_args(argv)

    pdfs = sorted(Path(args.dir).glob("*.pdf"))
    if not pdfs:
        print(f"keine PDF in {args.dir} - nichts zu triagieren, k unveraendert")
        return 2

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    pdf_json = work / "pdf.json"
    rc = read_pdf_corpus.main([
        "--dir", args.dir,
        "--db", str(work / "pdf.db"),
        "--json", str(pdf_json),
        "--md", str(work / "pdf.md"),
        "--max", str(max(1, args.max)),
        "--min-chars", str(args.min_chars),
    ])
    if rc != 0:
        print(f"Lesekette fehlgeschlagen (rc={rc})")
        return rc

    report = json.loads(pdf_json.read_text(encoding="utf-8"))
    erwartet = load_erwartet(Path(args.erwartet))
    prio = str(args.prioritaet).strip().upper()

    dokumente, zustaende = [], []
    for doc in report.get("documents", []):
        zustand = triage_dokument(doc)
        zustaende.append(zustand)
        pmid = stamm_pmid(doc.get("file", ""))
        eintrag = erwartet.get(pmid or "") or {}
        dokumente.append({
            "file": doc.get("file"),
            "pmid": pmid,
            "prioritaet": eintrag.get("prioritaet", ""),
            "angefordert": bool(eintrag) and eintrag.get("prioritaet") == prio,
            "zustand": zustand,
            "aktion": AKTIONEN[zustand],
            "chars": doc.get("chars"),
            "kurz": bool(doc.get("short")),
            "sol_rows": doc.get("sol_rows"),
            "sol_poolable": doc.get("sol_poolable"),
            "arm_stored": doc.get("arm_stored"),
            "direct_stored": doc.get("direct_stored"),
            "error": doc.get("error", ""),
        })

    poolbar_dateien = sum(1 for d in dokumente if d["zustand"] == "poolbar")
    k = k_stand(args.basis_k, poolbar_dateien, args.ziel)

    geliefert = {d["pmid"] for d in dokumente if d["pmid"]}
    fehlend = [{"pmid": pmid, **eintrag} for pmid, eintrag in sorted(erwartet.items())
               if eintrag.get("prioritaet") == prio and pmid not in geliefert]
    fremd = [d["file"] for d in dokumente if not d["pmid"] or d["pmid"] not in erwartet]

    result = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "directory": str(args.dir),
        "pdfs": report.get("pdfs"),
        "readable": report.get("readable"),
        "basis_k": k["basis_k"],
        "basis_quelle": PMC_REFERENZ,
        "k": k,
        "zustaende": dict(Counter(zustaende).most_common()),
        "documents": dokumente,
        "fehlend": fehlend,
        "fremd": fremd,
        "naechster_schritt": naechster_schritt(k, zustaende),
    }
    Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                               encoding="utf-8")

    lines = [
        "# Lieferung triagiert", "",
        f"Stand: {result['generated']}. Verzeichnis: `{args.dir}`. "
        "Deterministisch, kein Netz, kein Modell.", "",
        f"Basis: k = {k['basis_k']} ({PMC_REFERENZ}, XML-Korpus). "
        f"Schritt-Ziel: k >= {k['ziel']}. Gesamtziel k >= 5 nur mit A + B.", "",
        "## k-Stand", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| k vorher | {k['basis_k']} |",
        f"| poolbare Dateien dieser Lieferung | {k['zuwachs']} |",
        f"| **k nachher** | **{k['k_neu']}** |",
        f"| Schritt-Ziel | {k['ziel']} |",
        f"| erreicht | {'ja' if k['erreicht'] else 'nein'} |",
        f"| fehlt bis Ziel | {k['fehlt_bis_ziel']} |",
        "", "## Je Datei", "",
        "| Datei | PMID | Prio | Zustand | Zeichen | SOL-Zeilen | poolbar |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for d in dokumente:
        lines.append(tabellenzeile(d))
    lines += ["", "### Aktion je Datei", ""]
    for d in dokumente:
        lines.append(f"- `{d['file']}`: {d['aktion']}")
    lines += ["", f"## Nicht geliefert (Prioritaet {prio})", ""]
    if fehlend:
        for eintrag in fehlend:
            doi = f", doi:{eintrag['doi']}" if eintrag.get("doi") else ""
            lines.append(f"- {eintrag['pmid']}{doi} - {eintrag['titel']}")
    else:
        lines.append("- keine Luecke in dieser Stufe")
    if fremd:
        lines += ["", "## Dateien ohne Zuordnung zur Zugangsliste", ""]
        lines += [f"- `{name}`" for name in fremd]
    lines += ["", "## Naechster Schritt", "", result["naechster_schritt"], ""]
    Path(args.md).write_text("\n".join(lines), encoding="utf-8")

    print(f"pdfs={result['pdfs']} lesbar={result['readable']} "
          f"poolbar={k['zuwachs']} k={k['basis_k']}->{k['k_neu']} "
          f"ziel={k['ziel']} erreicht={'ja' if k['erreicht'] else 'nein'}")
    for zustand, count in Counter(zustaende).most_common():
        print(f"  {count:3d}  {zustand}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

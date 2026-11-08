"""A/B-Gegencheck der Spaltenabstands-Erkennung auf den vorhandenen .txt-Texten.

Der PDF-Lauf (``vergleich_volltext_columnar.py``) konnte nur eine von drei
Dateien lesen: pypdf gewinnt aus ``23098680.pdf`` keinen Text, obwohl daneben
eine 853-KB-``.txt`` liegt, und ``35120753.pdf`` ist HTML statt PDF. Dieser
Lauf nimmt deshalb die bereits vorhandenen ``.txt``-Dateien als Textquelle und
laesst die Kette sonst unveraendert.

Technisch wird nur ``read_pdf_corpus._pdf_to_text`` ersetzt: es liefert den
Inhalt der gleichnamigen ``.txt``. Damit die Kette ihre ``*.pdf``-Schleife
behaelt, liegt in einem temporaeren Verzeichnis je ``.txt`` eine leere
Platzhalterdatei ``<stem>.pdf``; gelesen wird nie sie, sondern der Text.

Gemessen wird wie beim PDF-Lauf zweimal: **vorher** mit abgeschalteter neuer
Erkennung (``_looks_columnar`` liefert False), **nachher** mit aktiver.
Kein Netz, kein Modell.

Aufruf:
    .venv/bin/python.exe scripts/vergleich_txt_columnar.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
for path in (ROOT, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import read_pdf_corpus  # noqa: E402
import triage_lieferung  # noqa: E402
import research_agent.research.table_extractor as te  # noqa: E402

TXT_DIR = ROOT / "data/bench/sol2/volltext"
OUT_DIR = ROOT / "data/bench/sol2/gegencheck"
PDF_REFERENZ = OUT_DIR / "gegencheck_20261108.json"

KENNZAHLEN = ("chars", "blocks", "arm_stored", "direct_stored", "rows",
              "sol_rows", "sol_poolable")


def txt_quelle(pfad) -> str | None:
    """Text aus der gleichnamigen .txt statt aus der PDF."""
    txt = TXT_DIR / (Path(pfad).stem + ".txt")
    if not txt.exists():
        return None
    return txt.read_text(encoding="utf-8", errors="replace").strip() or None


def lauf(aktiv: bool, workdir: Path) -> dict:
    """Eine volle Lesekette auf den .txt-Texten; Erkennung an oder aus."""
    original_looks = te._looks_columnar
    original_pdf = read_pdf_corpus._pdf_to_text
    marke = "nachher" if aktiv else "vorher"
    te._looks_columnar = (original_looks if aktiv else (lambda line: False))
    read_pdf_corpus._pdf_to_text = txt_quelle
    try:
        js = workdir / f"{marke}.json"
        rc = read_pdf_corpus.main([
            "--dir", str(workdir),
            "--db", str(workdir / f"{marke}.db"),
            "--json", str(js),
            "--md", str(workdir / f"{marke}.md"),
            "--max", "20",
            "--min-chars", "2000",
        ])
        if rc != 0:
            raise SystemExit(f"Lesekette {marke} fehlgeschlagen (rc={rc})")
        return json.loads(js.read_text(encoding="utf-8"))
    finally:
        te._looks_columnar = original_looks
        read_pdf_corpus._pdf_to_text = original_pdf


def kennzahlen(report: dict) -> dict:
    out = {}
    for doc in report.get("documents", []):
        eintrag = {name: doc.get(name) for name in KENNZAHLEN}
        eintrag["error"] = bool(doc.get("error"))
        eintrag["zustand"] = triage_lieferung.triage_dokument(doc)
        eintrag["sol"] = doc.get("sol", [])
        out[doc.get("file")] = eintrag
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    texte = sorted(TXT_DIR.glob("*.txt"))
    if not texte:
        raise SystemExit(f"keine .txt in {TXT_DIR}")

    with tempfile.TemporaryDirectory(prefix="txt_lauf_") as tmp:
        workdir = Path(tmp)
        for txt in texte:
            (workdir / (txt.stem + ".pdf")).write_bytes(b"")
        vorher = kennzahlen(lauf(False, workdir))
        nachher = kennzahlen(lauf(True, workdir))

    dateien = sorted(set(vorher) | set(nachher))
    abweichungen = []
    for name in dateien:
        a, b = vorher.get(name, {}), nachher.get(name, {})
        for feld in KENNZAHLEN + ("zustand",):
            if a.get(feld) != b.get(feld):
                abweichungen.append({"file": name, "feld": feld,
                                     "vorher": a.get(feld), "nachher": b.get(feld)})

    referenz = {}
    if PDF_REFERENZ.exists():
        alt = json.loads(PDF_REFERENZ.read_text(encoding="utf-8"))
        for name, eintrag in alt.get("vorher", {}).items():
            if name[:-4] + ".txt" in {p.name for p in texte}:
                referenz[name] = {"blocks": eintrag.get("blocks"),
                                  "sol_rows": eintrag.get("sol_rows"),
                                  "error": bool(eintrag.get("error"))}

    groessen = {}
    for txt in texte:
        groessen[txt.stem + ".txt"] = txt.stat().st_size

    result = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "directory": str(TXT_DIR.relative_to(ROOT)),
        "dateien": len(dateien),
        "groessen": groessen,
        "vorher": vorher,
        "nachher": nachher,
        "pdf_referenz": referenz,
        "abweichungen": abweichungen,
    }
    (OUT_DIR / "gegencheck_txt_20261108.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    def summe(werte: dict, feld: str) -> int:
        return sum(int(v.get(feld) or 0) for v in werte.values())

    lines = [
        "# Gegencheck auf den vorhandenen .txt-Texten",
        "",
        f"Stand: {result['generated']}. Verzeichnis: `{result['directory']}`. "
        "Deterministisch, kein Netz, kein Modell.",
        "",
        "Textquelle ist die bereits vorhandene `.txt`; ersetzt wird nur "
        "`read_pdf_corpus._pdf_to_text`, der Rest der Kette ist identisch. "
        "**vorher** = neue Erkennung aus, **nachher** = an.",
        "",
        "## Gesamt",
        "",
        "| Kennzahl | vorher | nachher |",
        "|---|---:|---:|",
    ]
    for feld in ("chars", "blocks", "arm_stored", "direct_stored", "rows",
                 "sol_rows", "sol_poolable"):
        lines.append(f"| {feld} | {summe(vorher, feld)} | {summe(nachher, feld)} |")
    lines.append(f"| Abweichungen | - | **{len(abweichungen)}** |")

    lines += ["", "## Je Datei", "",
              "| Datei | Bytes | Zeichen | Bloecke | Arme | direkt | SOL | poolbar | Zustand |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for name in dateien:
        a, b = vorher.get(name, {}), nachher.get(name, {})
        lines.append(
            f"| {name} | {groessen.get(name, 0)} | {a.get('chars')} | "
            f"{a.get('blocks')} -> {b.get('blocks')} | "
            f"{a.get('arm_stored')} -> {b.get('arm_stored')} | "
            f"{a.get('direct_stored')} -> {b.get('direct_stored')} | "
            f"{a.get('sol_rows')} -> {b.get('sol_rows')} | "
            f"{a.get('sol_poolable')} -> {b.get('sol_poolable')} | "
            f"{a.get('zustand')} -> {b.get('zustand')} |")

    if referenz:
        lines += ["", "## Gegenueberstellung mit dem PDF-Lauf", "",
                  "| Datei | PDF: Bloecke | PDF: SOL | txt: Bloecke | txt: SOL |",
                  "|---|---:|---:|---:|---:|"]
        for name in dateien:
            ref = referenz.get(name.replace(".txt", ".pdf"), {})
            txt_blocks = nachher.get(name, {}).get("blocks")
            txt_sol = nachher.get(name, {}).get("sol_rows")
            ref_blocks = "Fehler" if ref.get("error") else ref.get("blocks")
            lines.append(f"| {name} | {ref_blocks} | {'-' if ref.get('sol_rows') is None else ref.get('sol_rows')} | "
                         f"{txt_blocks} | {txt_sol} |")
        lines.append("")
        lines.append("Der PDF-Lauf konnte `23098680.pdf` nicht lesen; die `.txt` "
                     "daneben enthaelt 853 KB Text, der bislang ungenutzt war.")

    lines += ["", "## Abweichungen", ""]
    if abweichungen:
        for eintrag in abweichungen:
            lines.append(f"- `{eintrag['file']}`: {eintrag['feld']} "
                         f"{eintrag['vorher']!r} -> {eintrag['nachher']!r}")
    else:
        lines.append("- keine: die Erweiterung aendert an diesen Texten nichts.")

    lines += ["", "## SOL-Zeilen im Detail (nachher)", ""]
    leer = True
    for name in dateien:
        for eintrag in nachher.get(name, {}).get("sol", []):
            leer = False
            lines.append(f"- `{name}`: {eintrag.get('outcome')} | "
                         f"{eintrag.get('type')} | {eintrag.get('effect')} | "
                         f"{eintrag.get('unit')} | n={eintrag.get('n')}")
    if leer:
        lines.append("- keine")

    if any(e["feld"] in ("chars", "blocks") for e in abweichungen):
        lines += [
            "", "## Warum `chars` und `blocks` steigen", "",
            "`normalize()` in `meta/pdf_text.py` schuetzt erkannte "
            "Tabellenbereiche vor der Fliesstext-Verklebung (`_table_spans` "
            "-> `find_table_blocks`). Erkennt die neue Fassung mehr Bereiche, "
            "bleiben diese Zeilen roh stehen: Zeilenumbrueche und "
            "Bindestriche werden nicht aufgeloest, der Text wird laenger.",
            "",
            "Der Effekt ist also nicht 'drei Tabellen mehr gefunden', sondern "
            "'drei Bereiche ueberleben die Normalisierung und werden danach "
            "erkannt'. Kausal haengt beides aneinander: die Erkennung wirkt "
            "zweimal, einmal als Schutz in `normalize`, einmal als Leser in "
            "`find_table_blocks`.",
            "",
            "Folge: `arm_stored`, `direct_stored` und `sol_rows` bleiben bei 0, "
            "aber der Fliesstext-Leser sieht bei `23098680.txt` anderen Text "
            "als vorher - das ist eine echte Verhaltensaenderung, keine "
            "Nullnummer.",
        ]

    lines += [
        "", "## Grenzen", "",
        "- Zwei `.txt`-Dateien; keine Aussage ueber Verlags-PDFs insgesamt.",
        "- Die `.txt` stammt nicht aus pypdf, sondern aus einem frueheren, "
        "anderen Leseweg. Ihre Zeilenumbrueche sind daher nicht identisch mit "
        "dem, was die PDF-Kette produzieren wuerde.",
        "- Der Vorher-Zustand kommt aus einem Monkeypatch "
        "(`_looks_columnar` -> False), nicht aus einem alten Code-Stand.",
        "- Treffer hier sagen, was die Erweiterung auf diesem Text findet, "
        "nicht, dass sie in der Produktionskette ankommt - die liest weiterhin "
        "die PDF.",
    ]
    (OUT_DIR / "gegencheck_txt_20261108.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    print(f"dateien={len(dateien)} abweichungen={len(abweichungen)}")
    for feld in ("chars", "blocks", "arm_stored", "direct_stored", "rows",
                 "sol_rows", "sol_poolable"):
        print(f"  {feld}: {summe(vorher, feld)} -> {summe(nachher, feld)}")
    for name in dateien:
        a, b = vorher.get(name, {}), nachher.get(name, {})
        print(f"  {name}: blocks {a.get('blocks')} -> {b.get('blocks')} | "
              f"sol {a.get('sol_rows')} -> {b.get('sol_rows')} | "
              f"zustand {a.get('zustand')} -> {b.get('zustand')}")
    for eintrag in abweichungen:
        print(f"  ABWEICHUNG {eintrag['file']} {eintrag['feld']}: "
              f"{eintrag['vorher']} -> {eintrag['nachher']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

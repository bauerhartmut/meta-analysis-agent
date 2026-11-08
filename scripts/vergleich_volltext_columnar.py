"""A/B-Gegencheck der Spaltenabstands-Erkennung auf den vorhandenen Volltexten.

Frage: Aendert die neue Erkennung von Tabellen mit reinem Spaltenabstand
irgendetwas an den bereits gelesenen Volltexten? Gemessen wird zweimal
dieselbe Kette (``read_pdf_corpus``): einmal mit abgeschalteter neuer
Erkennung ("vorher", ``_looks_columnar`` liefert immer False) und einmal mit
aktiver ("nachher").

Verglichen werden je PDF: Bloecke, gespeicherte Arme, direkte Effekte,
SOL-Zeilen, poolbare SOL-Zeilen und der Triage-Zustand. Zusaetzlich wird je
Datei festgehalten, ob sie ueberhaupt eine lesbare PDF ist - sonst sagt ein
"keine Abweichung" nichts. Kein Netz, kein Modell.

Aufruf:
    .venv/bin/python.exe scripts/vergleich_volltext_columnar.py
"""

from __future__ import annotations

import json
import sys
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

PDF_DIR = ROOT / "data/bench/sol2/volltext"
OUT_DIR = ROOT / "data/bench/sol2/gegencheck"

KENNZAHLEN = ("chars", "blocks", "arm_stored", "direct_stored", "rows",
              "sol_rows", "sol_poolable")


def datei_befund(name: str) -> dict:
    """Was die Datei tatsaechlich ist: PDF, HTML-Beifang, Groesse, txt daneben."""
    pfad = PDF_DIR / name
    kopf = pfad.read_bytes()[:16] if pfad.exists() else b""
    txt = PDF_DIR / (pfad.stem + ".txt")
    return {
        "bytes": pfad.stat().st_size if pfad.exists() else 0,
        "header": kopf.decode("latin-1", "replace").strip(),
        "ist_pdf": kopf.lstrip().startswith(b"%PDF"),
        "txt_bytes": txt.stat().st_size if txt.exists() else 0,
    }


def lauf(aktiv: bool) -> dict:
    """Eine volle Lesekette; die neue Erkennung ist an- oder abgeschaltet."""
    original = te._looks_columnar
    marke = "nachher" if aktiv else "vorher"
    te._looks_columnar = original if aktiv else (lambda line: False)
    try:
        js = OUT_DIR / f"{marke}.json"
        rc = read_pdf_corpus.main([
            "--dir", str(PDF_DIR),
            "--db", str(OUT_DIR / f"{marke}.db"),
            "--json", str(js),
            "--md", str(OUT_DIR / f"{marke}.md"),
            "--max", "20",
            "--min-chars", "2000",
        ])
        if rc != 0:
            raise SystemExit(f"Lesekette {marke} fehlgeschlagen (rc={rc})")
        return json.loads(js.read_text(encoding="utf-8"))
    finally:
        te._looks_columnar = original


def kennzahlen(report: dict) -> dict:
    out = {}
    for doc in report.get("documents", []):
        eintrag = {name: doc.get(name) for name in KENNZAHLEN}
        eintrag["zustand"] = triage_lieferung.triage_dokument(doc)
        eintrag["error"] = bool(doc.get("error"))
        eintrag["sol"] = doc.get("sol", [])
        out[doc.get("file")] = eintrag
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vorher = kennzahlen(lauf(False))
    nachher = kennzahlen(lauf(True))

    dateien = sorted(set(vorher) | set(nachher))
    befund = {name: datei_befund(name) for name in dateien}
    abweichungen = []
    for name in dateien:
        a, b = vorher.get(name, {}), nachher.get(name, {})
        for feld in KENNZAHLEN + ("zustand",):
            if a.get(feld) != b.get(feld):
                abweichungen.append({"file": name, "feld": feld,
                                     "vorher": a.get(feld), "nachher": b.get(feld)})

    kette_lesbar = [n for n in dateien if not vorher.get(n, {}).get("error")]
    blind = [n for n in dateien if n not in kette_lesbar]
    mit_sol = [n for n in dateien if int(nachher.get(n, {}).get("sol_rows") or 0) > 0]

    result = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "directory": str(PDF_DIR.relative_to(ROOT)),
        "pdfs": len(dateien),
        "vorher": vorher,
        "nachher": nachher,
        "datei_befund": befund,
        "kette_lesbar": kette_lesbar,
        "blind": blind,
        "mit_sol_zeile": mit_sol,
        "abweichungen": abweichungen,
    }
    (OUT_DIR / "gegencheck_20261108.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    def summe(werte: dict, feld: str) -> int:
        return sum(int(v.get(feld) or 0) for v in werte.values())

    lines = [
        "# Gegencheck: Spaltenabstands-Erkennung auf den vorhandenen Volltexten",
        "",
        f"Stand: {result['generated']}. Verzeichnis: `{result['directory']}`. "
        "Deterministisch, kein Netz, kein Modell.",
        "",
        "Verglichen wird dieselbe Lesekette zweimal: **vorher** mit "
        "abgeschalteter neuer Erkennung (`_looks_columnar` liefert False), "
        "**nachher** mit aktiver Erkennung.",
        "",
        "## Gesamt",
        "",
        "| Kennzahl | vorher | nachher |",
        "|---|---:|---:|",
    ]
    for feld in ("blocks", "arm_stored", "direct_stored", "rows",
                 "sol_rows", "sol_poolable"):
        lines.append(f"| {feld} | {summe(vorher, feld)} | {summe(nachher, feld)} |")
    lines.append(f"| Abweichungen | - | **{len(abweichungen)}** |")

    lines += ["", "## Je Datei", "",
              "| Datei | Bloecke | Arme | direkt | SOL-Zeilen | poolbar | Zustand |",
              "|---|---:|---:|---:|---:|---:|---|"]
    for name in dateien:
        a, b = vorher.get(name, {}), nachher.get(name, {})
        lines.append(
            f"| {name} | {a.get('blocks')} -> {b.get('blocks')} | "
            f"{a.get('arm_stored')} -> {b.get('arm_stored')} | "
            f"{a.get('direct_stored')} -> {b.get('direct_stored')} | "
            f"{a.get('sol_rows')} -> {b.get('sol_rows')} | "
            f"{a.get('sol_poolable')} -> {b.get('sol_poolable')} | "
            f"{a.get('zustand')} -> {b.get('zustand')} |")

    lines += ["", "## Belastbarkeit der Stichprobe", "",
              "| Datei | Bytes | Kopf | echte PDF | txt daneben | durch Kette lesbar |",
              "|---|---:|---|---|---:|---|"]
    for name in dateien:
        b = befund[name]
        lines.append(
            f"| {name} | {b['bytes']} | `{b['header'][:12]}` | "
            f"{'ja' if b['ist_pdf'] else 'nein'} | {b['txt_bytes']} | "
            f"{'ja' if name in kette_lesbar else 'nein'} |")
    lines += [
        "",
        f"- durch die Kette lesbar: {len(kette_lesbar)} von {len(dateien)}",
        f"- ohne Aussage (kein Text aus der PDF gewonnen): {len(blind)}",
        f"- mit mindestens einer SOL-Zeile: {len(mit_sol)}",
        "",
        "Damit ist der Vergleich nur fuer die lesbaren Dateien aussagekraeftig. "
        "Wo `nein` steht, sagt 'keine Abweichung' nichts ueber die Erweiterung, "
        "sondern nur, dass die Kette diese Datei nicht liest.",
    ]

    lines += ["", "## Abweichungen", ""]
    if abweichungen:
        for eintrag in abweichungen:
            lines.append(f"- `{eintrag['file']}`: {eintrag['feld']} "
                         f"{eintrag['vorher']!r} -> {eintrag['nachher']!r}")
    else:
        lines.append("- keine: die Erweiterung aendert an diesen Dateien nichts.")

    lines += ["", "## SOL-Zeilen im Detail (nachher)", ""]
    leer = True
    for name in dateien:
        for eintrag in nachher.get(name, {}).get("sol", []):
            leer = False
            lines.append(f"- `{name}`: {eintrag.get('outcome')} | "
                         f"{eintrag.get('type')} | {eintrag.get('effect')} | "
                         f"{eintrag.get('unit')}")
    if leer:
        lines.append("- keine")

    lines += [
        "", "## Grenzen", "",
        "- Drei Dateien, davon nur ein Teil durch die Kette lesbar; kein Beweis "
        "fuer Verlags-PDFs insgesamt.",
        "- Der Vorher-Zustand wird ueber einen Monkeypatch hergestellt "
        "(`_looks_columnar` -> False), nicht ueber einen alten Code-Stand; "
        "alles andere an der Kette ist identisch.",
        "- `arm_stored` stammt aus dem Fliesstext-Leser und ist von der "
        "Tabellenerkennung hoechstens mittelbar beruehrt.",
        "- Eine vorhandene `.txt` neben einer PDF wird von der Kette nicht "
        "gelesen; wo nur sie Text enthaelt, bleibt die PDF eine Blindstelle.",
    ]
    (OUT_DIR / "gegencheck_20261108.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    print(f"pdfs={len(dateien)} abweichungen={len(abweichungen)} "
          f"lesbar={len(kette_lesbar)} blind={len(blind)} mit_sol={len(mit_sol)}")
    for feld in ("blocks", "arm_stored", "direct_stored", "sol_rows"):
        print(f"  {feld}: {summe(vorher, feld)} -> {summe(nachher, feld)}")
    for eintrag in abweichungen:
        print(f"  ABWEICHUNG {eintrag['file']} {eintrag['feld']}: "
              f"{eintrag['vorher']} -> {eintrag['nachher']}")
    for name in dateien:
        b = befund[name]
        print(f"  {name}: {b['bytes']} B | PDF={b['ist_pdf']} | txt={b['txt_bytes']} B "
              f"| lesbar={'ja' if name in kette_lesbar else 'nein'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

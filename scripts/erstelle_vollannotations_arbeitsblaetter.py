"""Erzeugt Arbeitsblaetter fuer die Vollannotation aller 30 Dokumente.

Read-only. Nutzt die Fundstellen-Logik aus
`scripts/erstelle_probelauf_arbeitsblaetter.py`, schreibt aber je Dokument ein
eigenes Blatt nach `docs/internal/vollannotation_arbeitsblatt_<id10>.md`
sowie eine Uebersicht und ein JSON. Die Blaetter sind fuer A und B identisch
und geben keine Effektzeile vor; die Auszuege sind Fundstellen.
"""

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from erstelle_probelauf_arbeitsblaetter import (  # noqa: E402
    arbeitsblatt, effektstellen, pflichtfelder, tabellen,
)

DOCS = ROOT / "data" / "golden_effects" / "documents.json"
SCHEMA = ROOT / "docs" / "internal" / "goldstandard_schema.json"


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default="docs/internal")
    p.add_argument("--json",
                   default="data/golden_effects/vollannotation_arbeitsblaetter.json")
    p.add_argument("--uebersicht",
                   default="docs/internal/vollannotation_arbeitsblaetter_20261110.md")
    args = p.parse_args(argv)

    daten = json.loads(DOCS.read_text(encoding="utf-8"))
    docs = daten["documents"]
    if len(docs) != daten.get("n_documents", 30):
        print(f"Erwartet {daten.get('n_documents')} Dokumente, gefunden {len(docs)}.")
        return 1
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    pflicht = pflichtfelder(schema)

    eintraege = []
    for doc in docs:
        pfad = ROOT / "data" / doc["path"]
        if not pfad.exists():
            print(f"Volltext fehlt: {pfad}")
            return 1
        text = pfad.read_text(encoding="utf-8")
        tab, eff = tabellen(text), effektstellen(text)
        doc = {**doc, "design_verbatim": doc.get("design_verbatim") or "nicht berichtet"}
        md = arbeitsblatt(doc, {}, text, pflicht, tab, eff)
        ziel = (ROOT / args.out_dir
                / f"vollannotation_arbeitsblatt_{doc['document_id'][:10]}.md")
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(md.rstrip("\n") + "\n", encoding="utf-8")
        eintraege.append({
            "document_id": doc["document_id"],
            "datei": str(ziel.relative_to(ROOT)),
            "titel": doc.get("title"),
            "stratum": doc.get("stratum"),
            "design_category": doc.get("design_category"),
            "design_verbatim": doc.get("design_verbatim"),
            "zeichen": len(text),
            "tabellen": tab,
            "effektstellen": eff,
        })
        print(f"{doc['document_id'][:10]}: {len(tab)} Tabellenstellen, "
              f"{len(eff)} Effektstellen -> {ziel.relative_to(ROOT)}")

    zeilen = [
        "# Vollannotations-Arbeitsblätter (2026-11-10)",
        "",
        "30 Dokumente, je ein Arbeitsblatt. Die Blätter sind für A und B",
        "identisch; sie werden getrennt ausgefüllt, ohne Austausch während der",
        "Annotation. Die Auszüge sind Fundstellen, keine Annotation.",
        "",
        "## Übersicht",
        "",
        "| Dokument | Schicht | Design | Zeichen | Tabellen | Effektstellen | Arbeitsblatt |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in eintraege:
        name = Path(e["datei"]).name
        zeilen.append(
            f"| {e['document_id'][:10]} | {e['stratum']} | "
            f"{e['design_category']} | {e['zeichen']:,} | "
            f"{len(e['tabellen'])} | {len(e['effektstellen'])} | "
            f"[{name}]({name}) |")
    gesamt_tab = sum(len(e["tabellen"]) for e in eintraege)
    gesamt_eff = sum(len(e["effektstellen"]) for e in eintraege)
    zeilen += [
        "",
        f"Summe: {len(eintraege)} Dokumente, {gesamt_tab} Tabellenstellen, "
        f"{gesamt_eff} Effektstellen.",
        "",
        "## Summen nach Schicht",
        "",
        "| Schicht | Dokumente | Tabellen | Effektstellen |",
        "|---|---|---|---|",
    ]
    schichten = OrderedDict()
    for e in eintraege:
        s = schichten.setdefault(e["stratum"], [0, 0, 0])
        s[0] += 1
        s[1] += len(e["tabellen"])
        s[2] += len(e["effektstellen"])
    for name, (n, tab, eff) in schichten.items():
        zeilen.append(f"| {name} | {n} | {tab} | {eff} |")
    zeilen += [
        "",
        "## Ablauf",
        "",
        "1. Arbeitsblatt lesen und den Volltext vollständig prüfen.",
        "2. Jede Effektzeile mit Quote und Unsicherheit erfassen; Dokument",
        "   abschließen (Zeilen oder `no_effect_reason`).",
        "3. `.venv/bin/python.exe scripts/pruefe_goldstandard.py --entwurf "
        "data/golden_effects/goldstandard_A.json` (bzw. B) bis 0 Fehler;",
        "   danach ohne `--entwurf` prüfen.",
        "4. Nach beiden Abgaben: `.venv/bin/python.exe scripts/werte_kappa_probe.py`",
        "   (ohne `--probelauf`); Konflikte mit dritter Stimme, Schwelle 0,80.",
        "",
    ]
    uebersicht = ROOT / args.uebersicht
    uebersicht.parent.mkdir(parents=True, exist_ok=True)
    uebersicht.write_text("\n".join(zeilen).rstrip("\n") + "\n", encoding="utf-8")

    ziel_json = ROOT / args.json
    ziel_json.parent.mkdir(parents=True, exist_ok=True)
    ziel_json.write_text(json.dumps(
        {"dokumente": eintraege, "pflichtfelder": pflicht},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Übersicht: {uebersicht.relative_to(ROOT)}")
    print(f"JSON: {ziel_json.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

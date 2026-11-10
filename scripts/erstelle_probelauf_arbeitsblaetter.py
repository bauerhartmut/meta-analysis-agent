"""Erzeugt Arbeitsblaetter fuer die drei Probelauf-Dokumente.

Read-only. Je Dokument ein Markdown-Arbeitsblatt mit Metadaten, Tabellen-
und Effektfundstellen (Zeilennummer und Auszug, keine Annotation) und den
Pflichtfeldern aus `docs/internal/goldstandard_schema.json`. Die Blaetter
sind fuer A und B identisch; sie geben keine Effektzeile vor.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABELLE = re.compile(r"(?i)table +([0-9]+[a-z]?)")
EFFEKT = re.compile(r"(?i)(95% *CI|CI:|HR *=|OR *=|RR *=|MD *=|"
                    r"mean difference|hazard ratio|odds ratio|risk ratio)")


def _zelle(text: str) -> str:
    return " ".join(str(text or "").replace("|", "/").split()).strip()


def _kurz(text: str, n: int = 220) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def tabellen(text: str) -> list:
    treffer, gesehen = [], set()
    for nr, zeile in enumerate(text.splitlines(), 1):
        for m in TABELLE.finditer(zeile):
            schluessel = (m.group(1).lower(), nr)
            if schluessel in gesehen:
                continue
            gesehen.add(schluessel)
            treffer.append({"tabelle": f"Table {m.group(1)}", "zeile": nr,
                            "auszug": _kurz(zeile)})
    return treffer


def effektstellen(text: str, max_n: int = 25) -> list:
    treffer = []
    for nr, zeile in enumerate(text.splitlines(), 1):
        m = EFFEKT.search(zeile)
        if not m:
            continue
        treffer.append({"zeile": nr, "auszug": _kurz(zeile)})
        if len(treffer) >= max_n:
            break
    return treffer


def pflichtfelder(schema: dict) -> dict:
    defs = schema["$defs"]
    return {"dokument": list(defs["document"]["required"]),
            "effekt": list(defs["effect"]["required"])}


def arbeitsblatt(doc: dict, meta: dict, text: str, pflicht: dict,
                 tab: list, eff: list) -> str:
    titel = doc.get("title") or meta.get("title") or doc["document_id"]
    zeilen = [
        f"# Arbeitsblatt: {titel}",
        "",
        f"- Dokument-ID: `{doc['document_id']}`",
        f"- Volltext: `{doc['path']}` ({len(text):,} Zeichen)",
        f"- Jahr: {doc.get('year') or meta.get('year') or '?'}",
        f"- Schicht: {doc.get('stratum')} | Design: {doc.get('design_category')}",
        f"- Design laut Dokument: {doc.get('design_verbatim')}",
        "",
        "**Für A und B identisch.** Getrennt ausfüllen und während der",
        "Annotation nicht austauschen. Nur Volltext, Anleitung und Schema",
        "verwenden; keine DB-, Modell- oder Fremdausgaben.",
        "",
        "## Vorgehen",
        "1. Volltext vollständig lesen, nicht nur Abstract.",
        "2. Jede Stelle mit quantifiziertem Effekt und Unsicherheit markieren.",
        "3. Je Kombination aus Outcome, Vergleich, Zeitpunkt, Adjustierung und",
        "   Population eine Zeile.",
        "4. Quote exakt kopieren und `quote_start`/`quote_end` im Volltext setzen.",
        "5. Dokument abschließen: Zeilen oder `no_effect_reason`.",
        "",
        "## Tabellenfundstellen",
        "",
    ]
    if tab:
        zeilen += ["| Tabelle | Zeile | Auszug |", "|---|---|---|"]
        for t in tab:
            zeilen.append(f"| {t['tabelle']} | {t['zeile']} | {_zelle(t['auszug'])} |")
    else:
        zeilen.append("Keine Tabellen-Erwähnung gefunden; Tabellen am Layout prüfen.")
    zeilen += ["", "## Textstellen mit Effekt und Unsicherheit", ""]
    if eff:
        zeilen += ["| Zeile | Auszug |", "|---|---|"]
        for e in eff:
            zeilen.append(f"| {e['zeile']} | {_zelle(e['auszug'])} |")
    else:
        zeilen.append("Keine Stelle mit den Mustern gefunden; manuell prüfen.")
    zeilen += [
        "",
        "Die Auszüge sind **Fundstellen, keine Annotation**. Werte nicht",
        "übernehmen, ohne sie am Volltext zu prüfen.",
        "",
        "## Pflichtfelder je Effektzeile",
        "",
        "| Feld | Pflicht |",
        "|---|---|",
    ]
    for feld in pflicht["effekt"]:
        zeilen.append(f"| `{feld}` | ja (Schema) |")
    zeilen += [
        "",
        "Zusätzlich ausfüllen, wenn berichtet: `se`, `ci_level`, `p_value`, `n`,",
        "`adjusted`, `time_point`, `population`, `section`, `page`,",
        "`source_table`, `notes`.",
        "",
        "## Dokument-Check",
        "",
        "Pflichtfelder Dokument: " + ", ".join(f"`{f}`" for f in pflicht["dokument"]) + ".",
        "",
        "- [ ] Jede Zeile hat `quote` exakt und `quote_start`/`quote_end` passend.",
        "- [ ] Kein Effekt umgerechnet, keine Zahl gerundet.",
        "- [ ] Entweder mindestens eine Zeile oder `no_effect_reason`.",
        "- [ ] Grenzfälle nach Anleitung geprüft: 5.2 (Ratio), 5.6 (Median/IQR),",
        "      5.8 (Uebersichtsarbeit), 5.11 (Spannweite über Zeitpunkte).",
        "",
    ]
    return chr(10).join(zeilen)


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default="docs/internal")
    p.add_argument("--json", default="data/golden_effects/probelauf_arbeitsblaetter.json")
    args = p.parse_args(argv)

    quelle = ROOT / "data/golden_effects/goldstandard_A.json"
    docs = [d for d in json.loads(quelle.read_text(encoding="utf-8"))["documents"]
            if d.get("probelauf")]
    if not docs:
        print("Keine Probelauf-Dokumente in goldstandard_A.json.")
        return 1
    meta = {d["document_id"]: d for d in
            json.loads((ROOT / "data/golden_effects/documents.json")
                       .read_text(encoding="utf-8"))["documents"]}
    schema = json.loads((ROOT / "docs/internal/goldstandard_schema.json")
                        .read_text(encoding="utf-8"))
    pflicht = pflichtfelder(schema)

    eintraege = []
    for doc in docs:
        pfad = ROOT / "data" / doc["path"]
        if not pfad.exists():
            print(f"Volltext fehlt: {pfad}")
            return 1
        with open(pfad, encoding="utf-8", newline="") as fh:
            text = fh.read()
        tab = tabellen(text)
        eff = effektstellen(text)
        md = arbeitsblatt(doc, meta.get(doc["document_id"], {}), text, pflicht, tab, eff)
        ziel = ROOT / args.out_dir / f"probelauf_arbeitsblatt_{doc['document_id'][:10]}.md"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(md + chr(10), encoding="utf-8")
        eintraege.append({
            "document_id": doc["document_id"], "datei": str(ziel.relative_to(ROOT)),
            "titel": doc.get("title"), "stratum": doc.get("stratum"),
            "design_category": doc.get("design_category"), "zeichen": len(text),
            "tabellen": tab, "effektstellen": eff,
        })
        print(f"{doc['document_id'][:10]}: {len(tab)} Tabellenstellen, "
              f"{len(eff)} Effektstellen -> {ziel.relative_to(ROOT)}")

    zeilen = [
        "# Probelauf-Arbeitsblätter (2026-11-10)",
        "",
        "Drei Dokumente, je ein Arbeitsblatt. Die Blätter sind für A und B",
        "identisch; sie werden getrennt ausgefüllt, ohne Austausch während der",
        "Annotation. Die Auszüge sind Fundstellen, keine Annotation.",
        "",
        "| Dokument | Schicht | Design | Zeichen | Tabellen | Effektstellen | Arbeitsblatt |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in eintraege:
        name = Path(e["datei"]).name
        zeilen.append(f"| {e['document_id'][:10]} | {e['stratum']} | {e['design_category']} | "
                      f"{e['zeichen']:,} | {len(e['tabellen'])} | {len(e['effektstellen'])} | "
                      f"[{name}]({name}) |")
    zeilen += [
        "",
        "Ablauf: Arbeitsblatt lesen, Volltext annotieren, Gerüst füllen,",
        "`pruefe_goldstandard.py --entwurf` laufen lassen, abgeben. Erst danach",
        "vergleichen.",
        "",
    ]
    uebersicht = ROOT / args.out_dir / "probelauf_arbeitsblaetter_20261110.md"
    uebersicht.write_text(chr(10).join(zeilen) + chr(10), encoding="utf-8")
    ziel_json = ROOT / args.json
    ziel_json.parent.mkdir(parents=True, exist_ok=True)
    ziel_json.write_text(json.dumps({"dokumente": eintraege, "pflichtfelder": pflicht},
                                    ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
    print(f"Übersicht: {uebersicht.relative_to(ROOT)}")
    print(f"JSON: {ziel_json.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

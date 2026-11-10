"""Erzeugt das Arbeitsblatt fuer die 12 Kalibrierungsdokumente.

Read-only. Die 12 Dokumente sind die erste Arbeitsmenge der Vollannotation,
kein separater Kappa-Lauf. Je Dokument wird auf das vorhandene
Vollannotations-Arbeitsblatt verlinkt; die Zahlen kommen aus
`data/golden_effects/vollannotation_arbeitsblaetter.json`.
"""

import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from erstelle_vollannotations_checkliste import ERKLAERUNG, _punkt  # noqa: E402

ERKLAERUNG_KAL = dict(ERKLAERUNG)
ERKLAERUNG_KAL["5.8 gepoolt"] = (
    "5.8: gepoolte Schaetzer als je eine Zeile mit `is_primary: false`; "
    "Dosis-Wirkungs-Peak und Sensitivitaetsanalyse in `notes`."
)

DOCS = ROOT / "data" / "golden_effects" / "documents.json"
BLAETTER = ROOT / "data" / "golden_effects" / "vollannotation_arbeitsblaetter.json"
A = ROOT / "data" / "golden_effects" / "goldstandard_A.json"
B = ROOT / "data" / "golden_effects" / "goldstandard_B.json"
ZIEL = ROOT / "docs" / "internal" / "kalibrierung_arbeitsblatt_20261110.md"
JSON_ZIEL = ROOT / "data" / "golden_effects" / "kalibrierung_arbeitsblatt.json"


def _index(pfad: Path) -> dict:
    return {d["document_id"]: d for d in
            json.loads(pfad.read_text(encoding="utf-8"))["documents"]}


def _stand(index: dict, docs: list) -> tuple:
    zeilen = sum(len(index.get(d["document_id"], {}).get("effects") or [])
                 for d in docs)
    begr = sum(1 for d in docs
               if str(index.get(d["document_id"], {}).get("no_effect_reason")
                      or "").strip())
    offen = sum(1 for d in docs
                if not (index.get(d["document_id"], {}).get("effects") or [])
                and not str(index.get(d["document_id"], {}).get(
                    "no_effect_reason") or "").strip())
    return zeilen, begr, offen


def _hash(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def main() -> int:
    docs = json.loads(DOCS.read_text(encoding="utf-8"))["documents"]
    kal = [d for d in docs if d.get("calibration")]
    if len(kal) != 12:
        print(f"Erwartet 12 Kalibrierungsdokumente, gefunden {len(kal)}.")
        return 1
    bl = {x["document_id"]: x for x in
          json.loads(BLAETTER.read_text(encoding="utf-8"))["dokumente"]}
    ia, ib = _index(A), _index(B)
    za, ba, oa = _stand(ia, kal)
    zb, bb, ob = _stand(ib, kal)

    eintraege = []
    for d in kal:
        did = d["document_id"]
        x = bl.get(did)
        if x is None:
            print(f"Arbeitsblatt fehlt fuer {did[:10]}")
            return 1
        if not (ROOT / x["datei"]).exists():
            print(f"Arbeitsblattdatei fehlt: {x['datei']}")
            return 1
        eintraege.append({
            "document_id": did,
            "datei": x["datei"],
            "titel": d.get("title"),
            "stratum": d.get("stratum"),
            "design_category": d.get("design_category"),
            "design_verbatim": d.get("design_verbatim"),
            "zeichen": x["zeichen"],
            "tabellen": len(x["tabellen"]),
            "effektstellen": len(x["effektstellen"]),
            "punkt": _punkt(d),
        })

    zeilen = [
        "# Kalibrierungsphase: 12 Dokumente (2026-11-10)",
        "",
        "Die 12 Kalibrierungsdokumente sind die **erste Arbeitsmenge** der",
        "Vollannotation, kein separater Kappa-Lauf. A und B annotieren",
        "getrennt; kein Austausch und keine Zwischenabgabe. Die Abgabe und der",
        "Zeilen-Kappa folgen nach allen 30 Dokumenten.",
        "",
        "## Reihenfolge",
        "",
        "1. Die 12 Dokumente in der Tabellenreihenfolge.",
        "2. Danach die 18 Ergänzungen; die fünf Negativkontrollen zuletzt.",
        "3. Keine Zwischenabgabe: Die Dateien bleiben bis zur Gesamtabgabe",
        "   offen; ein Zwischenvergleich würde die Blindheit brechen.",
        "",
        "## Dokumente",
        "",
        "| Dokument | Schicht | Design | Zeichen | Tabellen | Effektstellen | Punkt |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in eintraege:
        name = Path(e["datei"]).name
        zeilen.append(
            f"| [{e['document_id'][:10]}]({name}) | {e['stratum']} | "
            f"{e['design_category']} | {e['zeichen']:,} | {e['tabellen']} | "
            f"{e['effektstellen']} | {e['punkt']} |")
    gesamt_tab = sum(e["tabellen"] for e in eintraege)
    gesamt_eff = sum(e["effektstellen"] for e in eintraege)
    zeilen += [
        "",
        f"Summe: {len(eintraege)} Dokumente, {gesamt_tab} Tabellenstellen, "
        f"{gesamt_eff} Effektstellen.",
        "",
        "### Schichten",
        "",
        "| Schicht | Dokumente |",
        "|---|---|",
    ]
    schichten = OrderedDict()
    for e in eintraege:
        schichten[e["stratum"]] = schichten.get(e["stratum"], 0) + 1
    for name, n in schichten.items():
        zeilen.append(f"| {name} | {n} |")
    zeilen += [
        "",
        "## Prüfpunkte",
        "",
    ]
    punkte = []
    for e in eintraege:
        if e["punkt"] not in punkte:
            punkte.append(e["punkt"])
    for p in punkte:
        zeilen.append(f"- **{p}:** {ERKLAERUNG_KAL.get(p, '')}")
    zeilen += [
        "",
        "## Ablauf",
        "",
        "1. Arbeitsblatt und Volltext vollständig lesen.",
        "2. Jede Effektzeile mit Quote und Unsicherheit erfassen; Dokument",
        "   abschließen (Zeilen oder `no_effect_reason`).",
        "3. `.venv/bin/python.exe scripts/pruefe_goldstandard.py --entwurf "
        "data/golden_effects/goldstandard_A.json` (bzw. B) bis 0 Fehler.",
        "4. Nach den 12 weiter mit den 18 Ergänzungen; keine Zwischenabgabe.",
        "5. Nach allen 30: Abgabe, Hashes eintragen, Kappa mit",
        "   `werte_kappa_probe.py` (ohne `--probelauf`).",
        "",
        "## Stand (Start)",
        "",
        f"- A: {za} Zeilen, {ba} Begründungen, {oa} offen (von 12).",
        f"- B: {zb} Zeilen, {bb} Begründungen, {ob} offen (von 12).",
        f"- Hash A: `{_hash(A)}`",
        f"- Hash B: `{_hash(B)}`",
        "",
    ]
    text = "\n".join(zeilen).rstrip("\n") + "\n"
    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(text, encoding="utf-8")
    JSON_ZIEL.parent.mkdir(parents=True, exist_ok=True)
    JSON_ZIEL.write_text(json.dumps(
        {"dokumente": eintraege, "summe": {"dokumente": len(eintraege),
                                           "tabellen": gesamt_tab,
                                           "effektstellen": gesamt_eff}},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(text)
    print(f"Arbeitsblatt: {ZIEL.relative_to(ROOT)}")
    print(f"JSON: {JSON_ZIEL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

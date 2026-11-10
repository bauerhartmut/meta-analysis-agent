"""Erzeugt die Abgabe-Checkliste fuer die Vollannotation aller 30 Dokumente.

Read-only. Liest A und B, zaehlt Zeilen, Begruendungen und offene Dokumente,
berechnet die Hashes und schreibt eine Checkliste mit Dokumentliste,
Pruefpunkten, Reihenfolge und Abgabepfad. Die Checkliste ist fuer A und B
identisch, wird aber getrennt ausgefuellt.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "data" / "golden_effects" / "goldstandard_A.json"
B = ROOT / "data" / "golden_effects" / "goldstandard_B.json"
DOCS = ROOT / "data" / "golden_effects" / "documents.json"
ZIEL = ROOT / "docs" / "internal" / "vollannotation_abgabe_checkliste_20261110.md"

SONDERFALL = {
    "7111ea9787": "5.8",
    "bb9218735f": "5.7",
    "203c831dbe": "5.8 gepoolt",
    "3790c91f96": "5.11",
    "5cbf039f22": "Design",
}

ERKLAERUNG = {
    "5.8": "5.8: narrativer Ueberblick ohne eigenen gepoolten Schaetzer; keine Zeile, `no_effect_reason`.",
    "5.7": "5.7: p-Wert ohne Effektgroesse ist keine Zeile; Mittelwerte +/- SD pruefen.",
    "5.8 gepoolt": "5.8: nur der gepoolte HR- und MD-Schaetzer, je eine Zeile mit `is_primary: false`.",
    "5.11": "5.11: Spannweite ueber Zeitpunkte ist keine Zeile; je Zeitpunkt eine Tabellenzeile.",
    "Design": "Design pruefen: Schicht `aggregate`, `design_category: parallel_rct`; vor der Annotation klaeren.",
    "Negativkontrolle": "Negativkontrolle: keine Zeile, `no_effect_reason`; nur bei echtem quantifiziertem Effekt mit Unsicherheit eine Zeile.",
    "5.1": "5.1: Design am Volltext; nur Effekte mit Unsicherheit; Quote exakt.",
}


def _hash(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def _index(pfad: Path) -> dict:
    return {d["document_id"]: d for d in
            json.loads(pfad.read_text(encoding="utf-8"))["documents"]}


def _stand(pfad: Path) -> dict:
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    docs = daten["documents"]
    zeilen = sum(len(d.get("effects") or []) for d in docs)
    begr = sum(1 for d in docs if str(d.get("no_effect_reason") or "").strip())
    offen = sum(1 for d in docs
                if not (d.get("effects") or [])
                and not str(d.get("no_effect_reason") or "").strip())
    return {"zeilen": zeilen, "begruendungen": begr, "offen": offen,
            "dokumente": len(docs), "hash": _hash(pfad)}


def _status(doc: dict) -> str:
    if doc is None:
        return "fehlt"
    zeilen = len(doc.get("effects") or [])
    begr = str(doc.get("no_effect_reason") or "").strip()
    if zeilen:
        return f"{zeilen} Zeilen"
    if begr:
        return "Begruendung"
    return "offen"


def _punkt(meta: dict) -> str:
    kurz = meta["document_id"][:10]
    if kurz in SONDERFALL:
        return SONDERFALL[kurz]
    if meta.get("stratum") == "negative_control":
        return "Negativkontrolle"
    return "5.1"


def main() -> int:
    docs = json.loads(DOCS.read_text(encoding="utf-8"))["documents"]
    if len(docs) != 30:
        print(f"Erwartet 30 Dokumente, gefunden {len(docs)}.")
        return 1
    ia, ib = _index(A), _index(B)
    a, b = _stand(A), _stand(B)
    kalibrierung = sum(1 for d in docs if d.get("calibration"))

    zeilen = [
        "# Abgabe-Checkliste Vollannotation (2026-11-10)",
        "",
        "30 Dokumente, A und B getrennt. Während der Annotation kein",
        "Austausch; nur Volltext, Anleitung v1.1, Schema und das eigene",
        "Arbeitsblatt. Der Probelauf ist ein separater Format- und Ablauftest;",
        "diese Checkliste betrifft die Vollannotation.",
        "",
        "## Stand",
        "",
        "| Datei | Zeilen | Begründungen | offen | Dokumente | Hash |",
        "|---|---|---|---|---|---|",
        f"| `goldstandard_A.json` | {a['zeilen']} | {a['begruendungen']} | "
        f"{a['offen']} | {a['dokumente']} | `{a['hash']}` |",
        f"| `goldstandard_B.json` | {b['zeilen']} | {b['begruendungen']} | "
        f"{b['offen']} | {b['dokumente']} | `{b['hash']}` |",
        "",
        "Die Hashes sind Startwerte; nach dem Ausfüllen ändern sie sich. Die",
        "Abgabe-Hashes werden unten eingetragen.",
        "",
        "## Reihenfolge",
        "",
        f"1. Zuerst die {kalibrierung} Kalibrierungsdokumente (Spalte",
        "   `Kalibrierung: ja`); sie decken die Schichten ab und kalibrieren",
        "   die Anleitung.",
        f"2. Danach die {30 - kalibrierung} Ergänzungen.",
        "3. Die fünf Negativkontrollen zuletzt, aber vollständig begründen.",
        "",
        "## Dokumentliste",
        "",
        "| Dokument | Schicht | Design | Kalibrierung | A | B | Punkt |",
        "|---|---|---|---|---|---|---|",
    ]
    for meta in docs:
        did = meta["document_id"]
        kurz = did[:10]
        link = f"[{kurz}](vollannotation_arbeitsblatt_{kurz}.md)"
        zeilen.append(
            f"| {link} | {meta.get('stratum')} | {meta.get('design_category')} | "
            f"{'ja' if meta.get('calibration') else '—'} | "
            f"{_status(ia.get(did))} | {_status(ib.get(did))} | {_punkt(meta)} |")
    zeilen += [
        "",
        "## Besondere Prüfpunkte",
        "",
    ]
    for punkt in ("5.8", "5.7", "5.8 gepoolt", "5.11", "Design", "Negativkontrolle"):
        zeilen.append(f"- **{punkt}:** {ERKLAERUNG[punkt]}")
    zeilen += [
        "- **5.1:** Standardfall; Design am Volltext, nicht aus dem Titel.",
        "",
        "## Vor der Abgabe (je Annotator)",
        "",
        "- [ ] Alle 30 Dokumente bearbeitet; jedes hat Zeilen oder",
        "      `no_effect_reason`.",
        "- [ ] Alle 14 Pflichtfelder je Zeile und 9 Dokumentpflichtfelder sind",
        "      gesetzt.",
        "- [ ] Jede `quote` ist exakt; `quote_start`/`quote_end` passen.",
        "- [ ] Kein Effekt umgerechnet, keine Zahl gerundet.",
        "- [ ] Ratio-Werte positiv; Effekt liegt im KI.",
        "- [ ] `is_primary: false` nur bei gepoolten Schätzern.",
        "- [ ] `design_category` nach 5.1; 5.11 bei Spannweiten über Zeitpunkte.",
        "- [ ] 5.7 und 5.8 geprüft; Negativkontrollen begründet.",
        "",
        "## Abgabe",
        "",
        "1. `.venv/bin/python.exe scripts/pruefe_goldstandard.py --entwurf "
        "data/golden_effects/goldstandard_A.json data/golden_effects/goldstandard_B.json`",
        "   bis 0 Fehler.",
        "2. `.venv/bin/python.exe scripts/pruefe_goldstandard.py "
        "data/golden_effects/goldstandard_A.json data/golden_effects/goldstandard_B.json`",
        "   ohne `--entwurf`; Exit 0.",
        "3. Die ausgegebenen SHA-256 unten eintragen.",
        "4. Dateien committen und nicht mehr ändern; erst danach vergleichen.",
        "",
        "## Nach der Abgabe",
        "",
        "- `.venv/bin/python.exe scripts/werte_kappa_probe.py` (ohne",
        "  `--probelauf`).",
        "- `.venv/bin/python.exe scripts/berichte_kappa_konflikte.py "
        "--md docs/internal/kappa_konflikte_vollannotation_20261110.md "
        "--out data/golden_effects/kappa_konflikte_vollannotation.json`",
        "  (ohne `--probelauf`).",
        "- `.venv/bin/python.exe scripts/priorisiere_kappa_konflikte.py "
        "--quelle data/golden_effects/kappa_konflikte_vollannotation.json "
        "--md docs/internal/kappa_konflikte_priorisiert_vollannotation_20261110.md "
        "--out data/golden_effects/kappa_konflikte_priorisiert_vollannotation.json`",
        "- Konflikte für die dritte Stimme; Schwelle Zeilen-Kappa 0,80.",
        "",
        "## Abgabe-Hashes",
        "",
        "- A: ______________________________",
        "- B: ______________________________",
    ]
    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text("\n".join(zeilen).rstrip("\n") + "\n", encoding="utf-8")
    print("\n".join(zeilen))
    print(f"\nCheckliste: {ZIEL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

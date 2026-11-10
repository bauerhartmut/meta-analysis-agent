"""Priorisiert Kappa-Konflikte nach Schwere und schlaegt Entscheidungen vor.

Read-only, kein Modellaufruf. Quelle ist `data/golden_effects/kappa_konflikte.json`
aus `berichte_kappa_konflikte.py`. Die Reihenfolge folgt dem Schaden fuer den
Goldstandard:

1. Dokument ohne Zeile (`dokument`) - ein Annotator findet das Dokument leer,
2. fehlende Zeile (`nur_a`/`nur_b`) - Vollstaendigkeit,
3. Effekttyp (`typ`) - Poolingfaehigkeit,
4. Wert (`wert`) - Praezision,
5. KI (`ki`) - Unsicherheit.

Die Vorschlaege sind Pruefhinweise, keine Entscheidung. Die dritte Stimme
entscheidet am Volltext; die Spalte bleibt leer.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANG = {"dokument": 0, "nur_a": 1, "nur_b": 1, "typ": 2, "wert": 3, "ki": 4}
NAMEN = {0: "Dokument ohne Zeile", 1: "fehlende Zeile",
         2: "Effekttyp", 3: "Wert", 4: "KI"}


def _seite(c: dict) -> str:
    return f"{c.get('effect_type', '?')} {c.get('effect', '?')} (KI {c.get('ki', 'n/a')})"


def vorschlag(klasse: str, c: dict) -> str:
    if klasse == "dokument":
        return "Volltext pruefen: Effekte vorhanden? Sonst Begruendung uebernehmen"
    if klasse in ("nur_a", "nur_b"):
        if str(c.get("quote") or "").strip() and c.get("ki") not in (None, "", "n/a"):
            return "aufnehmen, Quote am Volltext verifizieren"
        return "pruefen: Beleg fehlt oder KI unklar"
    if klasse == "typ":
        return "Typ nach 5.2-5.5 am Volltext entscheiden"
    if klasse == "wert":
        return "Zeitpunkt/Adjustierung pruefen; sonst berichteten Wert uebernehmen"
    return "berichtetes KI uebernehmen, nicht umrechnen"


def priorisiere(klassen: dict) -> list:
    liste = []
    for klasse, eintraege in (klassen or {}).items():
        if klasse not in RANG:
            continue
        for c in eintraege or []:
            if klasse == "dokument":
                a = f"{c['effekte']} Zeilen" if c.get("seite") == "A" else "0 Zeilen"
                b = f"{c['effekte']} Zeilen" if c.get("seite") == "B" else "0 Zeilen"
            elif klasse in ("nur_a", "nur_b"):
                a, b = (_seite(c), "-") if klasse == "nur_a" else ("-", _seite(c))
            elif klasse == "ki":
                a = f"{c['a'][0]} bis {c['a'][1]}"
                b = f"{c['b'][0]} bis {c['b'][1]}"
            else:
                a, b = c.get("a"), c.get("b")
            liste.append({
                "rang": RANG[klasse], "klasse": klasse,
                "schwere": NAMEN[RANG[klasse]],
                "dokument": c.get("document_id", ""),
                "outcome": c.get("outcome", "-"),
                "a": a, "b": b,
                "vorschlag": vorschlag(klasse, c),
            })
    liste.sort(key=lambda x: (x["rang"], x["dokument"], x["outcome"], x["klasse"]))
    return liste


def markdown(liste: list, quelle: str) -> str:
    text = [
        "# Priorisierte Kappa-Konflikte fuer die dritte Stimme (2026-11-10)",
        "",
        f"Quelle: `{quelle}`. Reihenfolge: Dokument ohne Zeile vor fehlender",
        "Zeile vor Effekttyp vor Wert vor KI. Die Vorschlaege sind",
        "Pruefhinweise, keine Entscheidung.",
        "",
    ]
    if not liste:
        text += [
            "**Keine Konflikte, weil keine Annotation vorliegt.** A und B haben",
            "noch keine Effektzeilen abgegeben. Diese Datei ist kein Beleg fuer",
            "Uebereinstimmung und wird nach der Abgabe neu erzeugt.",
            "",
        ]
        return "\n".join(text)

    text += [
        f"**{len(liste)} Konflikte.** Zuerst die Dokumentebene, dann fehlende",
        "Zeilen, Typ, Wert und KI. Die Entscheidungsspalte fuellt die dritte",
        "Stimme.",
        "",
        "| Rang | Klasse | Schwere | Dokument | Outcome | A | B | Vorschlag | Entscheidung |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for x in liste:
        text.append(
            f"| {x['rang']} | {x['klasse']} | {x['schwere']} | {x['dokument'][:10]} | "
            f"{str(x['outcome'])[:70]} | {x['a']} | {x['b']} | {x['vorschlag']} |  |")
    text += ["", "Volle Eintraege: `data/golden_effects/kappa_konflikte_priorisiert.json`.", ""]
    return "\n".join(text)


def selbsttest() -> int:
    faelle = {
        "ki": [{"document_id": "d1", "outcome": "o", "a": [0.1, 0.2], "b": [0.1, 0.3]}],
        "wert": [{"document_id": "d1", "outcome": "o", "a": 1.0, "b": 1.2}],
        "typ": [{"document_id": "d1", "outcome": "o", "a": "hr", "b": "or"}],
        "nur_b": [{"document_id": "d1", "outcome": "o", "effect_type": "hr",
                   "effect": 1.0, "ki": "0.8 bis 1.2", "quote": "Risk 1.0"}],
        "dokument": [{"document_id": "d1", "seite": "A", "effekte": 2,
                      "begruendung": "keine relevanten Effekte"}],
    }
    liste = priorisiere(faelle)
    reihenfolge = [x["klasse"] for x in liste]
    if reihenfolge != ["dokument", "nur_b", "typ", "wert", "ki"]:
        print(f"Selbsttest fehlgeschlagen: Reihenfolge {reihenfolge}")
        return 1
    if not all(x["vorschlag"] for x in liste):
        print("Selbsttest fehlgeschlagen: leerer Vorschlag")
        return 1
    if liste[0]["a"] != "2 Zeilen" or liste[0]["b"] != "0 Zeilen":
        print(f"Selbsttest fehlgeschlagen: Dokumentseiten {liste[0]['a']} / {liste[0]['b']}")
        return 1
    if "aufnehmen" not in liste[1]["vorschlag"]:
        print(f"Selbsttest fehlgeschlagen: Vorschlag fehlende Zeile {liste[1]['vorschlag']}")
        return 1
    print("Selbsttest: Reihenfolge und Vorschlaege ok (5 konstruierte Faelle)")
    return 0


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--quelle", default="data/golden_effects/kappa_konflikte.json")
    p.add_argument("--md", default="docs/internal/kappa_konflikte_priorisiert_20261110.md")
    p.add_argument("--out", default="data/golden_effects/kappa_konflikte_priorisiert.json")
    p.add_argument("--selbsttest", action="store_true")
    args = p.parse_args(argv)

    if args.selbsttest:
        return selbsttest()

    quelle = ROOT / args.quelle
    if not quelle.exists():
        print(f"Quelle fehlt: {quelle}")
        return 1
    daten = json.loads(quelle.read_text(encoding="utf-8"))
    liste = priorisiere(daten.get("konflikte") or {})
    text = markdown(liste, args.quelle)
    print(text)
    ziel = ROOT / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps({"n_konflikte": len(liste), "konflikte": liste},
                               ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md = ROOT / args.md
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(text + "\n", encoding="utf-8")
    print(f"JSON: {ziel.relative_to(ROOT)}")
    print(f"Markdown: {md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""Triage-Bericht gegen die Erwartung aus der Schwellenrechnung pruefen.

Der Triage-Bericht (``scripts/triage_lieferung.py``) sagt, was gelesen wurde.
Dieses Skript sagt, ob das im Rahmen der Erwartung liegt:

  - Ist der Bericht in sich stimmig (k = Basis + poolbare Dateien)?
  - Wie hoch ist die Ausbeute gegen die beobachtete Quote p = 0,20 aus
    ``data/bench/sol2/schwelle_k5_20261108.md``?
  - Ist das Schritt-Ziel k >= 2 erreicht, wie weit ist das Gesamtziel k >= 5?
  - Was fehlt (nicht gelieferte Artikel, Scans, Ablehnungen)?

Kein Netz, kein Modell. Die Erwartung ist eine Annahme aus dem
Schwellendokument; sie wird hier zitiert, nicht neu geschaetzt.

Exit-Codes:
  0  Bericht stimmig, Befunde gemeldet
  1  Bericht in sich widerspruechlich (k passt nicht zu den Dateien)
  2  keine Lieferung / kein Triage-Bericht - nichts zu pruefen

Aufruf:
    .venv/bin/python.exe scripts/pruefe_lieferung.py \
        --bericht data/bench/sol2/lieferung.json \
        --md data/bench/sol2/lieferung_pruefung.md \
        --json data/bench/sol2/lieferung_pruefung.json

Die Datei ``lieferung.json`` stammt aus der Triage und darf nur dafuer
verwendet werden, wenn sie von einem echten Lauf stammt; ein Lauf auf
Pruef-PDFs ist eine Simulation und muss so gekennzeichnet bleiben.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ERWARTUNG_QUELLE = "data/bench/sol2/schwelle_k5_20261108.md"


def erwartung(n_gelesen: int, p: float) -> dict:
    """Erwartungswert und Wahrscheinlichkeit fuer null Treffer.

    Erwartungswert n * p ist eine Rechnung, keine Prognose; die
    Null-Wahrscheinlichkeit (1 - p) ** n sagt, wie ueblich eine Nullrunde bei
    dieser Quote waere.
    """
    n = max(0, int(n_gelesen))
    quote = min(1.0, max(0.0, float(p)))
    return {
        "n": n,
        "p": quote,
        "erwartet_poolbar": round(n * quote, 2),
        "p_null_poolbar": round((1.0 - quote) ** n, 3),
    }


def _zustand(doc: dict) -> str:
    if doc.get("zustand"):
        return str(doc["zustand"])
    if doc.get("error"):
        return "scan"
    return "poolbar" if int(doc.get("sol_poolable") or 0) > 0 else "unklar"


def pruefe(bericht: dict, p: float = 0.20, ziel: int = 2,
           gesamt_ziel: int = 5, artikel: int = 5) -> dict:
    """Kennzahlen und Befunde aus einem Triage-Bericht."""
    docs = list(bericht.get("documents") or [])
    k_block = dict(bericht.get("k") or {})
    zustaende = [_zustand(d) for d in docs]
    poolbar = sum(1 for z in zustaende if z == "poolbar")
    scan = sum(1 for z in zustaende if z == "scan")
    leser_luecke = sum(1 for z in zustaende if z == "leser_luecke")
    kandidaten = sum(1 for z in zustaende if z == "kandidaten_abgelehnt")
    nicht_berichtet = sum(1 for z in zustaende if z == "endpunkt_nicht_berichtet")
    gelesen = len(docs) - scan

    basis = int(k_block.get("basis_k") or 0)
    k_neu = int(k_block.get("k_neu") if k_block.get("k_neu") is not None else basis + poolbar)
    k_rechnet = basis + poolbar
    e = erwartung(gelesen, p)
    ausbeute = round(poolbar / gelesen, 2) if gelesen else None
    fehlend = [str(f.get("pmid") or "") for f in (bericht.get("fehlend") or [])]
    fremd = [str(f) for f in (bericht.get("fremd") or [])]

    befunde: list[dict] = []

    def melde(schwere: str, text: str) -> None:
        befunde.append({"schwere": schwere, "text": text})

    if not docs:
        melde("leer", f"Keine PDF gelesen (Verzeichnis: {bericht.get('directory', '?')}) - "
                      "nichts zu pruefen, k bleibt bei "
                      f"{k_neu}.")
    if k_neu != k_rechnet:
        melde("fehler", f"k im Bericht ist {k_neu}, aus den Dateien folgt aber "
                        f"{basis} + {poolbar} = {k_rechnet}.")
    if docs and k_neu < int(ziel):
        melde("abweichung", f"Schritt-Ziel k >= {ziel} verfehlt: k = {k_neu}, "
                            f"es fehlen {int(ziel) - k_neu}.")
    if docs and k_neu >= int(ziel):
        melde("ok", f"Schritt-Ziel k >= {ziel} erreicht mit k = {k_neu}.")
    if gelesen and poolbar < e["erwartet_poolbar"]:
        melde("abweichung", f"Ausbeute {poolbar} von {gelesen} gelesenen Dokumenten "
                            f"({ausbeute}) liegt unter der Annahme p = {p}; "
                            f"erwartet waren {e['erwartet_poolbar']}.")
    if gelesen and poolbar > e["erwartet_poolbar"]:
        melde("hinweis", f"Ausbeute {poolbar} von {gelesen} ({ausbeute}) liegt ueber "
                         f"der Annahme p = {p} (erwartet {e['erwartet_poolbar']}); "
                         "die Annahme im Schwellendokument fortschreiben, nicht "
                         "stillschweigend uebernehmen.")
    if scan:
        melde("hinweis", f"{scan} Datei(en) ohne Textebene - nachbestellen oder "
                         "abtippen, nicht als 'nicht berichtet' buchen.")
    if leser_luecke or kandidaten:
        melde("hinweis", f"{leser_luecke} Datei(en) mit erkannten, aber nicht "
                         f"gespeicherten SOL-Zeilen, {kandidaten} mit abgelehnten "
                         "Kandidaten - Ablehnungsgruende aufloesen, bevor p "
                         "fortgeschrieben wird.")
    if nicht_berichtet:
        melde("ok", f"{nicht_berichtet} Dokument(e) ohne berichteten Endpunkt - "
                    "ein Befund ueber die Studie, kein Kettenfehler.")
    if fehlend:
        melde("hinweis", "nicht geliefert: " + ", ".join(p for p in fehlend if p))
    if fremd:
        melde("hinweis", f"{len(fremd)} Datei(en) ohne Zuordnung zur Zugangsliste: "
                         + ", ".join(fremd[:5]))
    if docs and k_neu >= int(gesamt_ziel):
        melde("ok", f"Gesamtziel k >= {gesamt_ziel} erreicht.")
    elif docs:
        offen = int(gesamt_ziel) - k_neu
        weitere = int(-(-offen // p)) if p > 0 else 0
        melde("hinweis", f"Gesamtziel k >= {gesamt_ziel}: {offen} poolbare Studien "
                         f"fehlen; bei p = {p} waeren dafuer rechnerisch etwa "
                         f"{weitere} weitere Dokumente noetig (Erwartungswert, "
                         "keine Prognose).")

    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "bericht": bericht.get("directory"),
        "quelle_erwartung": ERWARTUNG_QUELLE,
        "annahme_p": p,
        "ziel": int(ziel),
        "gesamt_ziel": int(gesamt_ziel),
        "artikel": int(artikel),
        "kennzahlen": {
            "pdfs": bericht.get("pdfs"),
            "gelesen": gelesen,
            "poolbar": poolbar,
            "scan": scan,
            "ausbeute": ausbeute,
            "erwartet_poolbar": e["erwartet_poolbar"],
            "p_null_poolbar": e["p_null_poolbar"],
            "k_basis": basis,
            "k_neu": k_neu,
            "k_rechnet": k_rechnet,
            "konsistent": k_neu == k_rechnet,
            "fehlend": len(fehlend),
            "abdeckung": round((int(artikel) - len(fehlend)) / int(artikel), 2)
                         if artikel else None,
        },
        "befunde": befunde,
        "fehler": sum(1 for b in befunde if b["schwere"] == "fehler"),
        "abweichungen": sum(1 for b in befunde if b["schwere"] == "abweichung"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bericht", default="data/bench/sol2/lieferung.json")
    parser.add_argument("--md", default="data/bench/sol2/lieferung_pruefung.md")
    parser.add_argument("--json", default="data/bench/sol2/lieferung_pruefung.json")
    parser.add_argument("--p", type=float, default=0.20,
                        help="beobachtete Quote aus der Schwellenrechnung")
    parser.add_argument("--ziel", type=int, default=2)
    parser.add_argument("--gesamt-ziel", type=int, default=5)
    parser.add_argument("--artikel", type=int, default=5,
                        help="Zahl der bestellten Artikel in der A-Liste")
    args = parser.parse_args(argv)

    path = Path(args.bericht)
    if path.exists():
        bericht = json.loads(path.read_text(encoding="utf-8"))
    else:
        bericht = {"documents": [], "pdfs": 0, "k": {},
                   "directory": str(path.parent)}

    result = pruefe(bericht, p=args.p, ziel=args.ziel,
                    gesamt_ziel=args.gesamt_ziel, artikel=args.artikel)
    k = result["kennzahlen"]

    Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                               encoding="utf-8")

    lines = [
        "# Triage-Bericht gegen die Erwartung geprueft", "",
        f"Stand: {result['generated']}. Bericht: `{args.bericht}`. "
        "Kein Netz, kein Modell.", "",
        f"Erwartung aus `{ERWARTUNG_QUELLE}`: p = {args.p} poolbare Studien je "
        f"gelesenem Dokument; Schritt-Ziel k >= {args.ziel}, Gesamtziel "
        f"k >= {args.gesamt_ziel}. Die Quote ist eine Annahme, keine Messung.", "",
        "## Kennzahlen", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| PDFs im Bericht | {k['pdfs']} |",
        f"| gelesen (ohne Scans) | {k['gelesen']} |",
        f"| poolbar | {k['poolbar']} |",
        f"| Scans ohne Textebene | {k['scan']} |",
        f"| Ausbeute (poolbar / gelesen) | {k['ausbeute'] if k['ausbeute'] is not None else '-'} |",
        f"| Erwartungswert bei p = {args.p} | {k['erwartet_poolbar']} |",
        f"| P(null poolbare Studie) | {k['p_null_poolbar']} |",
        f"| k nach Bericht | {k['k_neu']} |",
        f"| k aus den Dateien nachgerechnet | {k['k_rechnet']} |",
        f"| nicht geliefert (A-Liste) | {k['fehlend']} von {args.artikel} |",
        "", "## Befunde", "",
        "| Schwere | Befund |", "|---|---|",
    ]
    for befund in result["befunde"]:
        lines.append(f"| {befund['schwere']} | {befund['text']} |")
    if not result["befunde"]:
        lines.append("| - | keine |")
    lines += [
        "", "## Was hier gerechnet und was angenommen ist", "",
        "- Gerechnet: k = Basis + poolbare Dateien, Ausbeute, Erwartungswert",
        "  n x p, Wahrscheinlichkeit einer Nullrunde (1 - p)^n, Abstand zum Ziel.",
        "- Angenommen: p selbst. Der Wert stammt aus der Schwellenrechnung",
        "  (1 von 5 Parallelstudien mit arm-level SOL) und ist dort als Annahme",
        "  markiert. Weicht die gemessene Ausbeute deutlich ab, gehoert die",
        "  Annahme fortgeschrieben - nicht dieses Skript.",
        "- Nicht geprueft: ob die Extraktion inhaltlich richtig ist. Dafuer",
        "  braucht es die Zitate in der DB je Zeile.",
        "",
    ]
    Path(args.md).write_text("\n".join(lines), encoding="utf-8")

    print(f"pdfs={k['pdfs']} gelesen={k['gelesen']} poolbar={k['poolbar']} "
          f"k={k['k_neu']} ziel={args.ziel} erreicht="
          f"{'ja' if k['k_neu'] >= args.ziel else 'nein'} "
          f"ausbeute={k['ausbeute']} erwartet={k['erwartet_poolbar']} "
          f"fehler={result['fehler']} abweichungen={result['abweichungen']}")
    for befund in result["befunde"]:
        print(f"  [{befund['schwere']}] {befund['text']}")

    if not k["pdfs"]:
        return 2
    if result["fehler"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

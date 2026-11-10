"""Erzeugt die Konfliktliste fuer die dritte Stimme aus A und B.

Read-only, kein Modellaufruf. Die Konflikte kommen aus derselben Logik wie
der Kappa-Lauf (`goldstandard_kappa.vergleiche`):

- `nur_a` / `nur_b`: Der Schluessel (Dokument, Outcome, Vergleich, Zeitpunkt)
  fehlt in der anderen Datei.
- `typ`: gleicher Schluessel, unterschiedlicher `effect_type`.
- `wert`: gleicher Typ, Effekt ausserhalb der Toleranz.
- `ki`: gleicher Wert, KI ausserhalb der Toleranz.

Die Markdown-Datei hat eine leere Spalte "Entscheidung" fuer die dritte
Stimme. Das JSON enthaelt die vollen Zeilen. Ohne Annotation ist der Bericht
leer und sagt das ausdruecklich; es werden keine Faelle erfunden.

Beispiel:
    .venv/bin/python.exe scripts/berichte_kappa_konflikte.py --probelauf \
        --md docs/internal/kappa_konflikte_20261110.md \
        --out data/golden_effects/kappa_konflikte.json
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.goldstandard_kappa import schluessel, vergleiche  # noqa: E402


def lade(pfad: Path) -> dict:
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    return {d["document_id"]: d.get("effects") or [] for d in daten["documents"]}


def index(docs: dict) -> dict:
    return {schluessel(doc, e): e
            for doc, effekte in docs.items() for e in effekte or []}


def _key_teile(key: tuple) -> dict:
    return {"document_id": key[0], "outcome": key[1],
            "comparison": key[2], "time_point": key[3]}


def _werte(effekt: dict) -> dict:
    ki = "n/a"
    if effekt.get("ci_low") is not None and effekt.get("ci_high") is not None:
        ki = f"{effekt['ci_low']} bis {effekt['ci_high']}"
    return {"effect_type": effekt.get("effect_type"),
            "effect": effekt.get("effect"), "ki": ki,
            "quote": " ".join(str(effekt.get("quote") or "").split())[:220]}


def _kurz(text, n=60) -> str:
    text = str(text or "")
    return text if len(text) <= n else text[: n - 1] + "…"


def markdown(ergebnis: dict, index_a: dict, index_b: dict,
             schwelle: float, probelauf: bool) -> str:
    def k(x):
        return "n/a" if x is None else f"{x:.3f}"

    def q(x):
        return "n/a" if x is None else f"{100 * x:.1f} %"

    n_konflikte = (len(ergebnis["nur_a"]) + len(ergebnis["nur_b"])
                   + len(ergebnis["typ_abweichung"])
                   + len(ergebnis["wert_abweichung"])
                   + len(ergebnis["ki_abweichung"]))
    text = [
        "# Kappa-Probelauf: Konflikte fuer die dritte Stimme (2026-11-10)",
        "",
        f"Grundlage: {'nur die drei Probelauf-Dokumente' if probelauf else 'alle Dokumente'}, "
        f"Toleranz 1 %. Schwelle Zeilen-Kappa: {schwelle:.2f}.",
        "",
        f"- Dokumente: {ergebnis['n_dokumente']}",
        f"- Schluessel: {ergebnis['n_keys']}",
        f"- Treffer: {ergebnis['treffer']} ({q(ergebnis['quote'])})",
        f"- Kappa Dokumentebene: {k(ergebnis['kappa_dokument'])}",
        f"- Kappa Zeilenebene: {k(ergebnis['kappa_zeile'])}",
        f"- Konflikte: {n_konflikte}",
        "",
    ]
    if ergebnis["n_keys"] == 0:
        text += [
            "**Keine Konflikte, weil keine Annotation vorliegt.** Beide Dateien",
            "enthalten keine Effektzeilen. Die Liste fuellt sich, sobald A und B",
            "abgegeben haben; sie ist kein Beleg fuer Uebereinstimmung.",
            "",
        ]
    text += [
        "Der Schluessel ist (Dokument, Outcome, Vergleich, Zeitpunkt). Zwei",
        "Zeilen mit demselben Schluessel, aber anderem Typ oder Wert sind ein",
        "Konflikt; zwei Zeilen mit verschiedenen Schluesseln sind `nur_a`/`nur_b`.",
        "",
        "## Entscheidungsregeln",
        "",
        "- `nur_a` / `nur_b`: Volltext pruefen. Belegt -> in den Konsens;",
        "  nicht belegt -> verwerfen und Grund notieren.",
        "- `typ`: Anleitung 5.2-5.5. `other` nur, wenn keine Kategorie passt.",
        "- `wert`: berichteten Wert uebernehmen; verschiedene Zeitpunkte oder",
        "  Adjustierungen sind getrennte Schluessel, keine Wertabweichung.",
        "- `ki`: berichtetes KI uebernehmen, nicht umrechnen.",
        "- Dokument ohne Zeile bei einem Annotator: pruefen, ob die Zeilen des",
        "  anderen belegt sind; wenn nicht, der Begruendung folgen.",
        "",
    ]

    def tabelle(titel, zeilen, kopf):
        text.extend([f"## {titel}", ""])
        if not zeilen:
            text.extend(["Keine.", ""])
            return
        text.append("| " + " | ".join(kopf) + " |")
        text.append("|" + "---|" * len(kopf))
        text.extend(zeilen)
        text.append("")

    def nur(key, effekt):
        w = _werte(effekt)
        return (f"| {key[0][:10]} | {_kurz(key[1], 70)} | {_kurz(key[2], 40)} | "
                f"{_kurz(key[3], 20)} | {w['effect_type']} | {w['effect']} | "
                f"{w['ki']} | {_kurz(w['quote'], 100)} |  |")

    tabelle("Nur A (in B nicht vorhanden)",
            [nur(k, index_a[k]) for k in ergebnis["nur_a"]],
            ["Dokument", "Outcome", "Vergleich", "Zeitpunkt", "Typ", "Effekt", "KI", "Quote (A)", "Entscheidung"])
    tabelle("Nur B (in A nicht vorhanden)",
            [nur(k, index_b[k]) for k in ergebnis["nur_b"]],
            ["Dokument", "Outcome", "Vergleich", "Zeitpunkt", "Typ", "Effekt", "KI", "Quote (B)", "Entscheidung"])

    typ_zeilen = []
    for x in ergebnis["typ_abweichung"]:
        key = x["key"]
        typ_zeilen.append(f"| {key[0][:10]} | {_kurz(key[1], 70)} | {_kurz(key[2], 40)} | "
                          f"{_kurz(key[3], 20)} | {x['a']} | {x['b']} |  |")
    tabelle("Typabweichung", typ_zeilen,
            ["Dokument", "Outcome", "Vergleich", "Zeitpunkt", "Typ A", "Typ B", "Entscheidung"])

    wert_zeilen = []
    for x in ergebnis["wert_abweichung"]:
        key = x["key"]
        wert_zeilen.append(f"| {key[0][:10]} | {_kurz(key[1], 70)} | {_kurz(key[2], 40)} | "
                           f"{_kurz(key[3], 20)} | {x['a']} | {x['b']} |  |")
    tabelle("Wertabweichung", wert_zeilen,
            ["Dokument", "Outcome", "Vergleich", "Zeitpunkt", "Wert A", "Wert B", "Entscheidung"])

    ki_zeilen = []
    for x in ergebnis["ki_abweichung"]:
        key = x["key"]
        ki_zeilen.append(f"| {key[0][:10]} | {_kurz(key[1], 70)} | {_kurz(key[2], 40)} | "
                         f"{_kurz(key[3], 20)} | {x['a'][0]} bis {x['a'][1]} | "
                         f"{x['b'][0]} bis {x['b'][1]} |  |")
    tabelle("KI-Abweichung", ki_zeilen,
            ["Dokument", "Outcome", "Vergleich", "Zeitpunkt", "KI A", "KI B", "Entscheidung"])

    text += [
        "Volle Zeilen und Schluessel: `data/golden_effects/kappa_konflikte.json`.",
        "",
    ]
    return "\n".join(text)


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", default="data/golden_effects/goldstandard_A.json")
    parser.add_argument("--b", default="data/golden_effects/goldstandard_B.json")
    parser.add_argument("--probelauf", action="store_true")
    parser.add_argument("--schwelle", type=float, default=0.80)
    parser.add_argument("--toleranz", type=float, default=0.01)
    parser.add_argument("--md", default="docs/internal/kappa_konflikte_20261110.md")
    parser.add_argument("--out", default="data/golden_effects/kappa_konflikte.json")
    args = parser.parse_args(argv)

    pa, pb = ROOT / args.a, ROOT / args.b
    for pfad in (pa, pb):
        if not pfad.exists():
            print(f"Datei fehlt: {pfad}")
            return 1
    da, db = lade(pa), lade(pb)
    if args.probelauf:
        ids = {d["document_id"] for d in
               json.loads(pa.read_text(encoding="utf-8"))["documents"]
               if d.get("probelauf")}
        da = {k: v for k, v in da.items() if k in ids}
        db = {k: v for k, v in db.items() if k in ids}

    ergebnis = vergleiche(da, db, toleranz=args.toleranz)
    ia, ib = index(da), index(db)
    ergebnis["konflikte"] = {
        "nur_a": [{**_key_teile(k), **_werte(ia[k])} for k in ergebnis["nur_a"]],
        "nur_b": [{**_key_teile(k), **_werte(ib[k])} for k in ergebnis["nur_b"]],
        "typ": [{**_key_teile(x["key"]), "a": x["a"], "b": x["b"]}
                for x in ergebnis["typ_abweichung"]],
        "wert": [{**_key_teile(x["key"]), "a": x["a"], "b": x["b"]}
                 for x in ergebnis["wert_abweichung"]],
        "ki": [{**_key_teile(x["key"]), "a": x["a"], "b": x["b"]}
               for x in ergebnis["ki_abweichung"]],
    }
    ergebnis["schwelle"] = args.schwelle
    ergebnis["probelauf"] = args.probelauf
    ergebnis["dateien"] = [str(pa.relative_to(ROOT)), str(pb.relative_to(ROOT))]

    text = markdown(ergebnis, ia, ib, args.schwelle, args.probelauf)
    print(text)
    ziel = ROOT / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1, default=list) + "\n",
                    encoding="utf-8")
    md = ROOT / args.md
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(text + "\n", encoding="utf-8")
    print(f"JSON: {ziel.relative_to(ROOT)}")
    print(f"Markdown: {md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

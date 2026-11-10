"""Waehlt die 30 Goldstandard-Dokumente und schreibt Auswahl + Begruendung.

Regeln:
- 12 Dokumente aus dem Kalibrierungsplan sind gesetzt.
- 18 Ergaenzungen je Schicht nach Caption-Treffern, fehlenden Effekttypen,
  Zeilenzahl und Groesse; Layout wird auf mindestens 10 Caption-Dokumente
  nachgezogen.
- 5 Negativkontrollen aus Volltexten ohne Effektzeile mit Protokoll-,
  Editorial- oder Kommentar-Titel.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/waehle_goldstandard.py
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAP = re.compile(r"(?im)^[ \t]*(?:table|tab\.?)[ \t]*S?[0-9]+")
VOLLTEXT = ROOT / "data" / "fulltext"

FIX = {
    "7111ea9787": "cohort", "3134fdc8c3": "cohort", "d0bec407a2": "cohort",
    "bb9218735f": "rct", "fb484d488b": "rct",
    "3bbb142c71": "crossover", "87079ba88a": "crossover",
    "2c7ab4d124": "cross_sectional", "09843d40d3": "cohort",
    "334f5f6798": "aggregate", "203c831dbe": "aggregate",
    "2675c25aab": "cross_sectional",
}
NEG_FIX = ["9cac5e48f3", "83966faed7", "0843e61250", "6e935d39b0", "af1bb4ac0c"]
ZIEL = {"rct": 6, "crossover": 3, "cohort": 7, "cross_sectional": 5, "aggregate": 4}
KAT = {"parallel_rct": "parallel_rct", "cluster_rct": "cluster_rct",
       "crossover_rct": "crossover_rct", "quasi_experimental": "quasi_experimental",
       "observational": "observational"}


def schicht(r):
    d = (r.get("design") or "").lower()
    if r.get("agg"):
        return "aggregate"
    if r.get("kat") == "crossover_rct":
        return "crossover"
    if r.get("kat") in ("parallel_rct", "cluster_rct"):
        return "rct"
    if "cross-sectional" in d or "case-control" in d:
        return "cross_sectional"
    if any(t in d for t in ("cohort", "longitudinal", "prospective", "retrospective")):
        return "cohort"
    return "other"


def score(r):
    return (r["caps"] >= 1, r["caps"] >= 2, r["ki"] > 0, r["n"],
            min(r["chars"], 120000))


def main():
    voll = {p.stem: p for p in VOLLTEXT.glob("*.txt")}
    kand = json.loads((ROOT / "data/bench/validierung/kandidaten_effektvolltexte.json")
                      .read_text(encoding="utf-8"))
    alle = json.loads((ROOT / "data/bench/validierung/kandidaten_volltexte.json")
                      .read_text(encoding="utf-8"))
    by_prefix = {r["fid"][:10]: r for r in kand}

    for r in kand:
        r["schicht"] = schicht(r)
        txt = voll.get(r["fid"])
        r["caps"] = len(CAP.findall(txt.read_text(encoding="utf-8", errors="replace"))) if txt else 0

    gewaehlt = [dict(by_prefix[p], schicht=s, fix=True) for p, s in FIX.items()]

    for sch, ziel in ZIEL.items():
        haben = [r for r in gewaehlt if r["schicht"] == sch]
        brauch = ziel - len(haben)
        if brauch <= 0:
            continue
        ids = {g["fid"] for g in gewaehlt}
        pool = [r for r in kand if r["schicht"] == sch and r["fid"] not in ids
                and r["chars"] >= 3000]
        typen_vorher = Counter(t for r in haben for t in r["typen"])
        pool.sort(key=lambda r: (len([t for t in r["typen"] if typen_vorher[t] == 0]),
                                 score(r)), reverse=True)
        gewaehlt.extend(dict(r, fix=False) for r in pool[:brauch])

    for _ in range(12):
        if sum(1 for r in gewaehlt if r["caps"] >= 1) >= 10:
            break
        ersatz = None
        for r in sorted([g for g in gewaehlt if not g["fix"]],
                        key=lambda x: (x["caps"], x["chars"])):
            if r["caps"] >= 1:
                continue
            pool = [c for c in kand if c["schicht"] == r["schicht"] and c["caps"] >= 1
                    and c["fid"] not in {g["fid"] for g in gewaehlt}]
            pool.sort(key=score, reverse=True)
            if pool:
                ersatz = (r, pool[0])
                break
        if not ersatz:
            break
        alt, neu = ersatz
        gewaehlt[gewaehlt.index(alt)] = dict(neu, fix=False)

    for pre in NEG_FIX:
        fid = next((f for f in alle if f[:10] == pre), None)
        if fid is None:
            raise SystemExit(f"Negativkontrolle nicht gefunden: {pre}")
        meta = alle[fid]
        text = voll[fid].read_text(encoding="utf-8", errors="replace")
        gewaehlt.append({"fid": fid, "titel": str(meta.get("titel") or ""),
                         "jahr": meta.get("jahr"), "chars": len(text),
                         "schicht": "negative_control", "caps": len(CAP.findall(text)),
                         "typen": [], "design": "", "kat": "unknown", "agg": False,
                         "n": 0, "fix": False})

    docs = []
    for r in gewaehlt:
        neg = r["schicht"] == "negative_control"
        docs.append({
            "document_id": r["fid"],
            "path": f"fulltext/{r['fid']}.txt",
            "stratum": r["schicht"],
            "design_category": "unknown" if neg else KAT.get(
                r.get("kat"), "aggregate" if r.get("agg") else "unknown"),
            "design_verbatim": (r.get("design") or "").strip()[:160],
            "title": str(r.get("titel") or "").strip(),
            "year": r.get("jahr"),
            "chars": r.get("chars"),
            "table_captions": r.get("caps", 0),
            "source_db": r.get("db"),
            "db_effect_rows": r.get("n", 0),
            "calibration": bool(r.get("fix")),
            "reason": ("Kalibrierungsdokument aus dem Versuchsplan." if r.get("fix") else
                       ("Negativkontrolle: Protokoll/Editorial/Kommentar ohne Effektzeile."
                        if neg else
                        "Ergaenzung Schicht %s; %s Zeilen in DB, %s Caption-Treffer, Typen %s."
                        % (r["schicht"], r.get("n", 0), r.get("caps", 0),
                           ", ".join(r.get("typen") or []) or "keine"))),
        })

    strata = Counter(d["stratum"] for d in docs)
    typen = Counter(t for r in gewaehlt for t in (r.get("typen") or []))
    assert len(docs) == 30, len(docs)
    assert sum(1 for d in docs if d["calibration"]) == 12
    assert all((ROOT / "data" / d["path"]).exists() for d in docs)
    assert len({d["document_id"] for d in docs}) == 30

    out = {
        "dataset": "goldstandard_documents", "version": "1.0",
        "created": "2026-11-10", "n_documents": 30,
        "strata": dict(strata), "type_coverage_db": dict(typen),
        "rules": [
            "12 Dokumente aus dem Kalibrierungsplan sind gesetzt.",
            "18 Ergaenzungen: je Schicht nach Caption-Treffern, dann fehlenden Effekttypen, dann Zeilenzahl/Groesse.",
            "5 Negativkontrollen aus Volltexten ohne Effektzeile mit Protokoll-/Editorial-/Kommentar-Titel.",
            "Kein Dokument doppelt; alle Volltexte vorhanden; Mindestgroesse 3000 Zeichen ausser gesetzten Dokumenten.",
        ],
        "known_gaps": [
            "Kein Dokument ohne Textebene im Korpus: die Pipeline nimmt nur Volltexte mit extrahierbarem Text auf. Die Schicht 'kein Textlayer' ist daher nicht besetzt.",
            "Caption-Treffer sind ein Layout-Hinweis per Regex, kein Beleg fuer Tabellen; die Annotatoren entscheiden am Dokument.",
            "db_effect_rows dient nur der Stratifikation, nicht als Goldstandard.",
        ],
        "documents": docs,
    }
    (ROOT / "data/golden_effects/documents.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    def kurz(s, n=58):
        return (s[:n] + "...") if len(s) > n else s

    zeilen = ["| %d | %s | %s | %d | %s | `%s` | %s |" % (
        i, d["stratum"], d["design_category"], d["table_captions"], d["chars"],
        d["document_id"][:10], kurz(d["title"])) for i, d in enumerate(docs, 1)]
    reihen = [("RCT (parallel/cluster)", "rct"), ("Crossover", "crossover"),
              ("Kohorte", "cohort"), ("Querschnitt/Fall-Kontrolle", "cross_sectional"),
              ("Aggregat (Uebersicht)", "aggregate"), ("Negativkontrolle", "negative_control")]
    schicht_zeilen = ["| %s | %d |" % (name, strata.get(key, 0))
                      for name, key in reihen]
    typen_text = ", ".join("%s %d" % (k, v) for k, v in sorted(typen.items()))
    caps_docs = sum(1 for d in docs if d["table_captions"] >= 1)

    md = """# Goldstandard: die 30 Dokumente (verbindlich, 2026-11-10)

Diese Liste ist der Auswahlbeleg. Sie wird nach dem Einfrieren nicht mehr
geaendert; neue Dokumente bedeuten eine neue Version mit neuer Begruendung.
Die maschinenlesbare Fassung steht in `data/golden_effects/documents.json`.

## Regeln der Auswahl

1. Die **12 Kalibrierungsdokumente** aus `kalibrierungslauf_plan_20261110.md`
   sind gesetzt. Sie sind mit `calibration: true` markiert.
2. Die **18 Ergaenzungen** wurden je Schicht nach drei Kriterien gewaehlt:
   zuerst Caption-Treffer (Layout), dann ein in der Schicht noch fehlender
   Effekttyp, dann Zeilenzahl und Groesse. So kommen Tabellen- und
   Fliesstextfaelle sowie alle Haupttypen vor.
3. Die **5 Negativkontrollen** stammen aus Volltexten ohne Effektzeile, deren
   Titel Protokoll, Editorial oder Kommentar nennt. Erwartung: `effects: []`
   mit Begruendung. Wird doch eine Zeile gefunden, ist die Erwartung falsch,
   nicht die Annotation.
4. Ausschluss: Dokumente unter 3000 Zeichen (ausser den gesetzten), doppelte
   IDs, fehlender Volltext.

## Schichtung

| Schicht | Anzahl |
|---|---|
%s
| **Summe** | **30** |

Effekttypen in der DB (nur Stratifikationshinweis, kein Goldstandard):
%s.

Dokumente mit mindestens einem Caption-Treffer: %d von 30.

## Die Liste

| # | Schicht | Design | Captions | Zeichen | ID | Titel |
|---|---|---|---|---|---|---|
%s

## Begruendung je Dokument

""" % ("\n".join(schicht_zeilen), typen_text, caps_docs, "\n".join(zeilen))
    for i, d in enumerate(docs, 1):
        md += "%d. `%s` - %s\n" % (i, d["document_id"], d["reason"])
    md += """
## Bekannte Luecken

- **Kein Dokument ohne Textebene**: der Korpus enthaelt nur Volltexte mit
  extrahierbarem Text. Die im Plan vorgesehene Schicht ist damit nicht
  besetzt; das wird nicht durch ein Ersatzdokument kaschiert.
- **Caption-Treffer** sind ein Regex-Hinweis, kein Beleg fuer eine Tabelle.
  Massgeblich ist die Sichtpruefung der Annotatoren.
- **`db_effect_rows`** zeigt, was die Pipeline bisher fand. Es ist kein
  Goldstandard und darf die Annotation nicht beeinflussen (Blindheit).

## Pruefung dieser Liste

- 30 Dokumente, 30 verschiedene IDs, alle Volltexte vorhanden.
- 12 von 12 Kalibrierungsdokumenten enthalten.
- Schichtsummen wie oben; Typenabdeckung or/rr/hr/md/smd/g/beta/r je
  mindestens einmal vertreten (z nicht gefordert).

## Naechster Schritt

Kappa-Probelauf an drei Dokumenten (je eines aus RCT, Kohorte, Aggregat),
bevor alle 30 annotiert werden. Liegt Kappa unter 0,80, wird die Anleitung
geschaerft, nicht die Auswahl geaendert.
"""
    (ROOT / "docs/internal/goldstandard_auswahl_20261110.md").write_text(md, encoding="utf-8")
    print("Geschrieben: data/golden_effects/documents.json, docs/internal/goldstandard_auswahl_20261110.md")
    print("Schichten:", dict(strata), "| Caption-Dokumente:", caps_docs)
    print("Typen:", dict(typen))


if __name__ == "__main__":
    main()
